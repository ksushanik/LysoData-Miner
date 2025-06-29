import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

interface NavCardProps {
  to: string;
  Icon: React.ElementType;
  title: string;
  description: string;
  className?: string;
}

const NavCard: React.FC<NavCardProps> = ({ to, Icon, title, description, className }) => {
  return (
    <Link
      to={to}
      className={`group relative block h-full overflow-hidden rounded-lg bg-white before:absolute before:inset-0 before:block before:translate-x-full before:transition before:duration-300 hover:before:translate-x-0 ${className}`}
    >
      <div className="relative flex h-full items-center justify-between border-2 border-gray-200 p-6 transition-colors group-hover:border-transparent group-hover:bg-gray-800 group-hover:text-white">
        <div className="flex items-center">
          <Icon className="mr-4 h-10 w-10 text-gray-600 transition-colors group-hover:text-white" />
          <div>
            <h3 className="text-xl font-bold">{title}</h3>
            <p className="text-sm text-gray-500 transition-colors group-hover:text-gray-300">{description}</p>
          </div>
        </div>
        <ArrowRight className="h-6 w-6 transform transition-transform duration-300 group-hover:translate-x-2" />
      </div>
    </Link>
  );
};

export default NavCard; 