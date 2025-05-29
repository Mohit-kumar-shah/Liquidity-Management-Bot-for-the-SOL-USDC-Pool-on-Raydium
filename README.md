# Liquidity Management Bot for the SOL-USDC Pool on Raydium

## Overview

The Liquidity Management Bot is an automated solution designed to optimize liquidity provision for the SOL-USDC pool on Raydium, a leading decentralized exchange on the Solana blockchain. This bot continuously monitors your liquidity positions, automatically withdraws funds from out-of-range positions, and reinvests them into new positions within a configurable price range (default: 5%) to maximize returns and maintain optimal capital efficiency.

By automating the complex process of liquidity management, this bot helps users maintain active positions in concentrated liquidity pools without constant manual intervention, ensuring their capital remains productive even during volatile market conditions.

## Features

- **Automated Liquidity Provision**: Automatically provides liquidity to the SOL-USDC pool within a specified price range
- **Continuous Position Monitoring**: Real-time tracking of liquidity positions and market conditions
- **Smart Rebalancing**: Automatically withdraws funds from out-of-range positions and reinvests them in new, active positions
- **Configurable Price Range**: Customizable price range management (default: ±5% from current price)
- **Secure Wallet Integration**: Seamless integration with Solana wallets for secure transaction execution
- **Customizable Parameters**: Adjustable settings for price range, slippage tolerance, and monitoring intervals
- **Robust Error Handling**: Comprehensive error management for network issues, transaction failures, and edge cases
- **Real-time Logging**: Detailed logging of all bot activities, transactions, and position changes
- **Gas Fee Optimization**: Intelligent transaction batching to minimize Solana network fees
- **Position Analytics**: Track performance metrics and returns on liquidity positions

## Prerequisites

Before using the Liquidity Management Bot, ensure you have the following:

- **Solana Wallet**: A compatible wallet (Phantom, Solflare, or similar) with sufficient funds
- **Token Holdings**: Both SOL and USDC tokens in your wallet for liquidity provision
- **Node.js**: Version 14.x or higher installed on your system
- **Raydium SDK**: Will be installed automatically via npm
- **Solana CLI** (Optional): For manual blockchain interactions and verification
- **Sufficient SOL**: Adequate SOL balance for transaction fees (recommended: 0.1+ SOL)
- **USDC Balance**: USDC tokens for liquidity provision (minimum recommended: $100 equivalent)
- **Stable Internet**: A Reliable internet connection for continuous operation
- **System Resources**: Adequate CPU and memory for continuous monitoring

## Installation

Follow these steps to install and set up the Liquidity Management Bot:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/liquidity-management-bot.git
cd liquidity-management-bot
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the project root and configure the following variables:

```bash
cp .env.example .env
nano .env
```

Add the following configuration:

```env
# Wallet Configuration
WALLET_PRIVATE_KEY=your_wallet_private_key_here

# Solana Network Configuration
RPC_ENDPOINT=https://api.mainnet-beta.solana.com

# Bot Configuration
PRICE_RANGE_PERCENT=5
SLIPPAGE_TOLERANCE=0.5
CHECK_INTERVAL=60

# Pool Configuration
POOL_ADDRESS=auto_detect
MIN_LIQUIDITY_AMOUNT=10

# Logging Configuration
LOG_LEVEL=info
LOG_TO_FILE=true
```

### 4. Fund Your Wallet

Ensure your Solana wallet contains:
- **SOL**: For transaction fees (minimum 0.1 SOL recommended)
- **USDC**: For liquidity provision (amount depends on your strategy)

### 5. Verify Installation

Test the configuration:

```bash
npm run test-config
```

## Usage

### Starting the Bot

To start the Liquidity Management Bot, run:

```bash
node index.js
```

Or use the npm script:

```bash
npm start
```

### Bot Operation Flow

When starts, the bot performs the following operations:

1. **Connection**: Connects to the Solana network using the configured RPC endpoint
2. **Wallet Verification**: Verifies wallet access and checks token balances
3. **Pool Discovery**: Locates and connects to the SOL-USDC pool on Raydium
4. **Position Analysis**: Analyzes existing liquidity positions
5. **Continuous Monitoring**: Monitors positions every 60 seconds (configurable)
6. **Automatic Rebalancing**: Withdraws out-of-range positions and creates new ones
7. **Logging**: Provides real-time updates on all activities

### Stopping the Bot

To safely stop the bot:

- Press `Ctrl+C` in the terminal
- The bot will complete any pending transactions before shutting down
- All positions will remain active until manually managed

### Monitoring Bot Activity

The bot provides comprehensive logging:

```bash
# View real-time logs
tail -f logs/bot.log

# View error logs
tail -f logs/error.log
```

## Configuration

### Environment Variables

Customize the bot's behavior by modifying the `.env` file:

#### Core Settings

- **`WALLET_PRIVATE_KEY`**: Your Solana wallet's private key (keep secure!)
- **`RPC_ENDPOINT`**: Solana RPC endpoint (default: mainnet-beta)

#### Bot Parameters

- **`PRICE_RANGE_PERCENT`**: Price range for liquidity positions
  - Example: `3` for ±3% range, `5` for ±5% range
  - Default: `5`

- **`SLIPPAGE_TOLERANCE`**: Maximum acceptable slippage percentage
  - Example: `0.3` for 0.3% max slippage
  - Default: `0.5`

- **`CHECK_INTERVAL`**: Position monitoring interval in seconds
  - Example: `30` for 30-second checks, `120` for 2-minute checks
  - Default: `60`

#### Advanced Settings

- **`MIN_LIQUIDITY_AMOUNT`**: Minimum USDC amount for new positions
  - Default: `10`

- **`MAX_RETRIES`**: Maximum transaction retry attempts
  - Default: `3`

- **`GAS_PRICE_MULTIPLIER`**: Gas price adjustment factor
  - Default: `1.1` (10% above base price)

### Example Configurations

#### Conservative Setup (Lower Risk)
```env
PRICE_RANGE_PERCENT=3
SLIPPAGE_TOLERANCE=0.3
CHECK_INTERVAL=120
MIN_LIQUIDITY_AMOUNT=50
```

#### Aggressive Setup (Higher Frequency)
```env
PRICE_RANGE_PERCENT=7
SLIPPAGE_TOLERANCE=0.8
CHECK_INTERVAL=30
MIN_LIQUIDITY_AMOUNT=5
```

## Troubleshooting

### Common Issues and Solutions

#### Transaction Failures

**Issue**: Transactions fail with an insufficient funds error
**Solution**: 
- Ensure adequate SOL balance for gas fees (minimum 0.05 SOL)
- Verify USDC balance is sufficient for liquidity provision
- Check if wallet has been drained by failed transactions

#### Network Connectivity Issues

**Issue**: The Bot cannot connect to the Solana network
**Solution**:
- Verify `RPC_ENDPOINT` is correct and accessible
- Check Solana network status at [status.solana.com](https://status.solana.com)
- Try alternative RPC endpoints:
  ```env
  RPC_ENDPOINT=https://solana-api.projectserum.com
  RPC_ENDPOINT=https://api.mainnet-beta.solana.com
  ```

#### Missing or Invalid Positions

**Issue**: Bot reports no positions or invalid position data
**Solution**:
- Verify the SOL-USDC pool exists and is active on Raydium
- Check if your wallet has any existing positions
- Ensure the pool address is correctly configured

#### High Gas Fees

**Issue**: Transaction costs are unexpectedly high
**Solution**:
- Monitor Solana network activity and wait for lower congestion
- Adjust `GAS_PRICE_MULTIPLIER` in configuration
- Consider using a different RPC endpoint with better fee estimation

#### Bot Crashes or Stops

**Issue**: The Bot unexpectedly stops running
**Solution**:
- Check logs for error messages: `cat logs/error.log`
- Verify system resources (CPU, memory)
- Ensure a stable internet connection
- Restart with: `npm start`

### Debug Mode

Enable detailed debugging:

```bash
DEBUG=true LOG_LEVEL=debug node index.js
```

### Getting Help

If issues persist:

1. Check the [Issues](https://github.com/your-username/liquidity-management-bot/issues) page
2. Review logs for specific error messages
3. Verify all prerequisites are met
4. Test with minimal configuration first

## Security Considerations

### Private Key Security

- **Never share your private key** with anyone
- Store the `.env` file securely and never commit it to version control
- Consider using environment variables instead of file storage for production
- Regularly rotate wallet keys if possible
- Use a dedicated wallet for bot operations, separate from your main holdings

### Operational Security

- **Monitor SOL balance** regularly to ensure sufficient funds for gas fees
- Set up alerts for low balance conditions
- Keep private keys in encrypted storage when not in use
- Use hardware wallets for large amounts when possible

### DeFi Risks

- **Smart Contract Risk**: Raydium's smart contracts, while audited, may contain bugs
- **Impermanent Loss**: Liquidity provision can result in impermanent loss during volatile periods
- **Market Risk**: Cryptocurrency markets are highly volatile and unpredictable
- **Slippage Risk**: Large trades may experience significant slippage
- **Liquidity Risk**: Pools may become illiquid during extreme market conditions

### Monitoring and Alerts

- Set up monitoring for unusual bot behavior
- Monitor transaction history regularly
- Keep track of position performance and returns
- Consider setting up automated alerts for significant events

## Contributing

We welcome contributions to improve the Liquidity Management Bot! Here's how you can contribute:

### Development Setup

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/liquidity-management-bot.git
   cd liquidity-management-bot
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install Development Dependencies**
   ```bash
   npm install --dev
   ```

4. **Make Your Changes**
   - Follow the existing code style and conventions
   - Add tests for new functionality
   - Update documentation as needed

5. **Test Your Changes**
   ```bash
   npm test
   npm run lint
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: your descriptive commit message"
   ```

7. **Submit a Pull Request**
   - Push your branch to your fork
   - Create a pull request with a clear description
   - Include any relevant issue numbers

### Contribution Guidelines

- Write clear, concise commit messages
- Follow existing code formatting and style
- Include tests for new features
- Update documentation for any API changes
- Ensure all tests pass before submitting


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.

```
MIT License

Copyright (c) 2024 Liquidity Management Bot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
In the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## Disclaimer

**Important Notice**: This software is provided "as-is" without any warranties, express or implied. Using this bot involves significant financial risks.
