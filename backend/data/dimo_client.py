"""
DIMO API Client for fetching network data
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dimo import DIMO
from config import settings

logger = logging.getLogger(__name__)


class DIMOClient:
    """Client for interacting with DIMO Network API"""

    def __init__(self):
        """Initialize DIMO client with credentials"""
        self.client = None
        self.dev_jwt = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize DIMO SDK client"""
        try:
            self.client = DIMO(settings.dimo_environment)
            logger.info(f"DIMO client initialized for {settings.dimo_environment} environment")

            # Authenticate if credentials are provided
            if settings.dimo_client_id and settings.dimo_api_key and settings.dimo_domain:
                self._authenticate()
        except Exception as e:
            logger.error(f"Failed to initialize DIMO client: {e}")
            # Continue without authentication - we can still use public APIs

    def _authenticate(self):
        """Authenticate and get developer JWT"""
        try:
            auth_header = self.client.auth.get_dev_jwt(
                client_id=settings.dimo_client_id,
                domain=settings.dimo_domain,
                private_key=settings.dimo_api_key
            )
            self.dev_jwt = auth_header.get("access_token")
            logger.info("Successfully authenticated with DIMO API")
        except Exception as e:
            logger.warning(f"Authentication failed, will use public APIs only: {e}")

    def get_total_vehicles(self) -> Optional[int]:
        """
        Get total number of connected vehicles in DIMO network
        Uses Identity API (public data)
        """
        try:
            query = """
            query {
                vehicles(first: 1) {
                    totalCount
                }
            }
            """
            result = self.client.identity.query(query=query)

            if result and 'data' in result:
                total_count = result['data']['vehicles']['totalCount']
                logger.info(f"Total vehicles in DIMO network: {total_count}")
                return total_count
            return None
        except Exception as e:
            logger.error(f"Error fetching total vehicles: {e}")
            return None

    def get_vehicles_batch(self, first: int = 100, after: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a batch of vehicles with pagination

        Args:
            first: Number of vehicles to fetch
            after: Cursor for pagination

        Returns:
            Dictionary containing vehicles data and page info
        """
        try:
            after_clause = f', after: "{after}"' if after else ''
            query = f"""
            query {{
                vehicles(first: {first}{after_clause}) {{
                    totalCount
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        id
                        definition {{
                            make
                            model
                            year
                        }}
                        aftermarketDevice {{
                            tokenId
                        }}
                    }}
                }}
            }}
            """
            result = self.client.identity.query(query=query)
            return result.get('data', {}).get('vehicles', {})
        except Exception as e:
            logger.error(f"Error fetching vehicles batch: {e}")
            return {}

    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive network statistics

        Returns:
            Dictionary containing various network metrics
        """
        try:
            # Get total vehicles
            total_vehicles = self.get_total_vehicles()

            # Get sample of vehicles to analyze
            vehicles_data = self.get_vehicles_batch(first=1000)

            stats = {
                'total_vehicles': total_vehicles or 0,
                'timestamp': datetime.utcnow().isoformat(),
                'sample_size': len(vehicles_data.get('nodes', [])) if vehicles_data else 0,
            }

            # Analyze vehicle makes/models if we have data
            if vehicles_data and vehicles_data.get('nodes'):
                makes = {}
                models = {}
                years = {}

                for vehicle in vehicles_data['nodes']:
                    if vehicle.get('definition'):
                        make = vehicle['definition'].get('make', 'Unknown')
                        model = vehicle['definition'].get('model', 'Unknown')
                        year = vehicle['definition'].get('year')

                        makes[make] = makes.get(make, 0) + 1
                        models[model] = models.get(model, 0) + 1
                        if year:
                            years[str(year)] = years.get(str(year), 0) + 1

                stats['top_makes'] = dict(sorted(makes.items(), key=lambda x: x[1], reverse=True)[:10])
                stats['top_models'] = dict(sorted(models.items(), key=lambda x: x[1], reverse=True)[:10])
                stats['year_distribution'] = dict(sorted(years.items(), key=lambda x: x[1], reverse=True)[:10])

            logger.info(f"Network stats collected: {stats.get('total_vehicles', 0)} total vehicles")
            return stats

        except Exception as e:
            logger.error(f"Error fetching network stats: {e}")
            return {
                'total_vehicles': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    def get_historical_data_simulation(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Generate simulated historical data for demo purposes
        In production, this would fetch actual historical data from DIMO or blockchain

        Args:
            days: Number of days of historical data to generate

        Returns:
            List of daily network metrics
        """
        logger.info(f"Generating {days} days of simulated historical data")

        # Get current total (or use estimate if API unavailable)
        current_total = self.get_total_vehicles() or 140000  # As of 2025 per research

        # Generate realistic growth pattern
        historical_data = []
        base_daily_growth = 150  # Average new vehicles per day

        # Start from past value and grow to current
        import random
        random.seed(42)  # Consistent data for demo

        starting_total = current_total - (days * base_daily_growth)
        starting_total = max(100000, starting_total)

        # Linear growth with small realistic daily variance
        for day_index in range(days):
            date = datetime.utcnow() - timedelta(days=(days - day_index - 1))

            # Linear growth with ±5% daily variance
            daily_variance = random.randint(-8, 8)
            vehicles_at_date = starting_total + (day_index * base_daily_growth) + daily_variance

            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'total_vehicles': int(vehicles_at_date),
                'new_vehicles': base_daily_growth + daily_variance,
                'timestamp': date.isoformat()
            })

        logger.info(f"Generated {len(historical_data)} data points from {historical_data[0]['date']} to {historical_data[-1]['date']}")
        return historical_data


# Singleton instance
dimo_client = DIMOClient()
