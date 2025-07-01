import { useEffect, useState } from 'react'
import { getDashboardStats } from '@/services/api'

export interface DashboardStats {
  total_species: number
  total_strains: number
  total_test_results: number
  total_categories: number
  total_sources: number
  total_collection_numbers: number
}

/**
 * Хук запрашивает статистику и кэширует её в памяти,
 * чтобы избежать лишних запросов при множественных компонентах.
 */
export const useStats = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats()
        if (isMounted) {
          setStats(data)
        }
      } catch (e: any) {
        if (isMounted) setError(e.message || 'Ошибка получения статистики')
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    fetchStats()
    return () => {
      isMounted = false
    }
  }, [])

  return { stats, loading, error }
} 