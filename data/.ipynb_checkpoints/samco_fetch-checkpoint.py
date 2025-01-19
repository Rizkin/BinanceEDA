import requests
import json
from datetime import datetime
from config.settings import SAMCO_USER_ID, SAMCO_PASSWORD
import os

# Defining the endpoints as variables
login_link = 'https://tradeapi.samco.in/login'
index_link = 'https://tradeapi.samco.in/indexData'
marketdepth_link = 'https://tradeapi.samco.in/marketDepth'
search_link = 'https://tradeapi.samco.in/eqDervSearch/search'
optionchain_link = 'https://api.stocknote.com/option/optionChain'
candledata_link = 'https://api.stocknote.com/intraday/candleData'
indexcandledata_link = 'https://api.stocknote.com/intraday/indexCandleData'
historical_candledata_link = 'https://api.stocknote.com/history/candleData'
historical_indexcandledata_link = 'https://api.stocknote.com/history/indexCandleData'

def samco_connect():
    """
    Connects to the SAMCO API using provided user credentials.

    Returns:
        dict: JSON response from the SAMCO API, including session token or error details.
    Raises:
        ValueError: If the environment variables for user credentials are missing.
        requests.exceptions.RequestException: If the API request fails.
    """
    # Fetch environment variables for credentials
    SAMCO_USER_ID = os.getenv("SAMCO_USER_ID")
    SAMCO_PASSWORD = os.getenv("SAMCO_PASSWORD")

    # Validate credentials
    if not SAMCO_USER_ID or not SAMCO_PASSWORD:
        raise ValueError("SAMCO_USER_ID and SAMCO_PASSWORD environment variables are required.")

    # Define headers and request body
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    request_body = {
        "userId": SAMCO_USER_ID,
        "password": SAMCO_PASSWORD
    }

    # Define the API endpoint
    login_link = 'https://tradeapi.samco.in/login'

    try:
        # Make the POST request
        response = requests.post(
            login_link,
            data=json.dumps(request_body),
            headers=headers
        )

        # Raise an HTTPError if the response code indicates an error
        response.raise_for_status()

        # Parse the response JSON
        response_dict = response.json()

        # Check for success in the response
        if response_dict.get('status') != 'Success':
            raise Exception(f"Login failed: {response_dict.get('statusMessage')}")

        return response_dict

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while connecting to SAMCO API: {e}")
        return {"status": "Failure", "error": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"status": "Failure", "error": str(e)}



def get_historical_candle_data(session_token, exchange, symbolName, fromDate, toDate=None):
    """
    Fetch historical candle data for a given symbol from a specified date range.

    :param session_token: (str) Session token for API authentication.
    :param exchange: (str) The exchange (e.g., NSE).
    :param symbolName: (str) The name of the symbol (e.g., ITC).
    :param fromDate: (str) The start date in 'YYYY-MM-DD' format.
    :param toDate: (str, optional) The end date in 'YYYY-MM-DD' format. Defaults to today's date.
    :return: (dict) JSON response from the API.
    """
    # Set toDate to today's date if not provided
    if toDate is None:
        toDate = datetime.now().strftime('%Y-%m-%d')
    
    # API endpoint
    historical_candledata_link = 'https://api.stocknote.com/history/candleData'
    
    # Headers
    historical_candledata_headers = {
        'Accept': 'application/json',
        'x-session-token': session_token
    }
    
    # API Request
    try:
        response = requests.get(
            historical_candledata_link,
            params={
                'exchange': exchange,
                'symbolName': symbolName,
                'fromDate': fromDate,
                'toDate': toDate
            },
            headers=historical_candledata_headers
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_intraday_candle_data(session_token, symbolName, fromDate, toDate=None, exchange=None, interval=None):
    if not session_token:
        print("Error: Session token is missing!")
        return None

    if toDate is None:
        toDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if len(fromDate) == 10:
        fromDate += " 00:00:00"

    historical_candledata_link = 'https://api.stocknote.com/intraday/candleData'

    headers = {
        'Accept': 'application/json',
        'x-session-token': session_token
    }

    params = {
        'symbolName': symbolName,
        'fromDate': fromDate,
        'toDate': toDate,
        'interval': interval
    }
    if exchange:
        params['exchange'] = exchange

    # # Debugging logs
    # print("Headers:", headers)
    # print("URL:", historical_candledata_link)
    # print("Params:", params)

    try:
        response = requests.get(historical_candledata_link, params=params, headers=headers)
        # print("Response Status Code:", response.status_code)
        if response.status_code == 500:
            print("Server error occurred. Check server status or parameters.")
        response.raise_for_status()  # Raise for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print("Response Text:", response.text if 'response' in locals() else "No response")
        return None



def get_option_chain(session_token, searchSymbolName, exchange=None, expiryDate=None, strikePrice=None, optionType=None):
    """
    Fetch the option chain for a given symbol.

    :param session_token: (str) Session token for API authentication.
    :param searchSymbolName: (str) The trading symbol of the scrip to be searched.
    :param exchange: (str, optional) The exchange name (e.g., NSE, NFO). Defaults to NSE.
    :param expiryDate: (str, optional) Expiry date in yyyy-MM-dd format.
    :param strikePrice: (str, optional) Strike price for filtering options.
    :param optionType: (str, optional) Option type (PE or CE).
    :return: (dict) JSON response from the API or None if an error occurs.
    """
    # Validate session token
    if not session_token:
        raise ValueError("Session token is missing!")

    if not searchSymbolName:
        raise ValueError("searchSymbolName is required!")

    # API endpoint
    option_chain_link = 'https://api.stocknote.com/option/optionChain'

    # Headers
    headers = {
        'Accept': 'application/json',
        'x-session-token': session_token
    }

    # Parameters
    params = {
        'searchSymbolName': searchSymbolName
    }
    if exchange:
        params['exchange'] = exchange
    if expiryDate:
        params['expiryDate'] = expiryDate
    if strikePrice:
        params['strikePrice'] = strikePrice
    if optionType:
        params['optionType'] = optionType

    # Debugging logs
    # print("Headers:", headers)
    # print("URL:", option_chain_link)
    # print("Params:", params)

    # API Request
    try:
        response = requests.get(option_chain_link, params=params, headers=headers)
        # print("Response Status Code:", response.status_code)
        if response.status_code == 500:
            print("Server error occurred. Check server status or parameters.")
        response.raise_for_status()  # Raise for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


