# Solana Liquidity Management Bot - Setup Guide

## Overview
This bot automatically manages liquidity positions in SOL-USDC Concentrated Liquidity Market Maker (CLMM) pools on Raydium. It monitors positions within a 5% price range and automatically rebalances when positions go out of range.

## Features
- ✅ Automated liquidity position management
- ✅ Real-time SOL price monitoring
- ✅ 5% price range management (+/- 2.5%)
- ✅ Automatic rebalancing when out of range
- ✅ Discord notifications for all operations
- ✅ Web dashboard for monitoring
- ✅ Comprehensive logging and error handling
- ✅ Wallet balance tracking

## Prerequisites
- DigitalOcean server (or any Linux server)
- Solana wallet with SOL and USDC funds
- Discord webhook URL for notifications
- Basic command line knowledge

## Installation Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker

# Clone the bot repository
git clone <your-repository-url>
cd solana-liquidity-bot
```

### 2. Configuration
Edit the `.env` file in the backend directory:

```bash
nano /app/backend/.env
```

Update the following values:

```env
# Solana Configuration
SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"
WALLET_PRIVATE_KEY="your_wallet_private_key_here"

# Pool Configuration
SOL_USDC_POOL_ID="8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj"
PRICE_RANGE_PERCENT=5.0
CHECK_INTERVAL_SECONDS=300
MIN_SOL_AMOUNT=0.01
MIN_USDC_AMOUNT=1.0

# Discord Configuration
DISCORD_WEBHOOK_URL="your_discord_webhook_url_here"
```

### 3. Required Credentials

#### Solana Wallet Private Key
1. Export your wallet private key from Phantom/Solflare
2. Ensure the wallet has SOL for transaction fees and USDC for liquidity
3. **SECURITY WARNING**: Never share your private key and keep it secure

#### Discord Webhook URL
1. Go to your Discord server
2. Server Settings → Integrations → Webhooks
3. Create New Webhook
4. Copy the Webhook URL
5. Test the webhook in the bot dashboard

#### Solana RPC URL (Optional)
- Default: Uses public Solana RPC
- Recommended: Get a dedicated RPC from:
  - Helius (https://helius.xyz/)
  - QuickNode (https://quicknode.com/)
  - Alchemy (https://alchemy.com/)

### 4. Starting the Bot

```bash
# Start all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.out.log
```

### 5. Access the Dashboard
- Open your browser and go to: `http://your-server-ip:3000`
- You should see the Solana Liquidity Management Bot dashboard

## Usage

### Web Dashboard
1. **Bot Status**: Shows if the bot is running/stopped
2. **SOL Price**: Current SOL price in USD
3. **Wallet**: SOL and USDC balances
4. **Positions**: Active liquidity positions
5. **Activity Logs**: Recent bot actions

### Bot Operations
1. **Start Bot**: Click "Start" to begin automated liquidity management
2. **Stop Bot**: Click "Stop" to halt all operations
3. **Test Discord**: Verify Discord notifications are working

### Discord Notifications
The bot will send notifications for:
- ✅ Bot started/stopped
- 💰 New liquidity positions created
- 🔄 Positions closed (out of range)
- ⚠️ Errors and warnings

## Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PRICE_RANGE_PERCENT` | Total price range (±2.5% each side) | 5.0 |
| `CHECK_INTERVAL_SECONDS` | How often to check positions | 300 (5 min) |
| `MIN_SOL_AMOUNT` | Minimum SOL for new positions | 0.01 |
| `MIN_USDC_AMOUNT` | Minimum USDC for new positions | 1.0 |

## Bot Logic

### Position Management
1. **Monitor**: Check position status every 5 minutes
2. **Detect**: Identify out-of-range positions
3. **Close**: Withdraw liquidity from out-of-range positions  
4. **Rebalance**: Create new position within 5% range
5. **Notify**: Send Discord notification for all actions

### Safety Features
- Minimum balance requirements
- Error handling and logging
- Position status tracking
- Automatic retry logic

## Troubleshooting

### Common Issues

#### Bot Won't Start
- Check if wallet private key is configured
- Verify wallet has sufficient SOL balance
- Check supervisor logs: `tail -f /var/log/supervisor/backend.err.log`

#### No Discord Notifications
- Verify webhook URL is correct
- Test webhook manually using "Test Discord" button
- Check Discord server permissions

#### Price Not Updating
- Check internet connection
- Verify API endpoints are accessible
- Bot uses CoinGecko API with fallback

### Log Files
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs  
tail -f /var/log/supervisor/frontend.out.log

# All services
sudo supervisorctl tail -f backend
```

### Restart Services
```bash
# Restart individual services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Restart all services
sudo supervisorctl restart all
```

## Security Best Practices

1. **Private Key Security**
   - Never commit private keys to version control
   - Use environment variables only
   - Consider using hardware wallets for large amounts

2. **Server Security**
   - Enable firewall (UFW)
   - Use SSH keys instead of passwords
   - Keep system updated
   - Monitor for unusual activity

3. **Discord Security**
   - Limit webhook permissions
   - Use dedicated channel for bot notifications
   - Monitor for unauthorized webhook usage

## Monitoring and Maintenance

### Daily Checks
- Verify bot is running
- Check wallet balances
- Review Discord notifications
- Monitor position performance

### Weekly Maintenance
- Check log files for errors
- Verify system resources
- Update dependencies if needed
- Backup configuration files

## Support

For technical support or questions:
- Twitter: @GoldenFishDAO
- Telegram: @christoshi

## Legal Disclaimer

This software is provided "as is" without warranty. Use at your own risk. 
Cryptocurrency trading involves substantial risk of loss. Past performance 
does not guarantee future results.

---

**Last Updated**: March 2025
**Version**: 1.0.0