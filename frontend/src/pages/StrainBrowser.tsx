import { useState, useEffect, useContext } from 'react'
import { Link } from 'react-router-dom'
import { CompareContext } from '../context/CompareContext'

interface Strain {
  strain_id: number
  strain_identifier: string
  scientific_name: string
  common_name: string
  description?: string
  isolation_source?: string
  isolation_location?: string
  isolation_date?: string
  gc_content_range?: string
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

export default function StrainBrowser() {
  const [strains, setStrains] = useState<Strain[]>([])
  const [pagination, setPagination] = useState<PaginationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(0)
  const { selected, toggle } = useContext(CompareContext)

  const fetchStrains = async (page = 0, search = '') => {
    setLoading(true)
    try {
      const searchParams = new URLSearchParams({
        skip: (page * 20).toString(),
        limit: '20'
      })
      
      if (search) {
        searchParams.append('search', search)
      }

      const response = await fetch(`http://localhost:8000/api/strains/?${searchParams}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data: StrainResponse = await response.json()
      setStrains(data.strains)
      setPagination(data.pagination)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setStrains([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStrains(currentPage, searchTerm)
  }, [currentPage, searchTerm])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setCurrentPage(0)
    fetchStrains(0, searchTerm)
  }

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage)
    window.scrollTo(0, 0)
  }

  if (loading && strains.length === 0) {
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
        <button 
          onClick={() => fetchStrains(currentPage, searchTerm)}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Strain Browser</h1>
          <p className="text-gray-600">
            Browse and search through the Lysobacter strain database
          </p>
        </div>
        <Link to="/strains/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">+ Новый штамм</Link>
      </div>

      {/* Search Form */}
      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <input
            type="text"
            placeholder="Search by strain identifier, scientific name, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </form>
      </div>

      {/* Results Info */}
      {pagination && (
        <div className="mb-4 text-sm text-gray-600">
          Showing {pagination.skip + 1}-{Math.min(pagination.skip + pagination.limit, pagination.total)} of {pagination.total} strains
        </div>
      )}

      {/* Strains Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {strains.map((strain) => (
          <div key={strain.strain_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold text-gray-900">
                {strain.strain_identifier}
              </h3>
              <span className={`px-2 py-1 text-xs rounded-full ${
                strain.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {strain.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            
            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium text-gray-700">Scientific name:</span>
                <div className="text-gray-600 italic">{strain.scientific_name}</div>
              </div>
              
              {strain.common_name && (
                <div>
                  <span className="font-medium text-gray-700">Common name:</span>
                  <div className="text-gray-600">{strain.common_name}</div>
                </div>
              )}
              
              {strain.description && (
                <div>
                  <span className="font-medium text-gray-700">Description:</span>
                  <div className="text-gray-600">{strain.description}</div>
                </div>
              )}
              
              {strain.isolation_source && (
                <div>
                  <span className="font-medium text-gray-700">Source:</span>
                  <div className="text-gray-600">{strain.isolation_source}</div>
                </div>
              )}
              
              {strain.isolation_location && (
                <div>
                  <span className="font-medium text-gray-700">Location:</span>
                  <div className="text-gray-600">{strain.isolation_location}</div>
                </div>
              )}
            </div>
            
            <div className="mt-4 pt-3 border-t border-gray-100">
              <div className="flex items-center justify-between">
                <Link to={`/strains/${strain.strain_id}`} className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                  View Details →
                </Link>
                <button
                  onClick={() => toggle(strain.strain_id)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {selected.includes(strain.strain_id) ? '− Убрать' : '+ В сравнение'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {pagination && pagination.total > pagination.limit && (
        <div className="mt-8 flex justify-center items-center space-x-2">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={!pagination.has_previous}
            className="px-3 py-1 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          
          <span className="px-4 py-1 text-sm text-gray-600">
            Page {currentPage + 1} of {Math.ceil(pagination.total / pagination.limit)}
          </span>
          
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={!pagination.has_next}
            className="px-3 py-1 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
} 