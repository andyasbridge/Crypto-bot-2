# Crypto Trading Bot

An automated Binance Futures trading bot with RSI + MACD strategy, stop loss, take profit, Telegram alerts, and logging.

## Features
- Trades all USDT pairs on Binance Futures
- Uses RSI and MACD indicators
- Position sizing based on account balance
- Stop-loss and take-profit support
- Sends alerts via Telegram
- Logs trades to a file

## Setup
1. Replace `api_key` and `api_secret` in `main.py`.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the bot: `python main.py`

## Configuration
- Max Drawdown: 2%
- Timeframe: 1h
- SL/TP: Editable in code

## Notes
- This bot uses `ccxt`, `ta`, and `pandas`
- Requires a Binance Futures account and API key
