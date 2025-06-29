import { useState, useEffect, useContext } from 'react'
import { useParams, Link } from 'react-router-dom'
import { CompareContext } from '../context/CompareContext'

interface Strain {
  strain_id: number
  strain_identifier: string
  scientific_name: string
  common_name: string
  description?: string
  is_active: boolean
}

interface PaginationData {
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_previous: boolean
}

interface StrainResponse {
  strains: Strain[]
  pagination: PaginationData
}

export default function SpeciesDetail() {
  const { scientificName } = useParams<{ scientificName: string }>()
  const decodedName = decodeURIComponent(scientificName || '')

  const [strains, setStrains] = useState<Strain[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { selected, toggle } = useContext(CompareContext)

  useEffect(() => {
    const fetchStrains = async () => {
      setLoading(true)
      try {
        const params = new URLSearchParams({ scientific_name: decodedName, limit: '100' })
        const response = await fetch(`http://localhost:8000/api/strains/?${params}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data: StrainResponse = await response.json()
        setStrains(data.strains)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
        setStrains([])
      } finally {
        setLoading(false)
      }
    }

    fetchStrains()
  }, [decodedName])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading strains...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-600">
        <h2 className="text-xl font-semibold mb-2">Error Loading Strains</h2>
        <p>{error}</p>
        <Link to="/strains" className="text-blue-600 hover:text-blue-800 mt-4 inline-block">
          Back to species list
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-4xl font-bold text-foreground">{decodedName}</h1>
        <Link to="/strains" className="text-sm font-medium text-primary hover:text-primary-dark transition-colors flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          Back to species
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {strains.map((strain) => (
          <div key={strain.strain_id} className="bg-white rounded-xl shadow-md border border-border p-6 flex flex-col transition-all duration-300 hover:shadow-lg hover:border-primary/50">
            <div className="flex-grow">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-bold text-foreground">
                  {strain.strain_identifier}
                </h3>
                <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                  strain.is_active ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground'
                }`}>
                  {strain.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              {strain.common_name && (
                <p className="text-sm text-muted-foreground mb-2">Common name: {strain.common_name}</p>
              )}

              {strain.description && (
                <p className="text-sm text-muted-foreground line-clamp-3">{strain.description}</p>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-border flex items-center justify-between">
              <Link to={`/strains/${strain.strain_id}`} state={{ scientificName: decodedName }} className="text-primary hover:text-primary-dark text-sm font-semibold transition-colors">
                View Details →
              </Link>
              <button
                onClick={() => toggle(strain.strain_id)}
                className="text-sm font-medium text-primary hover:text-primary-dark transition-colors"
              >
                {selected.includes(strain.strain_id) ? '− Убрать' : '+ В сравнение'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 