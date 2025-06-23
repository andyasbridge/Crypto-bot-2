import ccxt
import time
import ta
import pandas as pd
import logging

# --- CONFIGURATION ---
api_key = 'ZFi287lvQscv7wLNwegYI9GMncdzDLGsykuhWajRHFZmu9NTJ4gLCxfPJqvHUjvt'
api_secret = 'M7RX62VQGmqiAETGXWfQLqLKbPXFv9ZE1BZnhFdFHBrj0T4phlz03R4Vlwkhajmn'
max_drawdown_pct = 2  # % of balance per trade
timeframe = '1h'
sl_pct = 3  # Stop-loss %
tp_pct = 5  # Take-profit %

# Logging
logging.basicConfig(filename='trade_log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

# Init exchange
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# Load markets
markets = exchange.load_markets()
symbols = [s for s in markets if '/USDT' in s and markets[s]['active'] and markets[s].get('contract')]

def fetch_indicators(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        return df
    except Exception as e:
        print(f"Error fetching indicators for {symbol}: {e}")
        return None

def determine_signal(df):
    if df is None or len(df) < 2:
        return None
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    if latest['rsi'] > 80 and prev['rsi'] <= 80:
        return 'SHORT'
    elif latest['rsi'] < 30 and prev['rsi'] >= 30:
        return 'LONG'
    if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
        return 'LONG'
    elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
        return 'SHORT'
    return None

def execute_trade(symbol, side):
    try:
        balance = exchange.fetch_balance({'type': 'future'})
        usdt_balance = balance['total']['USDT']
        risk_amount = usdt_balance * (max_drawdown_pct / 100)
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        quantity = round(risk_amount / price, 3)
        if side == 'LONG':
            exchange.create_market_buy_order(symbol, quantity)
            sl = round(price * (1 - sl_pct / 100), 2)
            tp = round(price * (1 + tp_pct / 100), 2)
        elif side == 'SHORT':
            exchange.create_market_sell_order(symbol, quantity)
            sl = round(price * (1 + sl_pct / 100), 2)
            tp = round(price * (1 - tp_pct / 100), 2)
        msg = f"{side} {symbol} at {price:.2f}, SL: {sl}, TP: {tp}"
        print(msg)
        logging.info(msg)
    except Exception as e:
        print(f"Trade error on {symbol}: {e}")
        logging.error(f"Trade error on {symbol}: {e}")

# --- MAIN LOOP ---
if __name__ == '__main__':
    while True:
        print("Scanning market...")
        for symbol in symbols:
            df = fetch_indicators(symbol)
            signal = determine_signal(df)
            if signal:
                print(f"Signal for {symbol}: {signal}")
                execute_trade(symbol, signal)
        print("Sleeping 15 minutes...")
        time.sleep(900)
