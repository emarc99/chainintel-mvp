/**
 * ChainIntel Dashboard - Main Page
 * Displays DIMO network metrics and ML-powered growth forecasts
 */
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Activity, TrendingUp, Zap, BarChart3 } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { StatCard } from '@/components/StatCard';
import { LineChart } from '@/components/LineChart';
import { LoadingSpinner } from '@/components/LoadingSpinner';

interface NetworkMetrics {
  total_vehicles: number;
  timestamp: string;
  top_makes: Record<string, number>;
}

interface HistoricalDataPoint {
  date: string;
  total_vehicles: number;
  new_vehicles: number;
}

interface ForecastPrediction {
  date: string;
  predicted_vehicles: number;
  lower_bound: number;
  upper_bound: number;
}

interface ForecastData {
  current_vehicles: number;
  current_date: string;
  predictions: ForecastPrediction[];
  growth_metrics: {
    '30_day': { predicted_vehicles: number; growth_percentage: number };
    '90_day': { predicted_vehicles: number; growth_percentage: number };
    '180_day': { predicted_vehicles: number; growth_percentage: number };
  };
  avg_daily_growth: number;
}

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [networkMetrics, setNetworkMetrics] = useState<NetworkMetrics | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load network metrics and historical data in parallel
      const [metricsRes, historicalRes] = await Promise.all([
        apiClient.getNetworkMetrics(),
        apiClient.getHistoricalData(90),
      ]);

      if (metricsRes.success) {
        setNetworkMetrics(metricsRes.data);
      }

      if (historicalRes.success) {
        setHistoricalData(historicalRes.data);
      }

      // Try to load latest forecast
      const forecastRes = await apiClient.getLatestForecast();
      if (forecastRes.success && forecastRes.data) {
        setForecastData(forecastRes.data.predictions || forecastRes.data);
      }

      setLoading(false);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
      setLoading(false);
    }
  };

  const generateForecast = async () => {
    try {
      setForecastLoading(true);
      setError(null);

      const response = await apiClient.generateForecast(180);

      if (response.success) {
        setForecastData(response.forecast);
      } else {
        setError('Failed to generate forecast');
      }

      setForecastLoading(false);
    } catch (err: any) {
      console.error('Error generating forecast:', err);
      setError(err.message || 'Failed to generate forecast');
      setForecastLoading(false);
    }
  };

  // Calculate growth rate from historical data
  const calculateGrowthRate = () => {
    if (historicalData.length < 2) return { daily: 0, percentage: 0 };

    const last7Days = historicalData.slice(-7);
    const prev7Days = historicalData.slice(-14, -7);

    if (last7Days.length === 0 || prev7Days.length === 0) return { daily: 0, percentage: 0 };

    const lastWeekAvg = last7Days.reduce((sum, d) => sum + d.total_vehicles, 0) / last7Days.length;
    const prevWeekAvg = prev7Days.reduce((sum, d) => sum + d.total_vehicles, 0) / prev7Days.length;

    const dailyGrowth = (lastWeekAvg - prevWeekAvg) / 7;
    const percentageGrowth = ((lastWeekAvg - prevWeekAvg) / prevWeekAvg) * 100;

    return { daily: Math.round(dailyGrowth), percentage: percentageGrowth };
  };

  const growthRate = calculateGrowthRate();

  // Prepare chart data
  const historicalChartData = {
    labels: historicalData.map((d) => d.date),
    datasets: [
      {
        label: 'Total Vehicles',
        data: historicalData.map((d) => d.total_vehicles),
        borderColor: 'rgb(14, 165, 233)',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        fill: true,
      },
    ],
  };

  // Prepare forecast chart data
  const forecastChartData = forecastData
    ? {
        labels: [
          ...historicalData.slice(-30).map((d) => d.date),
          ...forecastData.predictions.slice(0, 90).map((p) => p.date),
        ],
        datasets: [
          {
            label: 'Historical',
            data: [
              ...historicalData.slice(-30).map((d) => d.total_vehicles),
              ...Array(90).fill(null),
            ],
            borderColor: 'rgb(14, 165, 233)',
            backgroundColor: 'rgba(14, 165, 233, 0.1)',
            fill: true,
          },
          {
            label: 'Forecast',
            data: [
              ...Array(30).fill(null),
              forecastData.current_vehicles,
              ...forecastData.predictions.slice(0, 89).map((p) => p.predicted_vehicles),
            ],
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            fill: true,
            borderDash: [5, 5],
          },
          {
            label: 'Upper Bound',
            data: [
              ...Array(30).fill(null),
              forecastData.current_vehicles,
              ...forecastData.predictions.slice(0, 89).map((p) => p.upper_bound),
            ],
            borderColor: 'rgba(34, 197, 94, 0.3)',
            backgroundColor: 'rgba(34, 197, 94, 0.05)',
            fill: false,
            borderDash: [2, 2],
            pointRadius: 0,
          },
        ],
      }
    : null;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <LoadingSpinner message="Loading ChainIntel Dashboard..." size="lg" />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>ChainIntel - DePIN Analytics Platform</title>
        <meta
          name="description"
          content="AI-powered analytics for DePIN infrastructure"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-900">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-900 to-primary-700 border-b border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-white mb-2">ChainIntel</h1>
                <p className="text-primary-100 text-lg">
                  AI-Powered Analytics for DePIN Infrastructure
                </p>
              </div>
              <div className="flex items-center space-x-2 bg-primary-800 bg-opacity-50 px-4 py-2 rounded-lg">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-primary-100 text-sm">Live Data</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {error && (
            <div className="mb-6 bg-red-900 bg-opacity-20 border border-red-500 rounded-lg p-4">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total Vehicles"
              value={networkMetrics?.total_vehicles || 0}
              subtitle="Connected to DIMO"
              icon={Activity}
            />
            <StatCard
              title="Daily Growth"
              value={growthRate.daily}
              subtitle="New vehicles/day"
              icon={TrendingUp}
              trend={{
                value: growthRate.percentage,
                isPositive: growthRate.percentage > 0,
              }}
            />
            <StatCard
              title="Network Status"
              value="Growing"
              subtitle="Healthy expansion"
              icon={Zap}
            />
            <StatCard
              title="Analytics Active"
              value="1"
              subtitle="ML model running"
              icon={BarChart3}
            />
          </div>

          {/* Historical Chart */}
          <div className="mb-8">
            <LineChart
              title="DIMO Network Growth (Last 90 Days)"
              labels={historicalChartData.labels}
              datasets={historicalChartData.datasets}
              height={350}
            />
          </div>

          {/* Forecast Section */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700 mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  ML-Powered Growth Forecast
                </h2>
                <p className="text-gray-400">
                  Prophet time-series forecasting model predicting 6-month network growth
                </p>
              </div>
              <button
                onClick={generateForecast}
                disabled={forecastLoading}
                className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                {forecastLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <BarChart3 className="w-5 h-5" />
                    <span>Generate Forecast</span>
                  </>
                )}
              </button>
            </div>

            {forecastData ? (
              <>
                {/* Forecast Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-700 bg-opacity-50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm mb-1">30-Day Forecast</p>
                    <p className="text-2xl font-bold text-white">
                      {forecastData.growth_metrics['30_day'].predicted_vehicles.toLocaleString()}
                    </p>
                    <p className="text-green-400 text-sm mt-1">
                      +{forecastData.growth_metrics['30_day'].growth_percentage.toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-700 bg-opacity-50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm mb-1">90-Day Forecast</p>
                    <p className="text-2xl font-bold text-white">
                      {forecastData.growth_metrics['90_day'].predicted_vehicles.toLocaleString()}
                    </p>
                    <p className="text-green-400 text-sm mt-1">
                      +{forecastData.growth_metrics['90_day'].growth_percentage.toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-700 bg-opacity-50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm mb-1">180-Day Forecast</p>
                    <p className="text-2xl font-bold text-white">
                      {forecastData.growth_metrics['180_day'].predicted_vehicles.toLocaleString()}
                    </p>
                    <p className="text-green-400 text-sm mt-1">
                      +{forecastData.growth_metrics['180_day'].growth_percentage.toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Forecast Chart */}
                {forecastChartData && (
                  <LineChart
                    title="Historical Data + 90-Day ML Forecast"
                    labels={forecastChartData.labels}
                    datasets={forecastChartData.datasets}
                    height={350}
                  />
                )}

                {/* Key Insights */}
                <div className="mt-6 bg-primary-900 bg-opacity-20 border border-primary-700 rounded-lg p-4">
                  <h3 className="text-white font-semibold mb-2">Key Insights</h3>
                  <ul className="space-y-2 text-gray-300 text-sm">
                    <li>
                      ✓ Average daily growth rate: <span className="text-primary-400 font-semibold">{forecastData.avg_daily_growth}</span> vehicles
                    </li>
                    <li>
                      ✓ Projected to reach <span className="text-primary-400 font-semibold">{forecastData.growth_metrics['90_day'].predicted_vehicles.toLocaleString()}</span> vehicles in 3 months
                    </li>
                    <li>
                      ✓ 90% confidence interval shown in forecast chart
                    </li>
                    <li>
                      ✓ Model trained on 90 days of historical network data
                    </li>
                  </ul>
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-400 mb-4">
                  No forecast available. Click the button above to generate ML predictions.
                </p>
              </div>
            )}
          </div>

          {/* Footer Info */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4">About This Dashboard</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-300">
              <div>
                <h4 className="font-semibold text-primary-400 mb-2">Data Source</h4>
                <p>
                  Live data from DIMO Network via GraphQL API. DIMO is a decentralized vehicle
                  network built on Polygon with 140,000+ connected vehicles.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-primary-400 mb-2">ML Technology</h4>
                <p>
                  Facebook Prophet time-series forecasting model with 90% confidence intervals.
                  Analyzes historical growth patterns to predict future network expansion.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-primary-400 mb-2">Tech Stack</h4>
                <p>
                  Next.js 14, TypeScript, Chart.js, Tailwind CSS (Frontend) | Python FastAPI,
                  Prophet ML, Supabase PostgreSQL (Backend)
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-primary-400 mb-2">ChainIntel Vision</h4>
                <p>
                  Building the Bloomberg Terminal for DePIN infrastructure. Wave 1 demonstrates
                  technical feasibility for Polygon Buildathon.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
