import { createContext, useEffect, useState, ReactNode } from 'react';

interface CompareContextType {
  selected: number[];
  add: (id: number) => void;
  remove: (id: number) => void;
  toggle: (id: number) => void;
  clear: () => void;
}

export const CompareContext = createContext<CompareContextType>({
  selected: [],
  add: () => {},
  remove: () => {},
  toggle: () => {},
  clear: () => {}
});

export const CompareProvider = ({ children }: { children: ReactNode }) => {
  const [selected, setSelected] = useState<number[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('compareStrains');
    if (stored) {
      try {
        setSelected(JSON.parse(stored));
      } catch {}
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('compareStrains', JSON.stringify(selected));
  }, [selected]);

  const add = (id: number) => {
    setSelected((prev) => (prev.includes(id) ? prev : [...prev, id]));
  };
  const remove = (id: number) => {
    setSelected((prev) => prev.filter((x) => x !== id));
  };
  const toggle = (id: number) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };
  const clear = () => setSelected([]);

  return (
    <CompareContext.Provider value={{ selected, add, remove, toggle, clear }}>
      {children}
    </CompareContext.Provider>
  );
}; 