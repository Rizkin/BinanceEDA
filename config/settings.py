import os

# Binance API Configuration
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "your-api-key-here")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "your-secret-key-here")

# Base URLs
BINANCE_BASE_URL = "https://api.binance.com"  # For REST API
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"  # For WebSocket

# Trading Configuration
TRADING_PAIR = "BTCUSDT"  # Default trading pair
TIMEFRAME = "1m"  # Default candlestick interval (e.g., 1m, 5m, 1h, 1d)
RISK_PER_TRADE = 0.01  # Risk per trade as a percentage of account balance
MAX_OPEN_TRADES = 5  # Maximum number of open trades at a time

# Strategy Settings
USE_STRATEGY = "simple_strategy"  # Default strategy to use
MOVING_AVERAGE_PERIODS = {
    "short": 20,  # Short-term moving average
    "long": 50,   # Long-term moving average
}

# Risk Management
STOP_LOSS_PERCENTAGE = 0.02  # Stop loss at 2% below the entry price
TAKE_PROFIT_PERCENTAGE = 0.04  # Take profit at 4% above the entry price

# Logging Configuration
LOG_FILE = "logs/bot.log"  # Path to the log file
LOG_LEVEL = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR

# Data Storage
DATA_DIR = "data/"  # Directory for storing fetched data
HISTORICAL_DATA_FILE = f"{DATA_DIR}historical_data_{TRADING_PAIR}.csv"

# Environment
USE_TESTNET = True  # Switch between Binance Testnet and Live environment

if USE_TESTNET:
    BINANCE_BASE_URL = "https://testnet.binance.vision/api"
    BINANCE_WS_URL = "wss://testnet.binance.vision/ws"

# Task Scheduling
FETCH_INTERVAL = 60  # Interval for fetching new data in seconds
CLEANUP_INTERVAL = 86400  # Interval for cleaning up old data in seconds