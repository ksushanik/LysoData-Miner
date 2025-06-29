import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { CompareContext } from '../context/CompareContext';

export default function CompareBar() {
  const { selected, clear } = useContext(CompareContext);
  const navigate = useNavigate();

  if (selected.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-3 rounded shadow-lg flex items-center space-x-3 z-50">
      <span>{selected.length} шт.</span>
      <button
        onClick={() => navigate('/compare')}
        className="bg-white text-blue-600 font-semibold px-3 py-1 rounded hover:bg-gray-100"
      >
        Сравнить
      </button>
      <button
        onClick={clear}
        className="text-sm opacity-80 hover:opacity-100"
      >
        Очистить
      </button>
    </div>
  );
} 