export default function About() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">About LysoData-Miner</h1>
        <p className="text-xl text-gray-600">
          A comprehensive database system for Lysobacter bacterial strain identification and analysis
        </p>
      </div>

      <div className="space-y-8">
        {/* Project Overview */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Project Overview</h2>
          <div className="prose prose-lg text-gray-600 space-y-4">
            <p>
              LysoData-Miner is a modern, web-based platform designed specifically for researchers 
              and microbiologists working with <em>Lysobacter</em> bacterial strains. This system 
              provides a comprehensive database of strain characteristics, including detailed 
              morphological, physiological, and biochemical properties.
            </p>
            <p>
              The platform features an advanced identification algorithm that enables users to 
              input laboratory test results and receive ranked strain matches with confidence 
              scores, facilitating accurate bacterial identification and classification.
            </p>
          </div>
        </section>

        {/* Technical Information */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Technical Information</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Backend Technology</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  FastAPI (Python web framework)
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  PostgreSQL database with optimized schema
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  SQLAlchemy 2.0 with async support
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Frontend Technology</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-3"></span>
                  React 18 with TypeScript
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-3"></span>
                  Vite for fast development
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-3"></span>
                  Tailwind CSS for styling
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
} 