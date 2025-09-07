import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import pickle
import warnings
import os

warnings.filterwarnings('ignore')

class BTCHourlyPredictor:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.last_training_date = None

    def prepare_prediction_input(self, data, num_recent_hours=24):
        """Prepare the most recent data for prediction"""
        recent_data = data.tail(num_recent_hours).copy()
        latest_data = recent_data.iloc[-1:].copy()
        return latest_data

    def predict_next_hours(self, latest_data, hours=6):
        """Predict next N hours"""
        if self.model is None:
            # For demo purposes, generate random predictions
            current_price = latest_data['close'].values[0] if 'close' in latest_data.columns else 50000
            
            predictions = []
            confidence_intervals = []
            
            for hour in range(hours):
                pred = current_price * (1 + np.random.uniform(-0.02, 0.02))
                confidence = 0.03
                lower = pred * (1 - confidence)
                upper = pred * (1 + confidence)
                
                predictions.append(round(pred, 2))
                confidence_intervals.append((round(lower, 2), round(upper, 2)))
            
            return predictions, confidence_intervals
        
        # If model was trained, use it for prediction
        current_features = latest_data[self.feature_columns].copy()
        predictions = []
        confidence_intervals = []

        for hour in range(hours):
            pred = self.model.predict(current_features.values.reshape(1, -1))[0]
            confidence = 0.03
            lower = pred * (1 - confidence)
            upper = pred * (1 + confidence)

            predictions.append(pred)
            confidence_intervals.append((lower, upper))

            # Update features for next prediction
            current_features['close'] = pred
            current_features['open'] = pred
            current_features['high'] = pred * 1.005
            current_features['low'] = pred * 0.995

        return predictions, confidence_intervals

    def feature_importance(self):
        if self.model is None:
            raise ValueError("Model not loaded or trained.")
        feature_importance = self.model.named_steps['xgb'].feature_importances_
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        return importance_df

class ETHHourlyPredictor(BTCHourlyPredictor):
    """ETH predictor - can have different logic if needed"""
    pass

# Utility functions
def save_model(predictor, filename):
    """Save trained predictor instance"""
    with open(filename, 'wb') as f:
        pickle.dump(predictor, f)
    print(f"Model saved to {filename}")

def load_model(filename):
    """Load trained predictor instance"""
    with open(filename, 'rb') as f:
        predictor = pickle.load(f)
    return predictor

def create_and_save_models():
    """Create and save placeholder models"""
    # Create pkdata directory if it doesn't exist
    os.makedirs('predictor/pkdata', exist_ok=True)
    
    # Create BTC model
    btc_predictor = BTCHourlyPredictor()
    save_model(btc_predictor, 'predictor/pkdata/btc_hourly_predictor.pkl')
    
    # Create ETH model
    eth_predictor = ETHHourlyPredictor()
    save_model(eth_predictor, 'predictor/pkdata/eth_hourly_predictor.pkl')
    
    print("Models created and saved successfully!")

# Create models when this module is imported
create_and_save_models()