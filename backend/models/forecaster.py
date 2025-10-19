"""
Machine Learning Forecasting Module using Prophet
"""
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

logger = logging.getLogger(__name__)


class NetworkForecaster:
    """Time-series forecasting for DePIN network growth"""

    def __init__(self):
        """Initialize the forecaster"""
        self.model = None
        self.training_data = None
        self.forecast_result = None

    def prepare_data(self, historical_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepare historical data for Prophet model

        Args:
            historical_data: List of daily metrics with 'date' and 'total_vehicles'

        Returns:
            DataFrame formatted for Prophet (ds, y columns)
        """
        logger.info(f"Preparing {len(historical_data)} data points for forecasting")

        # Convert to DataFrame
        df = pd.DataFrame(historical_data)

        # Prophet requires 'ds' (datestamp) and 'y' (value) columns
        df_prophet = pd.DataFrame({
            'ds': pd.to_datetime(df['date']),
            'y': df['total_vehicles']
        })

        # Sort by date
        df_prophet = df_prophet.sort_values('ds').reset_index(drop=True)

        logger.info(f"Data prepared: {len(df_prophet)} rows, date range {df_prophet['ds'].min()} to {df_prophet['ds'].max()}")
        return df_prophet

    def train_model(self, historical_data: List[Dict[str, Any]]) -> bool:
        """
        Train Prophet model on historical data

        Args:
            historical_data: List of daily metrics

        Returns:
            True if training successful, False otherwise
        """
        try:
            logger.info("Training Prophet forecasting model...")

            # Prepare data
            self.training_data = self.prepare_data(historical_data)

            # Initialize Prophet model with simple linear growth (no seasonality for demo)
            self.model = Prophet(
                daily_seasonality=False, # No daily seasonality
                weekly_seasonality=False, # Not enough data for weekly seasonality
                yearly_seasonality=False, # Not enough data for yearly seasonality
                # seasonality_mode='multiplicative', # going wild with current mocked simple data
                # changepoint_prior_scale=0.05,  # Controls flexibility
                growth='linear',  # Linear growth only
                changepoint_prior_scale=0.001,  # Very low - almost no trend changes
                interval_width=0.90  # 90% confidence intervals
            )

            # Fit the model
            self.model.fit(self.training_data)

            logger.info("Model training completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False

    def generate_forecast(self, days_ahead: int = 180) -> Dict[str, Any]:
        """
        Generate forecast for specified number of days

        Args:
            days_ahead: Number of days to forecast into the future

        Returns:
            Dictionary containing forecast results
        """
        if not self.model:
            logger.error("Model not trained. Call train_model() first.")
            return {}

        try:
            logger.info(f"Generating {days_ahead}-day forecast...")

            # Create future dataframe
            future = self.model.make_future_dataframe(periods=days_ahead, freq='D')

            # Generate predictions
            forecast = self.model.predict(future)

            # Store forecast result
            self.forecast_result = forecast

            # Extract key metrics
            last_historical_date = self.training_data['ds'].max()
            last_historical_value = self.training_data['y'].iloc[-1]

            # Get future predictions only
            future_forecast = forecast[forecast['ds'] > last_historical_date].copy()

            # Calculate growth metrics
            predictions = []
            for _, row in future_forecast.iterrows():
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_vehicles': int(row['yhat']),
                    'lower_bound': int(row['yhat_lower']),
                    'upper_bound': int(row['yhat_upper']),
                    'confidence': 0.90
                })

            # Calculate key milestones
            end_30_days = future_forecast.iloc[min(29, len(future_forecast)-1)]
            end_90_days = future_forecast.iloc[min(89, len(future_forecast)-1)]
            end_180_days = future_forecast.iloc[min(179, len(future_forecast)-1)] if len(future_forecast) >= 180 else future_forecast.iloc[-1]

            growth_metrics = {
                '30_day': {
                    'predicted_vehicles': int(end_30_days['yhat']),
                    'growth_from_current': int(end_30_days['yhat'] - last_historical_value),
                    'growth_percentage': round(((end_30_days['yhat'] - last_historical_value) / last_historical_value) * 100, 2)
                },
                '90_day': {
                    'predicted_vehicles': int(end_90_days['yhat']),
                    'growth_from_current': int(end_90_days['yhat'] - last_historical_value),
                    'growth_percentage': round(((end_90_days['yhat'] - last_historical_value) / last_historical_value) * 100, 2)
                },
                '180_day': {
                    'predicted_vehicles': int(end_180_days['yhat']),
                    'growth_from_current': int(end_180_days['yhat'] - last_historical_value),
                    'growth_percentage': round(((end_180_days['yhat'] - last_historical_value) / last_historical_value) * 100, 2)
                }
            }

            # Calculate average daily growth
            avg_daily_growth = int((end_90_days['yhat'] - last_historical_value) / 90)

            result = {
                'model_type': 'prophet',
                'forecast_horizon': days_ahead,
                'current_vehicles': int(last_historical_value),
                'current_date': last_historical_date.strftime('%Y-%m-%d'),
                'predictions': predictions,
                'growth_metrics': growth_metrics,
                'avg_daily_growth': avg_daily_growth,
                'confidence_level': 0.90,
                'timestamp': datetime.utcnow().isoformat()
            }

            logger.info(f"Forecast generated: {len(predictions)} future data points")
            logger.info(f"90-day prediction: {growth_metrics['90_day']['predicted_vehicles']} vehicles "
                       f"({growth_metrics['90_day']['growth_percentage']}% growth)")

            return result

        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return {}

    def validate_model(self, test_size: int = 14) -> Dict[str, float]:
        """
        Validate model performance using last N days as test set

        Args:
            test_size: Number of days to use for validation

        Returns:
            Dictionary containing validation metrics
        """
        if not self.model or self.training_data is None:
            logger.error("Model not trained. Call train_model() first.")
            return {}

        try:
            logger.info(f"Validating model with {test_size}-day test set...")

            # Split data
            train_data = self.training_data[:-test_size].copy()
            test_data = self.training_data[-test_size:].copy()

            # Train on train set
            temp_model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05,
                interval_width=0.90
            )
            temp_model.fit(train_data)

            # Predict on test set
            forecast = temp_model.predict(test_data[['ds']])

            # Calculate metrics
            y_true = test_data['y'].values
            y_pred = forecast['yhat'].values

            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

            metrics = {
                'mae': round(mae, 2),
                'rmse': round(rmse, 2),
                'mape': round(mape, 2),
                'test_size': test_size
            }

            logger.info(f"Validation metrics - MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%")
            return metrics

        except Exception as e:
            logger.error(f"Error validating model: {e}")
            return {}

    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Analyze growth trends from the forecast

        Returns:
            Dictionary containing trend analysis
        """
        if self.forecast_result is None:
            logger.error("No forecast available. Call generate_forecast() first.")
            return {}

        try:
            # Get trend component
            trend = self.forecast_result[['ds', 'trend']].copy()

            # Calculate trend growth rate
            trend['daily_change'] = trend['trend'].diff()
            avg_trend_change = trend['daily_change'].mean()

            # Identify acceleration/deceleration
            recent_trend = trend.tail(30)['daily_change'].mean()
            historical_trend = trend.head(30)['daily_change'].mean()

            trend_direction = "accelerating" if recent_trend > historical_trend else "decelerating"

            analysis = {
                'avg_daily_trend_change': round(avg_trend_change, 2),
                'recent_30day_trend': round(recent_trend, 2),
                'historical_30day_trend': round(historical_trend, 2),
                'trend_direction': trend_direction,
                'growth_momentum': round((recent_trend / historical_trend - 1) * 100, 2) if historical_trend != 0 else 0
            }

            logger.info(f"Trend analysis: {trend_direction} growth with {analysis['growth_momentum']:.2f}% momentum change")
            return analysis

        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {}


# Singleton instance
forecaster = NetworkForecaster()
