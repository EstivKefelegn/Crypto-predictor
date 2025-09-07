import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import os
from django.conf import settings

# Import functions under test
from .scraper import fetch_recent_data
from .predictor import make_predictions


class TestCryptoPredictor(unittest.TestCase):
    def setUp(self):
        """Set up test data and mocks"""
        # Mock historical data
        self.mock_data = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=72, freq="h"),
            "open": np.random.uniform(40000, 50000, 72),
            "high": np.random.uniform(41000, 51000, 72),
            "low": np.random.uniform(39000, 49000, 72),
            "close": np.random.uniform(40500, 49500, 72),
            "volume": np.random.uniform(1000, 5000, 72),
        })

        # Mock predictor model
        self.mock_predictor = Mock()
        self.mock_predictor.clean_data.return_value = self.mock_data
        self.mock_predictor.create_features.return_value = self.mock_data
        self.mock_predictor.prepare_prediction_input.return_value = self.mock_data.iloc[-1:]

        # Default: 3 predictions
        self.mock_predictor.predict_next_hours.return_value = (
            [45000, 45200, 45500],
            [(44500, 45500), (44700, 45700), (45000, 46000)],
        )

    @patch("predictor.predictor.fetch_recent_data")
    @patch("predictor.predictor.pickle.load")
    @patch("predictor.predictor.open")
    def test_make_predictions_btc(self, mock_open, mock_pickle_load, mock_fetch):
        """Test BTC predictions"""
        mock_fetch.return_value = self.mock_data
        mock_pickle_load.return_value = self.mock_predictor

        # Mock file context manager
        mock_file = Mock()
        mock_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_open.return_value.__exit__ = Mock(return_value=None)

        predictions, intervals = make_predictions(coin="BTCUSDT", hours_to_predict=3)

        self.assertIsNotNone(predictions)
        self.assertEqual(len(predictions), 3)
        self.assertTrue(all(isinstance(p, (int, float)) for p in predictions))
        mock_fetch.assert_called_once_with("BTCUSDT", hours=72)
        expected_path = os.path.join("pkdata", "btc_hourly_predictor.pkl")
        mock_open.assert_called_once_with(expected_path, "rb")

    @patch("predictor.predictor.fetch_recent_data")
    @patch("predictor.predictor.pickle.load")
    @patch("predictor.predictor.open")
    def test_make_predictions_eth(self, mock_open, mock_pickle_load, mock_fetch):
        """Test ETH predictions with hours_to_predict=2"""
        mock_fetch.return_value = self.mock_data

        # Adjust mock to return exactly 2 predictions for ETH test
        self.mock_predictor.predict_next_hours.return_value = (
            [3000, 3100],
            [(2950, 3050), (3050, 3150)],
        )

        mock_pickle_load.return_value = self.mock_predictor
        mock_file = Mock()
        mock_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_open.return_value.__exit__ = Mock(return_value=None)

        predictions, intervals = make_predictions(coin="ETHUSDT", hours_to_predict=2)

        self.assertEqual(len(predictions), 2)
        expected_path = os.path.join("pkdata", "eth_hourly_predictor.pkl")
        mock_open.assert_called_once_with(expected_path, "rb")

    @patch("predictor.predictor.fetch_recent_data")
    def test_make_predictions_unknown_coin(self, mock_fetch):
        """Test error handling for unknown coin"""
        mock_fetch.return_value = self.mock_data

        with self.assertRaises(ValueError):
            make_predictions(coin="DOGEUSDT", hours_to_predict=3)

    @patch("predictor.scraper.Client")
    def test_fetch_recent_data_structure(self, mock_client):
        """Test fetch_recent_data returns correct DataFrame"""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock historical klines
        mock_klines = [
            [1640995200000, "40000.0", "40500.0", "39500.0", "40200.0", "1000.0",
             1640998800000, "40200000.0", 1000, "5000.0", "50000.0", "0"],
            [1640998800000, "40200.0", "40800.0", "40000.0", "40600.0", "1200.0",
             1641002400000, "48720000.0", 1200, "6000.0", "60000.0", "0"],
        ]
        mock_client_instance.get_historical_klines.return_value = mock_klines

        result = fetch_recent_data("BTCUSDT", hours=24)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertListEqual(
            list(result.columns),
            ["timestamp", "open", "high", "low", "close", "volume"]
        )

    def test_model_files_exist(self):
        """Ensure model files exist (skip if not present)"""
        base_dir = os.path.join(settings.BASE_DIR, "predictor", "pkdata")
        btc_path = os.path.join(base_dir, "btc_hourly_predictor.pkl")
        eth_path = os.path.join(base_dir, "eth_hourly_predictor.pkl")

        # Only check if the directory exists, skip otherwise
        if os.path.exists(base_dir):
            self.assertTrue(os.path.exists(btc_path), "BTC model file should exist")
            self.assertTrue(os.path.exists(eth_path), "ETH model file should exist")
        else:
            self.skipTest("pkdata directory does not exist, skipping model file checks")


if __name__ == "__main__":
    unittest.main(verbosity=2)
