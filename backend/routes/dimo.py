"""
DIMO API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from data.dimo_client import dimo_client
from data.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dimo", tags=["DIMO"])


@router.get("/metrics")
async def get_network_metrics() -> Dict[str, Any]:
    """
    Get current DIMO network metrics

    Returns:
        Dictionary containing current network statistics
    """
    try:
        logger.info("Fetching DIMO network metrics...")
        stats = dimo_client.get_network_stats()

        if not stats:
            raise HTTPException(status_code=500, detail="Failed to fetch network metrics")

        # Store in database (non-blocking)
        try:
            db.store_network_metrics(stats)
        except Exception as e:
            logger.warning(f"Failed to store metrics in database: {e}")

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Error in get_network_metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(days: int = 90) -> Dict[str, Any]:
    """
    Get historical network data

    Args:
        days: Number of days of historical data (default 90)

    Returns:
        Dictionary containing historical metrics
    """
    try:
        logger.info(f"Fetching {days} days of historical data...")

        # Try to get from database first
        historical_data = db.get_historical_data(days=days)

        # If no data in DB, generate simulated data
        if not historical_data:
            logger.info("No historical data in database, generating simulated data...")
            historical_data = dimo_client.get_historical_data_simulation(days=days)

            # Store for future use (non-blocking)
            try:
                db.store_historical_data(historical_data)
            except Exception as e:
                logger.warning(f"Failed to store historical data: {e}")

        return {
            "success": True,
            "data": historical_data,
            "count": len(historical_data)
        }

    except Exception as e:
        logger.error(f"Error in get_historical_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for DIMO API connection

    Returns:
        Connection status and basic info
    """
    try:
        # Try to get total vehicles count
        total_vehicles = dimo_client.get_total_vehicles()

        return {
            "success": True,
            "status": "connected" if total_vehicles is not None else "limited",
            "total_vehicles": total_vehicles,
            "message": "DIMO API connection healthy" if total_vehicles else "Using fallback data"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "error",
            "message": str(e)
        }
