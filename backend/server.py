from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import json
import time
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import schedule
from threading import Thread

# Solana imports
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
import base58


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Solana setup
solana_client = AsyncClient(os.environ.get('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'))

# Global variables for bot control
bot_running = False
bot_task = None

# Create the main app without a prefix
app = FastAPI(title="Solana Liquidity Management Bot")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class BotStatus(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_running: bool
    current_sol_balance: float = 0.0
    current_usdc_balance: float = 0.0
    active_positions: int = 0
    last_check: Optional[datetime] = None
    last_action: Optional[str] = None
    sol_price: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LiquidityPosition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position_id: str
    pool_id: str
    lower_price: float
    upper_price: float
    sol_amount: float
    usdc_amount: float
    liquidity_amount: float
    status: str = "active"  # active, closed, out_of_range
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

class BotLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    level: str  # INFO, WARNING, ERROR
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BotConfig(BaseModel):
    price_range_percent: float = 5.0
    check_interval_seconds: int = 300
    min_sol_amount: float = 0.01
    min_usdc_amount: float = 1.0

# Helper Functions
class SolanaWalletManager:
    def __init__(self):
        self.private_key = os.environ.get('WALLET_PRIVATE_KEY', '')
        if self.private_key and self.private_key != 'your_private_key_here':
            try:
                self.keypair = Keypair.from_base58_string(self.private_key)
                self.public_key = self.keypair.pubkey()
            except Exception as e:
                logger.error(f"Invalid private key: {e}")
                self.keypair = None
                self.public_key = None
        else:
            self.keypair = None
            self.public_key = None

    async def get_sol_balance(self) -> float:
        if not self.public_key:
            return 0.0
        try:
            response = await solana_client.get_balance(self.public_key)
            return response.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0

    async def get_usdc_balance(self) -> float:
        # USDC mint address on mainnet
        usdc_mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        if not self.public_key:
            return 0.0
        try:
            # This is simplified - in reality you'd need to get token account
            # For now return 0, will be implemented with proper SPL token handling
            return 0.0
        except Exception as e:
            logger.error(f"Error getting USDC balance: {e}")
            return 0.0

wallet_manager = SolanaWalletManager()

class PriceMonitor:
    def __init__(self):
        self.jupiter_api = os.environ.get('JUPITER_API_URL', 'https://price.jup.ag/v6')
        self.sol_mint = "So11111111111111111111111111111111111111112"
        
    async def get_sol_price(self) -> float:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.jupiter_api}/price?ids={self.sol_mint}")
                if response.status_code == 200:
                    data = response.json()
                    return float(data['data'][self.sol_mint]['price'])
                return 0.0
        except Exception as e:
            logger.error(f"Error fetching SOL price: {e}")
            return 0.0

price_monitor = PriceMonitor()

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.environ.get('DISCORD_WEBHOOK_URL', '')
        
    async def send_notification(self, message: str, level: str = "INFO"):
        if not self.webhook_url or self.webhook_url == 'your_discord_webhook_here':
            logger.info(f"Discord notification: {message}")
            return
            
        try:
            embed = {
                "title": "🤖 Liquidity Bot Notification",
                "description": message,
                "color": 0x00ff00 if level == "INFO" else 0xff9900 if level == "WARNING" else 0xff0000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "footer": {"text": "Solana Liquidity Management Bot"}
            }
            
            payload = {"embeds": [embed]}
            
            async with httpx.AsyncClient() as client:
                await client.post(self.webhook_url, json=payload)
                
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")

discord_notifier = DiscordNotifier()

class LiquidityManager:
    def __init__(self):
        self.pool_id = os.environ.get('SOL_USDC_POOL_ID', '8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj')
        self.price_range_percent = float(os.environ.get('PRICE_RANGE_PERCENT', '5.0'))
        
    async def get_current_positions(self) -> List[LiquidityPosition]:
        """Get active liquidity positions from database"""
        try:
            positions = await db.liquidity_positions.find({"status": "active"}).to_list(100)
            return [LiquidityPosition(**pos) for pos in positions]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def check_position_in_range(self, position: LiquidityPosition, current_price: float) -> bool:
        """Check if position is still in range"""
        return position.lower_price <= current_price <= position.upper_price
    
    async def create_position(self, sol_amount: float, usdc_amount: float, current_price: float) -> Optional[str]:
        """Create a new liquidity position - simplified simulation"""
        try:
            # Calculate price range (±2.5% for 5% total range)
            range_multiplier = self.price_range_percent / 100 / 2
            lower_price = current_price * (1 - range_multiplier)
            upper_price = current_price * (1 + range_multiplier)
            
            # Simulate position creation
            position = LiquidityPosition(
                position_id=f"pos_{int(time.time())}",
                pool_id=self.pool_id,
                lower_price=lower_price,
                upper_price=upper_price,
                sol_amount=sol_amount,
                usdc_amount=usdc_amount,
                liquidity_amount=sol_amount * current_price + usdc_amount,
                status="active"
            )
            
            await db.liquidity_positions.insert_one(position.dict())
            
            message = f"💰 New position created: {sol_amount:.4f} SOL + {usdc_amount:.2f} USDC at price ${current_price:.2f} (Range: ${lower_price:.2f} - ${upper_price:.2f})"
            await discord_notifier.send_notification(message)
            await self.log_action("INFO", message)
            
            return position.position_id
            
        except Exception as e:
            error_msg = f"Error creating position: {e}"
            logger.error(error_msg)
            await self.log_action("ERROR", error_msg)
            return None
    
    async def close_position(self, position: LiquidityPosition, reason: str) -> bool:
        """Close a liquidity position"""
        try:
            # Update position status in database
            await db.liquidity_positions.update_one(
                {"id": position.id},
                {"$set": {"status": "closed", "closed_at": datetime.now(timezone.utc)}}
            )
            
            message = f"🔄 Position closed: {position.position_id} - {reason}"
            await discord_notifier.send_notification(message, "WARNING")
            await self.log_action("INFO", message)
            
            return True
            
        except Exception as e:
            error_msg = f"Error closing position: {e}"
            logger.error(error_msg)
            await self.log_action("ERROR", error_msg)
            return False
    
    async def log_action(self, level: str, message: str, details: Optional[Dict] = None):
        """Log bot action to database"""
        try:
            log_entry = BotLog(level=level, message=message, details=details)
            await db.bot_logs.insert_one(log_entry.dict())
        except Exception as e:
            logger.error(f"Error logging action: {e}")

liquidity_manager = LiquidityManager()

# Bot Logic
async def bot_cycle():
    """Main bot logic - runs periodically"""
    try:
        # Get current price
        current_price = await price_monitor.get_sol_price()
        if current_price == 0:
            await liquidity_manager.log_action("ERROR", "Could not fetch SOL price")
            return
        
        # Get wallet balances
        sol_balance = await wallet_manager.get_sol_balance()
        usdc_balance = await wallet_manager.get_usdc_balance()
        
        # Get current positions
        positions = await liquidity_manager.get_current_positions()
        
        # Check existing positions
        out_of_range_positions = []
        for position in positions:
            if not await liquidity_manager.check_position_in_range(position, current_price):
                out_of_range_positions.append(position)
        
        # Close out-of-range positions
        for position in out_of_range_positions:
            await liquidity_manager.close_position(position, f"Price ${current_price:.2f} out of range ${position.lower_price:.2f}-${position.upper_price:.2f}")
        
        # Create new position if we have enough balance and no active positions
        active_positions = len(positions) - len(out_of_range_positions)
        min_sol = float(os.environ.get('MIN_SOL_AMOUNT', '0.01'))
        min_usdc = float(os.environ.get('MIN_USDC_AMOUNT', '1.0'))
        
        if active_positions == 0 and sol_balance >= min_sol and usdc_balance >= min_usdc:
            # Use 80% of available balance for new position
            sol_to_use = sol_balance * 0.8
            usdc_to_use = usdc_balance * 0.8
            await liquidity_manager.create_position(sol_to_use, usdc_to_use, current_price)
        
        # Update bot status
        status = BotStatus(
            is_running=True,
            current_sol_balance=sol_balance,
            current_usdc_balance=usdc_balance,
            active_positions=active_positions,
            last_check=datetime.now(timezone.utc),
            last_action=f"Checked at ${current_price:.2f}",
            sol_price=current_price
        )
        
        await db.bot_status.replace_one({}, status.dict(), upsert=True)
        
        logger.info(f"Bot cycle completed - Price: ${current_price:.2f}, SOL: {sol_balance:.4f}, Active positions: {active_positions}")
        
    except Exception as e:
        error_msg = f"Error in bot cycle: {e}"
        logger.error(error_msg)
        await liquidity_manager.log_action("ERROR", error_msg)

async def run_bot():
    """Background task that runs the bot"""
    global bot_running
    check_interval = int(os.environ.get('CHECK_INTERVAL_SECONDS', '300'))
    
    while bot_running:
        await bot_cycle()
        await asyncio.sleep(check_interval)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Solana Liquidity Management Bot API", "status": "running"}

@api_router.get("/status", response_model=BotStatus)
async def get_bot_status():
    try:
        status_doc = await db.bot_status.find_one({})
        if status_doc:
            return BotStatus(**status_doc)
        else:
            return BotStatus(is_running=bot_running)
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(status_code=500, detail="Error getting bot status")

@api_router.post("/start")
async def start_bot(background_tasks: BackgroundTasks):
    global bot_running, bot_task
    
    if bot_running:
        return {"message": "Bot is already running"}
    
    # Check if wallet is configured
    if not wallet_manager.keypair:
        raise HTTPException(status_code=400, detail="Wallet private key not configured")
    
    bot_running = True
    bot_task = asyncio.create_task(run_bot())
    
    await discord_notifier.send_notification("🚀 Liquidity bot started!")
    await liquidity_manager.log_action("INFO", "Bot started")
    
    return {"message": "Bot started successfully"}

@api_router.post("/stop")
async def stop_bot():
    global bot_running, bot_task
    
    if not bot_running:
        return {"message": "Bot is not running"}
    
    bot_running = False
    if bot_task:
        bot_task.cancel()
    
    await discord_notifier.send_notification("⏹️ Liquidity bot stopped")
    await liquidity_manager.log_action("INFO", "Bot stopped")
    
    return {"message": "Bot stopped successfully"}

@api_router.get("/positions", response_model=List[LiquidityPosition])
async def get_positions(status: Optional[str] = None):
    try:
        query = {}
        if status:
            query["status"] = status
        
        positions = await db.liquidity_positions.find(query).sort("created_at", -1).to_list(100)
        return [LiquidityPosition(**pos) for pos in positions]
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail="Error getting positions")

@api_router.get("/logs", response_model=List[BotLog])
async def get_logs(level: Optional[str] = None, limit: int = 100):
    try:
        query = {}
        if level:
            query["level"] = level
        
        logs = await db.bot_logs.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
        return [BotLog(**log) for log in logs]
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail="Error getting logs")

@api_router.get("/price")
async def get_current_price():
    try:
        price = await price_monitor.get_sol_price()
        return {"sol_price": price, "timestamp": datetime.now(timezone.utc)}
    except Exception as e:
        logger.error(f"Error getting price: {e}")
        raise HTTPException(status_code=500, detail="Error getting price")

@api_router.get("/wallet")
async def get_wallet_info():
    try:
        sol_balance = await wallet_manager.get_sol_balance()
        usdc_balance = await wallet_manager.get_usdc_balance()
        
        return {
            "public_key": str(wallet_manager.public_key) if wallet_manager.public_key else None,
            "sol_balance": sol_balance,
            "usdc_balance": usdc_balance,
            "configured": wallet_manager.keypair is not None
        }
    except Exception as e:
        logger.error(f"Error getting wallet info: {e}")
        raise HTTPException(status_code=500, detail="Error getting wallet info")

@api_router.post("/test-notification")
async def test_discord_notification():
    try:
        await discord_notifier.send_notification("🧪 Test notification from Liquidity Bot!")
        return {"message": "Test notification sent"}
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail="Error sending test notification")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    global bot_running, bot_task
    bot_running = False
    if bot_task:
        bot_task.cancel()
    client.close()
    await solana_client.close()
