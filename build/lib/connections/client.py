import os
from binance.client import Client
from config.settings import BINANCE_API_KEY, BINANCE_SECRET_KEY, USE_TESTNET

class BinanceClient:
    def __init__(self):
        """
        Initializes the Binance API client using settings from config/settings.py.
        """
        self.api_key = BINANCE_API_KEY
        self.api_secret = BINANCE_SECRET_KEY
        self.use_testnet = USE_TESTNET

        if not self.api_key or not self.api_secret:
            raise ValueError("API Key and Secret Key are required! Check config/settings.py.")

        # Set base URLs for testnet or live environment
        self.base_url = "https://testnet.binance.vision/api" if self.use_testnet else "https://api.binance.com"

        # Initialize REST API client
        self.client = Client(api_key=self.api_key, api_secret=self.api_secret)
        if self.use_testnet:
            self.client.API_URL = self.base_url

        print(f"Initialized Binance Client (Testnet: {self.use_testnet})")

    # ---------------------------
    # General Endpoints
    # ---------------------------
    def test_connection(self):
        """
        Test the connection to the Binance API.
        """
        try:
            status = self.client.ping()
            print("Connection successful:", status)
            return status
        except Exception as e:
            print("Error testing connection:", e)
            raise

    def get_server_time(self):
        """
        Get the server time from Binance.
        """
        try:
            server_time = self.client.get_server_time()
            return server_time
        except Exception as e:
            print("Error fetching server time:", e)
            raise

    # ---------------------------
    # Market Data Endpoints
    # ---------------------------
    def get_symbol_ticker(self, symbol):
        """
        Get the current price for a symbol.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker for {symbol}:", e)
            raise

    def get_klines(self, symbol, interval, limit=100):
        """
        Get historical candlestick data.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param interval: Candlestick interval (e.g., '1m', '5m', '1h').
        :param limit: Number of data points to retrieve (default: 100).
        """
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            return klines
        except Exception as e:
            print(f"Error fetching candlestick data for {symbol}:", e)
            raise

    # ---------------------------
    # Account and Trade Endpoints
    # ---------------------------
    def get_account_balance(self):
        """
        Fetch the account balance for all assets.
        """
        try:
            account_info = self.client.get_account()
            balances = account_info['balances']
            return {item['asset']: float(item['free']) for item in balances if float(item['free']) > 0}
        except Exception as e:
            print("Error fetching account balance:", e)
            raise

    def get_trade_history(self, symbol):
        """
        Fetch recent trade history for a symbol.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        """
        try:
            trades = self.client.get_my_trades(symbol=symbol)
            return trades
        except Exception as e:
            print(f"Error fetching trade history for {symbol}:", e)
            raise

    # ---------------------------
    # Order Management Endpoints
    # ---------------------------
    def create_order(self, symbol, side, order_type, quantity, price=None):
        """
        Place a new order.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param side: 'BUY' or 'SELL'.
        :param order_type: 'MARKET', 'LIMIT', etc.
        :param quantity: Quantity to trade.
        :param price: Price for limit orders (optional).
        """
        try:
            if order_type == 'LIMIT' and price is None:
                raise ValueError("Price is required for LIMIT orders.")
            
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                price=price if order_type == 'LIMIT' else None,
                timeInForce="GTC" if order_type == 'LIMIT' else None
            )
            return order
        except Exception as e:
            print(f"Error creating order for {symbol}:", e)
            raise

    def cancel_order(self, symbol, order_id):
        """
        Cancel an existing order.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param order_id: ID of the order to cancel.
        """
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return result
        except Exception as e:
            print(f"Error canceling order {order_id} for {symbol}:", e)
            raise

    def get_open_orders(self, symbol=None):
        """
        Get all open orders or for a specific symbol.
        :param symbol: Trading pair (optional).
        """
        try:
            open_orders = self.client.get_open_orders(symbol=symbol)
            return open_orders
        except Exception as e:
            print(f"Error fetching open orders for {symbol or 'all symbols'}:", e)
            raise
