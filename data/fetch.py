import requests
import logging
from connections.client import BinanceClient
from config.settings import TRADING_PAIR, TIMEFRAME, BINANCE_API_KEY, BINANCE_SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceAPIError(Exception):
    """Custom exception for Binance API errors."""
    pass

class BinanceBaseFetcher:
    @staticmethod
    def _make_request(method, url, headers=None, params=None):
        try:
            logger.info(f"Making {method} request to {url} with params: {params}")
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            logger.info(f"Raw Response: {response.text}")  # Log the raw response
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise BinanceAPIError(f"Request failed: {e}")


class BinanceDataFetcher(BinanceBaseFetcher):
    """
    Fetches spot trading data using BinanceClient.
    """
    def __init__(self):
        self.client = BinanceClient()

    def get_historical_klines(self, symbol=TRADING_PAIR, interval=TIMEFRAME, limit=100):
        """
        Fetch historical candlestick (OHLCV) data.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param interval: Candlestick interval (e.g., '1m', '5m', '1h').
        :param limit: Number of data points to retrieve.
        :return: List of candlestick data.
        """
        try:
            logger.info(f"Fetching historical klines for {symbol} with interval {interval} and limit {limit}")
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            return klines
        except Exception as e:
            logger.error(f"Error fetching historical klines: {e}")
            raise BinanceAPIError(f"Error fetching historical klines: {e}")

    def get_current_price(self, symbol=TRADING_PAIR):
        """
        Fetch the current price for a symbol.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :return: Current price.
        """
        try:
            logger.info(f"Fetching current price for {symbol}")
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return ticker['price']
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            raise BinanceAPIError(f"Error fetching current price: {e}")

    def get_recent_trades(self, symbol=TRADING_PAIR, limit=10):
        """
        Fetch recent trades for a symbol.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param limit: Number of recent trades to retrieve.
        :return: List of recent trades.
        """
        try:
            logger.info(f"Fetching recent trades for {symbol} with limit {limit}")
            trades = self.client.client.get_recent_trades(symbol=symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"Error fetching recent trades: {e}")
            raise BinanceAPIError(f"Error fetching recent trades: {e}")

class BinanceOptionsFetcher(BinanceBaseFetcher):
    """
    Fetches options trading data from Binance.
    """
    BASE_URL = "https://eapi.binance.com"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {"X-MBX-APIKEY": self.api_key}

    def get_option_info(self, symbol):
        """
        Fetch information for a specific option symbol.
        :param symbol: Option symbol (e.g., 'BTC-250328-90000-P').
        :return: Option info as a dictionary.
        """
        endpoint = f"{self.BASE_URL}/eapi/v1/exchangeInfo"
        try:
            data = self._make_request("GET", endpoint, headers=self.headers)
            # Filter the optionSymbols for the specific symbol
            option_info = next((item for item in data.get('optionSymbols', []) if item['symbol'] == symbol), None)
            if option_info is None:
                raise BinanceAPIError(f"Option symbol {symbol} not found.")
            return option_info
        except BinanceAPIError as e:
            logger.error(f"Error fetching option info for {symbol}: {e}")
            raise

    def get_current_option_price(self, symbol):
        """
        Fetch the current price for an options symbol.
        :param symbol: Option symbol (e.g., 'BTC-250328-90000-P').
        :return: Current price as a float.
        """
        endpoint = f"{self.BASE_URL}/eapi/v1/mark"
        try:
            logger.info(f"Fetching current price for option symbol {symbol}")
            params = {"symbol": symbol}
            data = self._make_request("GET", endpoint, headers=self.headers, params=params)

            # Since the response is a list, access the first element
            if not data or not isinstance(data, list):
                raise BinanceAPIError(f"Unexpected response format: {data}")
            
            # Extract the markPrice from the first item
            return float(data[0]['markPrice'])
            
        except BinanceAPIError as e:
            logger.error(f"Error fetching current option price for {symbol}: {e}")
            raise


    def get_historical_option_klines(self, symbol, interval="1m", startTime=None, endTime=None, limit=100):
        """
        Fetch historical candlestick (OHLCV) data for options.
        :param symbol: Option symbol (e.g., 'BTC-250328-90000-P').
        :param interval: Candlestick interval (e.g., '1m', '5m', '1h').
        :param startTime: Start time in milliseconds (optional).
        :param endTime: End time in milliseconds (optional).
        :param limit: Number of data points to retrieve (max 1000).
        :return: List of candlestick data.
        """
        endpoint = f"{self.BASE_URL}/eapi/v1/klines"
        try:
            logger.info(f"Fetching historical klines for option symbol {symbol} with interval {interval}")
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit
            }
            return self._make_request("GET", endpoint, headers=self.headers, params=params)
        except BinanceAPIError as e:
            logger.error(f"Error fetching historical option klines for {symbol}: {e}")
            raise

    def get_recent_option_trades(self, symbol, limit=10):
        """
        Fetch recent trades for an options symbol.
        :param symbol: Option symbol (e.g., 'BTC-250328-90000-P').
        :param limit: Number of recent trades to retrieve (max 100).
        :return: List of recent trades.
        """
        endpoint = f"{self.BASE_URL}/eapi/v1/trades"
        try:
            logger.info(f"Fetching recent trades for option symbol {symbol} with limit {limit}")
            params = {"symbol": symbol, "limit": limit}
            return self._make_request("GET", endpoint, headers=self.headers, params=params)
        except BinanceAPIError as e:
            logger.error(f"Error fetching recent option trades for {symbol}: {e}")
            raise
