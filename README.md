# BinanceEDA
Binance

1. Objective: 
Trying to build algo bot to trade using binance api 

2. Project structure: 
    Planned:
        BinanceEDA/
        ├── config/
        │   └── settings.py         # Configuration file for API keys, URLs, etc.
        ├── connections/
        │   ├── client.py           # Binance API client setup
        │   ├── websocket.py        # WebSocket connections
        │   └── rest.py             # REST API methods
        ├── data/
        │   ├── fetch.py            # Fetch and store live data
        │   ├── preprocess.py       # Data cleaning and preparation
        │   ├── analysis.py         # Data analysis and indicators
        ├── strategies/
        │   ├── base_strategy.py    # Abstract class for strategy implementation
        │   ├── simple_strategy.py  # Example: Moving Average Crossover
        │   ├── advanced_strategy.py # Example: RSI + Bollinger Bands
        ├── trading/
        │   ├── order_manager.py    # Handle buy/sell/cancel orders
        │   ├── portfolio.py        # Portfolio management and P&L tracking
        │   └── risk_manager.py     # Risk management logic
        ├── utils/
        │   ├── logger.py           # Logging functionality
        │   ├── helpers.py          # Common helper functions
        │   └── scheduler.py        # Task scheduling (if required)
        ├── main.py                 # Entry point of the bot
        └── README.md               # Documentation
        
        Currently: 
        BinanceEDA/  # Root directory
        ├── config/
        │   ├── __init__.py
        │   └── settings.py
        ├── connections/
        │   ├── __init__.py
        │   └── client.py
        ├── strategies/
        │   ├── __init__.py
        │   └── simple_strategy.py
        ├── trading/
        │   ├── __init__.py
        │   └── order_manager.py
        ├── main.py
        ├── setup.py
        └── README.md

3. Device Details:
  Will be relying on API for now and keys are already stored in the AWS free tier device.
  Device Details: 1 t3.micro instance.
  Will need to setup S3 storage situation if required currently the box has over 4 GB space.


5. Objectives ?
   1. Get all BTC USD data for last 2 years at 15 mnts interval. (estimate the size of the data) Using Binance API
   2. Store the data in csv or something optimal for reading.
   3. Create analysis.py where we run HMM (hidden markov model) to identify the regimes and predict the stages. 


   







