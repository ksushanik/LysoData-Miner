import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface Species {
  scientific_name: string
  strain_count: number
}

export default function SpeciesBrowser() {
  const [speciesList, setSpeciesList] = useState<Species[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchSpecies = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/species')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setSpeciesList(data.species)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setSpeciesList([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSpecies()
  }, [])

  const filteredSpecies = speciesList.filter((s) =>
    s.scientific_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading species...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-600">
        <h2 className="text-xl font-semibold mb-2">Error Loading Species</h2>
        <p>{error}</p>
        <button
          onClick={fetchSpecies}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Species Browser</h1>
        <p className="text-gray-600">Browse Lysobacter species in the database</p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search scientific name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Species grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredSpecies.map((sp) => (
          <Link
            key={sp.scientific_name}
            to={`/strains/species/${encodeURIComponent(sp.scientific_name)}`}
            className="block bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <h3 className="text-lg font-semibold text-gray-900 italic mb-2">
              {sp.scientific_name}
            </h3>
            <p className="text-sm text-gray-600">
              {sp.strain_count} strain{sp.strain_count !== 1 ? 's' : ''}
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
} 