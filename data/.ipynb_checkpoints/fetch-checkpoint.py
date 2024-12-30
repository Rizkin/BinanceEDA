import requests
import logging
from connections.client import BinanceClient
from config.settings import TRADING_PAIR, TIMEFRAME, BINANCE_API_KEY, BINANCE_SECRET_KEY
import time
import pandas as pd
from datetime import datetime, timedelta

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
            logger.info(f"Raw Response: {response.text}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise BinanceAPIError(f"Request failed: {e}")

class BinanceDataFetcher:
    """
    Fetches spot trading data using BinanceClient.
    """
    def __init__(self):
        self.client = BinanceClient()

    def fetch_candlestick_data(self, symbol, interval, start_time, end_time, limit=1000):
        """
        Fetch historical candlestick (OHLCV) data.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param interval: Candlestick interval (e.g., '1m', '5m', '1h').
        :param start_time: Start time in milliseconds.
        :param end_time: End time in milliseconds.
        :param limit: Number of data points to retrieve (default: 1000).
        :return: List of candlestick data.
        """
        try:
            logger.info(f"Fetching candlestick data for {symbol} with interval {interval}, startTime {start_time}, endTime {end_time}, limit {limit}.")
            return self.client.client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error fetching candlestick data: {e}")
            raise BinanceAPIError(f"Error fetching candlestick data: {e}")

    def fetch_and_save_historical_data(self, symbol, interval, start_days_ago, end_days_ago, output_file):
        """
        Fetch historical data and save it to a CSV file.
        :param symbol: Trading pair (e.g., 'BTCUSDT').
        :param interval: Candlestick interval (e.g., '15m').
        :param start_days_ago: Start time in days ago.
        :param end_days_ago: End time in days ago.
        :param output_file: Name of the CSV file to save data.
        """
        start_time = int((datetime.now() - timedelta(days=start_days_ago)).timestamp() * 1000)
        end_time = int((datetime.now() - timedelta(days=end_days_ago)).timestamp() * 1000)

        logger.info(f"Fetching historical data for {symbol} from {datetime.fromtimestamp(start_time / 1000)} to {datetime.fromtimestamp(end_time / 1000)} with {interval} interval.")

        all_data = []
        chunk_size = 1000  # Limit per API call
        current_start_time = start_time

        while current_start_time < end_time:
            current_end_time = min(current_start_time + (chunk_size * self.interval_to_milliseconds(interval)), end_time)
            logger.info(f"Fetching data from {datetime.fromtimestamp(current_start_time / 1000)} to {datetime.fromtimestamp(current_end_time / 1000)}.")
            try:
                data = self.fetch_candlestick_data(
                    symbol=symbol,
                    interval=interval,
                    start_time=current_start_time,
                    end_time=current_end_time,
                    limit=chunk_size
                )
                if not data:
                    logger.warning(f"No more data returned for time range: {datetime.fromtimestamp(current_start_time / 1000)} to {datetime.fromtimestamp(current_end_time / 1000)}.")
                    break
                all_data.extend(data)
                current_start_time = data[-1][0] + 1  # Move to the next interval
                time.sleep(0.1)  # Respect API rate limits
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                raise

        if not all_data:
            logger.warning("No data fetched for the specified time range.")
            return

        logger.info(f"Fetched {len(all_data)} rows. Saving data to {output_file}.")

        columns = ["timestamp", "open", "high", "low", "close", "volume",
                   "close_time", "quote_asset_volume", "number_of_trades",
                   "taker_buy_base", "taker_buy_quote", "ignore"]
        df = pd.DataFrame(all_data, columns=columns)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved successfully to {output_file}.")

    @staticmethod
    def interval_to_milliseconds(interval):
        """
        Convert a Binance interval string to milliseconds.
        :param interval: Binance interval string (e.g., '1m', '1h').
        :return: Interval in milliseconds.
        """
        interval_map = {
            "1m": 60 * 1000,
            "3m": 3 * 60 * 1000,
            "5m": 5 * 60 * 1000,
            "15m": 15 * 60 * 1000,
            "30m": 30 * 60 * 1000,
            "1h": 60 * 60 * 1000,
            "2h": 2 * 60 * 60 * 1000,
            "4h": 4 * 60 * 60 * 1000,
            "6h": 6 * 60 * 60 * 1000,
            "8h": 8 * 60 * 60 * 1000,
            "12h": 12 * 60 * 60 * 1000,
            "1d": 24 * 60 * 60 * 1000,
            "3d": 3 * 24 * 60 * 60 * 1000,
            "1w": 7 * 24 * 60 * 60 * 1000,
            "1M": 30 * 24 * 60 * 60 * 1000
        }
        return interval_map[interval]




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
            if not data or not isinstance(data, list):
                raise BinanceAPIError(f"Unexpected response format: {data}")
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
