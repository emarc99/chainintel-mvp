"""
Analytics and ML Forecasting Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from models.forecaster import forecaster
from data.dimo_client import dimo_client
from data.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.post("/forecast")
async def generate_forecast(
    days_ahead: int = 180,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Generate network growth forecast using ML model

    Args:
        days_ahead: Number of days to forecast (default 180)

    Returns:
        Dictionary containing forecast results
    """
    try:
        logger.info(f"Generating {days_ahead}-day forecast...")

        # Get historical data
        historical_data = db.get_historical_data(days=90)

        # If no data in DB, get simulated data
        if not historical_data:
            logger.info("No historical data in database, using simulated data...")
            historical_data = dimo_client.get_historical_data_simulation(days=90)

        if not historical_data:
            raise HTTPException(status_code=500, detail="No historical data available")

        # Train model
        success = forecaster.train_model(historical_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to train forecasting model")

        # Generate forecast
        forecast_result = forecaster.generate_forecast(days_ahead=days_ahead)

        if not forecast_result:
            raise HTTPException(status_code=500, detail="Failed to generate forecast")

        # Validate model
        validation_metrics = forecaster.validate_model(test_size=14)

        # Get trend analysis
        trend_analysis = forecaster.get_trend_analysis()

        # Store forecast in database (background task)
        if background_tasks:
            background_tasks.add_task(db.store_forecast, forecast_result)

        return {
            "success": True,
            "forecast": forecast_result,
            "validation": validation_metrics,
            "trend_analysis": trend_analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/latest")
async def get_latest_forecast() -> Dict[str, Any]:
    """
    Get the most recent forecast from database

    Returns:
        Latest forecast data
    """
    try:
        logger.info("Retrieving latest forecast...")

        forecast = db.get_latest_forecast()

        if not forecast:
            return {
                "success": False,
                "message": "No forecast available. Generate a new forecast using POST /api/analytics/forecast"
            }

        return {
            "success": True,
            "data": forecast
        }

    except Exception as e:
        logger.error(f"Error in get_latest_forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/growth-rate")
async def get_growth_rate() -> Dict[str, Any]:
    """
    Calculate current network growth rate

    Returns:
        Growth rate metrics
    """
    try:
        logger.info("Calculating growth rate...")

        # Get last 30 days of data
        historical_data = db.get_historical_data(days=30)

        if not historical_data:
            historical_data = dimo_client.get_historical_data_simulation(days=30)

        if not historical_data or len(historical_data) < 2:
            raise HTTPException(status_code=500, detail="Insufficient data for growth rate calculation")

        # Calculate metrics
        first_day = historical_data[0]
        last_day = historical_data[-1]
        total_growth = last_day['total_vehicles'] - first_day['total_vehicles']
        days_span = len(historical_data)

        avg_daily_growth = total_growth / days_span if days_span > 0 else 0
        growth_percentage = (total_growth / first_day['total_vehicles']) * 100 if first_day['total_vehicles'] > 0 else 0

        # Calculate week-over-week growth
        if len(historical_data) >= 14:
            last_week = historical_data[-7:]
            prev_week = historical_data[-14:-7]

            last_week_avg = sum(d['total_vehicles'] for d in last_week) / 7
            prev_week_avg = sum(d['total_vehicles'] for d in prev_week) / 7
            wow_growth = ((last_week_avg - prev_week_avg) / prev_week_avg) * 100 if prev_week_avg > 0 else 0
        else:
            wow_growth = 0

        result = {
            "time_period": f"{days_span} days",
            "start_date": first_day['date'],
            "end_date": last_day['date'],
            "start_vehicles": first_day['total_vehicles'],
            "end_vehicles": last_day['total_vehicles'],
            "total_growth": total_growth,
            "growth_percentage": round(growth_percentage, 2),
            "avg_daily_growth": round(avg_daily_growth, 2),
            "week_over_week_growth": round(wow_growth, 2)
        }

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_growth_rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    """
    Get comprehensive analytics summary

    Returns:
        Summary of all analytics insights
    """
    try:
        logger.info("Generating analytics summary...")

        # Get current metrics
        current_metrics = dimo_client.get_network_stats()

        # Get latest forecast
        latest_forecast = db.get_latest_forecast()

        # Get growth rate
        historical_data = db.get_historical_data(days=30)
        if not historical_data:
            historical_data = dimo_client.get_historical_data_simulation(days=30)

        growth_metrics = {}
        if historical_data and len(historical_data) >= 2:
            first_day = historical_data[0]
            last_day = historical_data[-1]
            total_growth = last_day['total_vehicles'] - first_day['total_vehicles']
            growth_metrics = {
                "avg_daily_growth": round(total_growth / len(historical_data), 2),
                "total_30day_growth": total_growth
            }

        summary = {
            "current_network": {
                "total_vehicles": current_metrics.get('total_vehicles', 0),
                "timestamp": current_metrics.get('timestamp'),
                "top_makes": current_metrics.get('top_makes', {}),
            },
            "growth": growth_metrics,
            "forecast_available": latest_forecast is not None,
            "last_updated": current_metrics.get('timestamp')
        }

        return {
            "success": True,
            "data": summary
        }

    except Exception as e:
        logger.error(f"Error in get_analytics_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
