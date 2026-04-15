import { ReactNode } from 'react';
import { AlertCircle, CheckCircle, Clock, Cpu, Brain } from 'lucide-react';

interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  color?: 'default' | 'success' | 'warning' | 'danger';
  trend?: 'up' | 'down' | 'neutral';
}

const iconMap = {
  default: <Clock className="h-6 w-6" />,
  success: <CheckCircle className="h-6 w-6" />,
  warning: <AlertCircle className="h-6 w-6" />,
  danger: <AlertCircle className="h-6 w-6" />,
};

const colorClasses = {
  default: 'bg-gray-800 border-gray-700',
  success: 'bg-green-900/30 border-green-800',
  warning: 'bg-yellow-900/30 border-yellow-800',
  danger: 'bg-red-900/30 border-red-800',
};

const trendColors = {
  up: 'text-green-400',
  down: 'text-red-400',
  neutral: 'text-gray-400',
};

export function StatusCard({
  title,
  value,
  subtitle,
  icon,
  color = 'default',
  trend,
}: StatusCardProps) {
  return (
    <div className={`glass-dark rounded-xl p-6 border ${colorClasses[color]} transition-all hover:scale-[1.02]`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-2">{title}</p>
          <div className="flex items-baseline gap-2">
            <h3 className="text-3xl font-bold">{value}</h3>
            {trend && (
              <span className={`text-sm font-medium ${trendColors[trend]}`}>
                {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-gray-500 text-sm mt-2">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-full ${color === 'default' ? 'bg-gray-800' : color === 'success' ? 'bg-green-900' : color === 'warning' ? 'bg-yellow-900' : 'bg-red-900'}`}>
          {icon || iconMap[color]}
        </div>
      </div>
    </div>
  );
}