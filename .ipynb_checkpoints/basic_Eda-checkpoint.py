apikey = 'YOURAPIKEY'
secret = 'YOURAPISECRET'
### testing commit

!pip install python-binance pandas mplfinance

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
client = Client(apikey, secret)


tickers = client.get_all_tickers()

tickers[1]['price']
ticker_df = pd.DataFrame(tickers)
ticker_df.head()
ticker_df.tail()
ticker_df.set_index('symbol', inplace=True)
float(ticker_df.loc['ETHBTC']['price'])
depth = client.get_order_book(symbol='BTCUSDT')
#depth
depth_df = pd.DataFrame(depth['asks'])
depth_df.columns = ['Price', 'Volume']
depth_df.head()

depth_df.dtypes

client.get_historical_klines??
historical = client.get_historical_klines('ETHBTC', Client.KLINE_INTERVAL_1DAY, '11 Nov 2024')

#historical
hist_df = pd.DataFrame(historical)
hist_df.head()


hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']

hist_df.tail()
hist_df.shape
hist_df.dtypes

hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit='s')
hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']/1000, unit='s')

numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)

hist_df.tail()
hist_df.dtypes
hist_df.describe()

hist_df.info()
import mplfinance as mpf
hist_df.set_index('Close Time').tail(100)

mpf.plot(hist_df.set_index('Close Time').tail(120), 
        type='candle', style='charles', 
        volume=True, 
        title='ETHBTC Last 120 Days', 
        mav=(10,20,30))





