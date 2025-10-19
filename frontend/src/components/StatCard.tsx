/**
 * Stat Card Component - Displays key metrics
 */
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  className = '',
}) => {
  return (
    <div className={`bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
          <p className="text-3xl font-bold text-white mb-1">{value.toLocaleString()}</p>
          {subtitle && <p className="text-gray-500 text-sm">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="bg-primary-500 bg-opacity-20 p-3 rounded-lg">
            <Icon className="w-6 h-6 text-primary-400" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-4 flex items-center">
          <span
            className={`text-sm font-medium ${
              trend.isPositive ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value).toFixed(2)}%
          </span>
          <span className="text-gray-500 text-sm ml-2">vs last period</span>
        </div>
      )}
    </div>
  );
};
