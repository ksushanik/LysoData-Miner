import React, { useEffect, useState } from 'react';
import { Beaker, ClipboardList, Dna, FileText, FlaskConical, HardDrive, Library, LocateFixed, LucideProps, Network, PencilRuler, Microscope, GitBranch, Archive } from 'lucide-react';
import { getDashboardStats } from '@/services/api';
import StatCard from '@/components/StatCard';
import NavCard from '@/components/NavCard';

interface Stats {
  total_species: number;
  total_strains: number;
  total_test_results: number;
  total_categories: number;
  total_sources: number;
  total_collection_numbers: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getDashboardStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statItems: {
    title: string;
    value: keyof Stats;
    Icon: React.ForwardRefExoticComponent<Omit<LucideProps, "ref"> & React.RefAttributes<SVGSVGElement>>;
    colorClass: string;
  }[] = [
    { title: 'Всего видов', value: 'total_species', Icon: Dna, colorClass: 'border-blue-500' },
    { title: 'Всего штаммов', value: 'total_strains', Icon: Microscope, colorClass: 'border-green-500' },
    { title: 'Результатов тестов', value: 'total_test_results', Icon: FileText, colorClass: 'border-indigo-500' },
    { title: 'Категорий тестов', value: 'total_categories', Icon: Library, colorClass: 'border-purple-500' },
    { title: 'Источников', value: 'total_sources', Icon: Archive, colorClass: 'border-yellow-500' },
    { title: 'Номеров в коллекциях', value: 'total_collection_numbers', Icon: GitBranch, colorClass: 'border-pink-500' },
  ];


  return (
    <div className="container mx-auto p-4 md:p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Обзор базы данных</h1>
        <p className="text-gray-500">Ключевые метрики и быстрый доступ к основным разделам системы.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        {statItems.map(({ title, value, Icon, colorClass }) => (
          <StatCard
            key={title}
            title={title}
            value={loading || stats === null ? undefined : stats[value]}
            Icon={Icon}
            colorClass={colorClass}
            loading={loading}
          />
        ))}
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Основные разделы</h2>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <NavCard 
                to="/strains"
                Icon={PencilRuler}
                title="Обзор штаммов"
                description="Поиск и фильтрация по всей базе данных штаммов."
                className="before:bg-sky-500"
            />
            <NavCard 
                to="/identify"
                Icon={LocateFixed}
                title="Идентификация штамма"
                description="Определение наиболее вероятных видов по результатам тестов."
                className="before:bg-teal-500"
            />
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 