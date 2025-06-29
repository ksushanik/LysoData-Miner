import { useEffect, useState } from 'react';
import { getDashboardStats } from '../services/api';
import { Server, Dna, TestTube2, Shapes, Library } from 'lucide-react';

interface Stats {
  total_species: number;
  total_strains: number;
  total_test_results: number;
  total_categories: number;
  total_sources: number;
}

interface StatCardProps {
    icon: React.ReactNode;
    title: string;
    value: number | undefined | null;
    colorClass: string;
}

const StatCard = ({ icon, title, value, colorClass }: StatCardProps) => (
    <div className={`bg-white p-6 rounded-lg shadow-lg flex items-center space-x-4 border-l-4 ${colorClass}`}>
        <div className="text-3xl">{icon}</div>
        <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold">{value !== null && value !== undefined ? value.toLocaleString() : '...'}</p>
        </div>
    </div>
);

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getDashboardStats();
        setStats(data);
      } catch (err) {
        setError('Не удалось загрузить статистику.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (error) {
    return <div className="text-center text-red-500">{error}</div>;
  }

  return (
    <div className="p-4 md:p-8 bg-gray-50 min-h-full">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Обзор базы данных</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <StatCard 
                icon={<Dna className="text-blue-500" />} 
                title="Всего видов" 
                value={stats?.total_species} 
                colorClass="border-blue-500" 
            />
            <StatCard 
                icon={<TestTube2 className="text-green-500" />} 
                title="Всего штаммов" 
                value={stats?.total_strains} 
                colorClass="border-green-500"
            />
            <StatCard 
                icon={<Server className="text-indigo-500" />} 
                title="Результатов тестов" 
                value={stats?.total_test_results}
                colorClass="border-indigo-500"
            />
            <StatCard 
                icon={<Shapes className="text-purple-500" />} 
                title="Категорий тестов" 
                value={stats?.total_categories}
                colorClass="border-purple-500"
            />
             <StatCard 
                icon={<Library className="text-yellow-500" />} 
                title="Источников" 
                value={stats?.total_sources}
                colorClass="border-yellow-500"
            />
        </div>
    </div>
  );
} 