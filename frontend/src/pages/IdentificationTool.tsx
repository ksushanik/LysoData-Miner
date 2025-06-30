import { useState, useEffect, useMemo } from 'react'

interface TestCategory {
  category_id: number
  category_name: string
  description: string
  sort_order: number
}

interface TestValue {
  value_id: number;
  value_code: string;
  value_name: string;
}

interface Test {
  test_id: number
  test_name: string
  test_type: 'boolean' | 'numeric' | 'text'
  category_id: number
  description?: string
  possible_values?: TestValue[]
}

interface TestOption {
  value_id: string | number;
  display_value: string;
}

interface MatchDetail {
    test_name: string;
    strain_result: string | null;
    query_result: string;
    match_status: 'match' | 'mismatch' | 'not_found';
}

interface IdentificationResult {
    strain: {
        strain_id: number;
        strain_identifier: string;
        scientific_name: string;
    };
    score: number;
    match_count: number;
    mismatch_count: number;
    query_test_count: number;
    details: MatchDetail[];
}

export default function IdentificationTool() {
  const [categories, setCategories] = useState<TestCategory[]>([])
  const [tests, setTests] = useState<Test[]>([])
  const [testOptions, setTestOptions] = useState<Record<number, TestOption[]>>({})
  const [testResults, setTestResults] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)
  const [identifying, setIdentifying] = useState(false)
  const [results, setResults] = useState<IdentificationResult[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        const categoriesResponse = await fetch('/api/tests/categories')
        if (!categoriesResponse.ok) throw new Error(`Failed to fetch categories: ${categoriesResponse.statusText}`)
        const categoriesData = await categoriesResponse.json()
        setCategories(categoriesData.categories || [])

        const testsResponse = await fetch('/api/tests/')
        if (!testsResponse.ok) throw new Error(`Failed to fetch tests: ${testsResponse.statusText}`)
        const testsData = await testsResponse.json()
        const fetchedTests = testsData.tests || []
        setTests(fetchedTests)

        // Fetch options for non-boolean tests
        const optionsPromises = fetchedTests
          .filter((test: Test) => test.test_type === 'numeric' || test.test_type === 'text')
          .map((test: Test) => 
            fetch(`/api/tests/${test.test_id}/options`)
              .then(res => res.ok ? res.json() : Promise.resolve({ options: [] }))
              .then(data => ({ test_id: test.test_id, options: data.options }))
          );
        
        const allOptions = await Promise.all(optionsPromises);
        const optionsMap = allOptions.reduce((acc, { test_id, options }) => {
          acc[test_id] = options;
          return acc;
        }, {} as Record<number, TestOption[]>);
        setTestOptions(optionsMap);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleTestResultChange = (testId: number, value: string) => {
    setTestResults(prev => ({
      ...prev,
      [testId]: value
    }))
  }

  const handleIdentify = async () => {
    if (Object.keys(testResults).length === 0) {
      setError('Please provide at least one test result')
      return
    }

    setIdentifying(true)
    setError(null)

    try {
      const response = await fetch('/api/identification/identify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_results: testResults,
          limit: 20
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResults(data.matches || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Identification failed')
    } finally {
      setIdentifying(false)
    }
  }

  const clearResults = () => {
    setTestResults({})
    setResults([])
    setError(null)
  }

  const groupedAndSortedTests = useMemo(() => {
    const grouped: Record<number, Test[]> = {};
    for (const test of tests) {
        if (!grouped[test.category_id]) {
            grouped[test.category_id] = [];
        }
        grouped[test.category_id].push(test);
    }
    return grouped;
  }, [tests]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading identification tool...</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Strain Identification Tool</h1>
        <p className="text-gray-600">
          Enter your laboratory test results to identify potential strain matches
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Test Input Form */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Laboratory Test Results</h2>
            
            {categories.map(category => {
              const categoryTests = groupedAndSortedTests[category.category_id] || [];
              if (categoryTests.length === 0) return null

              return (
                <div key={category.category_id} className="mb-6">
                  <h3 className="text-lg font-medium text-gray-800 mb-3">
                    {category.description}
                  </h3>
                  
                  <div className="space-y-3">
                    {categoryTests.map(test => {
                      const options = test.test_type === 'boolean' 
                        ? test.possible_values
                        : testOptions[test.test_id];

                      return (
                        <div key={test.test_id} className="flex items-center justify-between py-2">
                          <label className="text-sm font-medium text-gray-700 flex-1">
                            {test.test_name}
                            {test.description && (
                              <span className="text-gray-500 text-xs block">
                                {test.description}
                              </span>
                            )}
                          </label>
                          
                          <div className="ml-4 w-48">
                            <select
                              value={testResults[test.test_id] || ''}
                              onChange={(e) => handleTestResultChange(test.test_id, e.target.value)}
                              className="w-full border border-gray-300 rounded px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                              <option value="">Select...</option>
                              {test.test_type === 'boolean' ? (
                                test.possible_values?.map(value => (
                                  <option key={value.value_id} value={value.value_code}>
                                    {value.value_name}
                                  </option>
                                ))
                              ) : (
                                options?.map(option => (
                                  <option key={option.value_id} value={option.value_id}>
                                    {option.display_value}
                                  </option>
                                ))
                              )}
                            </select>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
            
            <div className="flex space-x-4 pt-4 border-t border-gray-200">
              <button
                onClick={handleIdentify}
                disabled={identifying || Object.keys(testResults).length === 0}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {identifying ? 'Identifying...' : 'Identify Strain'}
              </button>
              
              <button
                onClick={clearResults}
                className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 min-h-[500px]">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Identification Results</h2>
            
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">{error}</p>
              </div>
            )}
            
            {identifying && (
                <div className="text-center p-8">
                    <p>Identifying, please wait...</p>
                </div>
            )}

            {!identifying && results.length === 0 && !error && (
              <div className="text-center p-8">
                <p className="text-gray-500">Results will appear here.</p>
              </div>
            )}

            {!identifying && results.length > 0 && (
              <div className="space-y-4">
                {results.map(result => (
                  <div key={result.strain.strain_id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                        <a href={`/strains/${result.strain.strain_id}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            <h3 className="text-lg font-bold">{result.strain.strain_identifier}</h3>
                            <p className="text-sm italic text-gray-600">{result.strain.scientific_name}</p>
                        </a>
                        <div className="text-right">
                            <p className="text-xl font-bold text-green-600">{(result.score * 100).toFixed(1)}%</p>
                            <p className="text-xs text-gray-500">Match Score</p>
                        </div>
                    </div>
                    <div className="text-xs mt-2 space-x-4">
                        <span>Matches: <span className="font-semibold">{result.match_count}/{result.query_test_count}</span></span>
                        <span>Mismatches: <span className="font-semibold">{result.mismatch_count}</span></span>
                    </div>
                  </div>
                ))}
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  )
} 