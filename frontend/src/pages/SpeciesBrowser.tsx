import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchSpecies as fetchSpeciesAPI } from '../services/api'

interface Species {
  scientific_name: string | null
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
      const data = await fetchSpeciesAPI()
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
    s.scientific_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-muted-foreground">Loading species...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-destructive">
        <h2 className="text-xl font-semibold mb-2">Error Loading Species</h2>
        <p>{error}</p>
        <button
          onClick={fetchSpecies}
          className="mt-4 bg-primary text-primary-foreground px-4 py-2 rounded hover:bg-primary/90"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4">
      <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-1">Species Browser</h1>
          <p className="text-muted-foreground">Browse all Lysobacter species in the database.</p>
        </div>
        <Link 
          to="/strains/new" 
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
        >
          + Add New Strain
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by scientific name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-border bg-background rounded-lg focus:ring-1 focus:ring-primary focus:border-primary"
        />
      </div>

      {/* Species grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredSpecies.map((sp, index) => (
          <Link
            key={sp.scientific_name || `unknown-${index}`}
            to={`/strains/species/${encodeURIComponent(sp.scientific_name || 'unknown')}`}
            className="block bg-white rounded-lg shadow-sm border border-border p-6 hover:shadow-md hover:border-primary/50 transition-all"
          >
            <h3 className="text-lg font-semibold text-foreground italic mb-2">
              {sp.scientific_name || 'Unknown species'}
            </h3>
            <p className="text-sm text-muted-foreground">
              {sp.strain_count} strain{sp.strain_count !== 1 ? 's' : ''} available
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
} 