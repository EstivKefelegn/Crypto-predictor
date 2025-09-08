from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .scraper import fetch_recent_data
from .models import CoinHistory
from django.http import JsonResponse
from asgiref.sync import async_to_sync
import os
import pandas as pd
import pickle

COINS = ["BTCUSDT", "ETHUSDT"]

def landing_page(request):
    return render(request, 'predictor/landing.html')

@login_required
def home(request):
    context = {"coins": COINS}
    return render(request, "predictor/main.html", context)

@login_required
def scrape_coin(request, coin):
    if coin not in COINS:
        return JsonResponse({"error": "Invalid coin"}, status=400)
    
    try:
        data = async_to_sync(fetch_recent_data)(coin)
        
        for index, row in data.iterrows():
            timestamp = row['timestamp']
            if hasattr(timestamp, 'to_pydatetime'):
                timestamp = timestamp.to_pydatetime()
            
            CoinHistory.objects.update_or_create(
                coin_symbol=coin,
                timestamp=timestamp,
                defaults={
                    'open_price': float(row['open']),
                    'high_price': float(row['high']),
                    'low_price': float(row['low']),
                    'close_price': float(row['close']),
                    'volume': float(row['volume'])
                }
            )
        
        request.session["coin_selected"] = coin
        request.session["hours"] = len(data)
        
        return redirect("display_data")
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        import traceback
        traceback.print_exc()
        return redirect("home")
@login_required
def display_data(request):
    coin_selected = request.session.get("coin_selected")
    context = {"coins": COINS}
    
    if coin_selected:
        coin_data = CoinHistory.objects.filter(coin_symbol=coin_selected).order_by('-timestamp')
        hours = coin_data.count()
        context.update({
            "coin_selected": coin_selected,
            "hours": hours,
            "coin_data": coin_data
        })
    
    return render(request, "predictor/display_data.html", context)

@login_required
def predict_coin(request, coin):
    if coin not in COINS:
        return redirect("home")

    # Fetch last 24 hours of data
    coin_data = CoinHistory.objects.filter(coin_symbol=coin).order_by('-timestamp')[:24]
    if not coin_data.exists():
        return redirect("home")

    # Convert queryset to DataFrame and convert Decimal to float
    df = pd.DataFrame(list(coin_data.values(
        'timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
    )))
    
    # Convert Decimal fields to float
    decimal_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
    for col in decimal_columns:
        df[col] = df[col].astype(float)
    
    df.rename(columns={
        'open_price': 'open',
        'high_price': 'high',
        'low_price': 'low',
        'close_price': 'close'
    }, inplace=True)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Load the trained predictor
    model_filename = "btc_hourly_predictor.pkl" if coin == "BTCUSDT" else "eth_hourly_predictor.pkl"
    model_path = os.path.join(os.path.dirname(__file__), "pkdata", model_filename)

    try:
        from .predictor import BTCHourlyPredictor, ETHHourlyPredictor
        
        with open(model_path, 'rb') as f:
            predictor = pickle.load(f)

        latest_data = predictor.prepare_prediction_input(df, num_recent_hours=24)
        predictions, intervals = predictor.predict_next_hours(latest_data, hours=6)

        context = {
            "coins": COINS,
            "coin_selected": coin,
            "hours": coin_data.count(),
            "predictions": list(zip(predictions, intervals))
        }

        return render(request, "predictor/main.html", context)

    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return redirect("display_data")