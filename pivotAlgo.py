import kiteconnect
import pandas as pd

# API credentials
api_key = input("please enter your api key:  ")
api_secret = input("please enter your secret key:  ")
access_token = input("please enter your access token:  ")

# Initialize KiteConnect instance
kite = kiteconnect.KiteConnect(api_key=api_key)

# Set access token
kite.set_access_token(access_token)

# Define function to calculate pivot points
def calculate_pivot_points(high, low, close):
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    return (pivot, r1, r2, s1, s2)

# Define function to get historical data for a given instrument
def get_historical_data(instrument_token, interval):
    # Set end date to today and start date to 7 days ago
    to_date = pd.Timestamp.today().date()
    from_date = to_date - pd.Timedelta(days=7)

    # Fetch historical data using KiteConnect
    data = kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=interval
    )

    # Convert data to Pandas DataFrame and set date as index
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)

    return df

# Get historical data for HDFC Bank
hdfcbank = get_historical_data(instrument_token="HDFCBANK", interval="5minute")

# Calculate pivot points
hdfcbank["pivot"], hdfcbank["r1"], hdfcbank["r2"], hdfcbank["s1"], hdfcbank["s2"] = calculate_pivot_points(hdfcbank["high"], hdfcbank["low"], hdfcbank["close"])

# Define function to place a limit order
def place_limit_order(tradingsymbol, quantity, price, transaction_type, variety):
    order_id = kite.place_order(
        exchange=kite.EXCHANGE_NSE,
        tradingsymbol=tradingsymbol,
        quantity=quantity,
        transaction_type=transaction_type,
        order_type=kite.ORDER_TYPE_LIMIT,
        product=kite.PRODUCT_MIS,
        price=price,
        variety=variety
    )["order_id"]
    return order_id

# Define function to place a stop loss order
def place_stop_loss_order(tradingsymbol, quantity, price, transaction_type, variety):
    order_id = kite.place_order(
        exchange=kite.EXCHANGE_NSE,
        tradingsymbol=tradingsymbol,
        quantity=quantity,
        transaction_type=transaction_type,
        order_type=kite.ORDER_TYPE_SLM,
        product=kite.PRODUCT_MIS,
        trigger_price=price,
        price=price,
        variety=variety
    )["order_id"]
    return order_id

    # Place buy order if current price is above R1
    if hdfcbank["last_price"].iloc[-1] > hdfcbank["r1"].iloc[-1]:
        price = hdfcbank["last_price"].iloc[-1] + 0.05
        order_id = place_limit_order(tradingsymbol="HDFCBANK", quantity=1, price=price, transaction_type=kite.TRANSACTION_TYPE_BUY, variety=kite.VARIETY_REGULAR)
        #Place stop loss order at R2
        stop_loss_price = hdfcbank["r2"].iloc[-1] - 0.05
        stop_loss_order_id = place_stop_loss_order(tradingsymbol="HDFCBANK", quantity=1, price=stop_loss_price, transaction_type=kite.TRANSACTION_TYPE_SELL, variety=kite.VARIETY_REGULAR)
        print(f"Placed buy order {order_id} at price {price} and stop loss order {stop_loss_order_id} at price {stop_loss_price}")

    #Place sell order if current price is below S1
    elif hdfcbank["last_price"].iloc[-1] < hdfcbank["s1"].iloc[-1]:
        price = hdfcbank["last_price"].iloc[-1] - 0.05
        order_id = place_limit_order(tradingsymbol="HDFCBANK", quantity=1, price=price, transaction_type=kite.TRANSACTION_TYPE_SELL, variety=kite.VARIETY_REGULAR)
        # Place stop loss order at S2
        stop_loss_price = hdfcbank["s2"].iloc[-1] + 0.05
        stop_loss_order_id = place_stop_loss_order(tradingsymbol="HDFCBANK", quantity=1, price=stop_loss_price, transaction_type=kite.TRANSACTION_TYPE_BUY, variety=kite.VARIETY_REGULAR)
        print(f"Placed sell order {order_id} at price {price} and stop loss order {stop_loss_order_id} at price {stop_loss_price}")

    #Do nothing if current price is between R1 and S1

    else:
        print("Do nothing.")
