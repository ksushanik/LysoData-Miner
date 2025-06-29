import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

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
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold italic text-gray-900">{decodedName}</h1>
        <Link to="/strains" className="text-blue-600 hover:text-blue-800">← Back to species</Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {strains.map((strain) => (
          <div key={strain.strain_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold text-gray-900">
                {strain.strain_identifier}
              </h3>
              <span className={`px-2 py-1 text-xs rounded-full ${
                strain.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {strain.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            {strain.common_name && (
              <p className="text-sm text-gray-600 mb-2">Common name: {strain.common_name}</p>
            )}

            {strain.description && (
              <p className="text-sm text-gray-600 line-clamp-3">{strain.description}</p>
            )}

            <div className="mt-4 pt-3 border-t border-gray-100">
              <Link to={`/strains/${strain.strain_id}`} state={{ scientificName: decodedName }} className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View Details →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 