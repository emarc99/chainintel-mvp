"""
Database module for Supabase integration
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database client for Supabase operations"""

    def __init__(self):
        """Initialize Supabase client"""
        self.client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client connection"""
        try:
            if settings.supabase_url and settings.supabase_key:
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not provided, database features disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")

    def store_network_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Store network metrics in the database

        Args:
            metrics: Dictionary containing network metrics

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Database not initialized, skipping storage")
            return False

        try:
            data = {
                'timestamp': metrics.get('timestamp', datetime.utcnow().isoformat()),
                'total_vehicles': metrics.get('total_vehicles', 0),
                'sample_size': metrics.get('sample_size', 0),
                'top_makes': metrics.get('top_makes', {}),
                'top_models': metrics.get('top_models', {}),
                'year_distribution': metrics.get('year_distribution', {})
            }

            result = self.client.table('network_metrics').insert(data).execute()
            logger.info(f"Stored network metrics: {data['total_vehicles']} vehicles")
            return True
        except Exception as e:
            logger.error(f"Error storing network metrics: {e}")
            return False

    def store_historical_data(self, historical_data: List[Dict[str, Any]]) -> bool:
        """
        Store historical network data

        Args:
            historical_data: List of daily metrics

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Database not initialized, skipping storage")
            return False

        try:
            # Prepare data for batch insert
            records = []
            for record in historical_data:
                records.append({
                    'date': record['date'],
                    'total_vehicles': record['total_vehicles'],
                    'new_vehicles': record['new_vehicles'],
                    'timestamp': record['timestamp']
                })

            # Batch insert
            result = self.client.table('historical_metrics').insert(records).execute()
            logger.info(f"Stored {len(records)} historical data points")
            return True
        except Exception as e:
            logger.error(f"Error storing historical data: {e}")
            return False

    def get_historical_data(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Retrieve historical data from database

        Args:
            days: Number of days to retrieve

        Returns:
            List of historical metrics
        """
        if not self.client:
            logger.warning("Database not initialized, returning empty list")
            return []

        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')

            result = self.client.table('historical_metrics')\
                .select('*')\
                .gte('date', cutoff_date)\
                .order('date', desc=False)\
                .execute()

            data = result.data if hasattr(result, 'data') else []
            logger.info(f"Retrieved {len(data)} historical data points")
            return data
        except Exception as e:
            logger.error(f"Error retrieving historical data: {e}")
            return []

    def store_forecast(self, forecast_data: Dict[str, Any]) -> bool:
        """
        Store ML forecast results

        Args:
            forecast_data: Dictionary containing forecast results

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Database not initialized, skipping storage")
            return False

        try:
            data = {
                'timestamp': datetime.utcnow().isoformat(),
                'model_type': forecast_data.get('model_type', 'prophet'),
                'forecast_horizon': forecast_data.get('forecast_horizon', 180),
                'predictions': forecast_data.get('predictions', []),
                'metrics': forecast_data.get('metrics', {})
            }

            result = self.client.table('forecasts').insert(data).execute()
            logger.info("Stored forecast results")
            return True
        except Exception as e:
            logger.error(f"Error storing forecast: {e}")
            return False

    def get_latest_forecast(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most recent forecast

        Returns:
            Latest forecast data or None
        """
        if not self.client:
            return None

        try:
            result = self.client.table('forecasts')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()

            if hasattr(result, 'data') and result.data:
                logger.info("Retrieved latest forecast")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving forecast: {e}")
            return None


# Singleton instance
db = Database()


# SQL schema for Supabase tables
SQL_SCHEMA = """
-- Network Metrics Table
CREATE TABLE IF NOT EXISTS network_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_vehicles INTEGER NOT NULL,
    sample_size INTEGER,
    top_makes JSONB,
    top_models JSONB,
    year_distribution JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Historical Metrics Table
CREATE TABLE IF NOT EXISTS historical_metrics (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_vehicles INTEGER NOT NULL,
    new_vehicles INTEGER,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Forecasts Table
CREATE TABLE IF NOT EXISTS forecasts (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model_type VARCHAR(50) NOT NULL,
    forecast_horizon INTEGER NOT NULL,
    predictions JSONB NOT NULL,
    metrics JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_network_metrics_timestamp ON network_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_historical_metrics_date ON historical_metrics(date DESC);
CREATE INDEX IF NOT EXISTS idx_forecasts_timestamp ON forecasts(timestamp DESC);
"""
