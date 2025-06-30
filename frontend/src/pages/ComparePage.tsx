import { useContext, useEffect, useState } from 'react'
import { CompareContext } from '../context/CompareContext'
import { Link } from 'react-router-dom'

interface TestEntry { test_name: string; result: string; category?: string }
interface StrainData {
  strain_id: number
  strain_identifier: string
  scientific_name: string
  test_results: TestEntry[]
}

export default function ComparePage() {
  const { selected, remove, clear } = useContext(CompareContext)
  const [strains, setStrains] = useState<StrainData[]>([])
  const [loading, setLoading] = useState(true)
  const [showDiffOnly, setShowDiffOnly] = useState(false)

  useEffect(() => {
    const fetchBatch = async () => {
      if (selected.length < 2) return;
      setLoading(true)
      try {
        const res = await fetch('/api/strains/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ strain_ids: selected })
        })
        const data = await res.json()
        setStrains(data.strains)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchBatch()
  }, [selected])

  if (selected.length < 2) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">Сравнение штаммов</h1>
        <p>Добавьте минимум два штамма для сравнения.</p>
        <Link to="/strains" className="text-blue-600">← Назад</Link>
      </div>
    )
  }

  if (loading) return <p>Загрузка данных…</p>

  // Собираем уникальный список характеристик
  const allTests = new Map<string, { category?: string; values: (string|null)[] }>()
  strains.forEach((s, idx) => {
    s.test_results.forEach(tr => {
      const key = tr.test_name
      if (!allTests.has(key)) {
        allTests.set(key, { category: tr.category, values: Array(strains.length).fill(null) })
      }
      allTests.get(key)!.values[idx] = tr.result
    })
  })

  // Фильтрация различий
  const entries = Array.from(allTests.entries()).filter(([_, info]) => {
    if (!showDiffOnly) return true
    const values = info.values
    // Consider null vs non-null as отличие. Различие есть, если не все элементы равны друг другу.
    const first = values[0]
    return values.some((v) => v !== first)
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Сравнение штаммов</h1>

      <div className="mb-4 flex items-center space-x-4">
        <label className="flex items-center space-x-2">
          <input type="checkbox" checked={showDiffOnly} onChange={() => setShowDiffOnly(!showDiffOnly)} />
          <span>Показывать только различия</span>
        </label>
        <button onClick={clear} className="text-sm text-red-600">Очистить</button>
      </div>

      <div className="overflow-auto">
        <table className="min-w-full border">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2 border" />
              {strains.map(s => (
                <th key={s.strain_id} className="p-2 border text-left">
                  {s.strain_identifier}
                  <button onClick={() => remove(s.strain_id)} className="ml-2 text-xs text-red-600">×</button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {entries.map(([test, info]) => (
              <tr key={test}>
                <td className="p-2 border whitespace-nowrap text-sm font-medium">{test}</td>
                {info.values.map((val, i) => (
                  <td key={i} className="p-2 border text-sm">{val ?? 'n.d.'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
} 