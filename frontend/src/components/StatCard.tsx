import React from 'react';
import { LucideProps } from 'lucide-react';

interface StatCardProps {
  title: string;
  value?: number;
  Icon: React.ForwardRefExoticComponent<Omit<LucideProps, "ref"> & React.RefAttributes<SVGSVGElement>>;
  colorClass: string;
  loading: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, Icon, colorClass, loading }) => {
  return (
    <div className={`relative overflow-hidden rounded-lg border bg-white p-5 shadow-sm ${colorClass}`}>
      <div className="flex items-center">
        <div className={`mr-4 rounded-full bg-gray-100 p-3`}>
          <Icon className="h-6 w-6 text-gray-700" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-gray-500">{title}</p>
          {loading ? (
            <div className="mt-1 h-7 w-24 animate-pulse rounded-md bg-gray-200" />
          ) : (
            <p className="text-2xl font-bold text-gray-800">
              {value !== undefined ? value.toLocaleString() : '-'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatCard; 