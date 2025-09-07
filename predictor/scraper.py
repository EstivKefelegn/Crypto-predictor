from datetime import datetime, timedelta
from binance import AsyncClient
import pandas as pd
import asyncio

async def fetch_recent_data(coin, hours=24):
    """Fetch only the most recent hours of data needed for prediction"""
    client = await AsyncClient.create(api_key="your_api_key", api_secret="your_api_secret", tld="us")    

    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    print(f"Fetching last {hours} hours of data...")
    
    # Get historical klines
    klines = await client.get_historical_klines(
        coin, 
        AsyncClient.KLINE_INTERVAL_1HOUR,
        start_time.strftime("%d %b %Y %H:%M:%S"),
        end_time.strftime("%d %b %Y %H:%M:%S")
    )
    
    # Process data
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
    
    await client.close_connection()
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]