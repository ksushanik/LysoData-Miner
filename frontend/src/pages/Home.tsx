export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to LysoData-Miner
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          A comprehensive database for Lysobacter bacterial strain identification and analysis
        </p>
        <div className="flex justify-center space-x-4">
          <a
            href="/strains"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Browse Strains
          </a>
          <a
            href="/identify"
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Identify Strain
          </a>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 py-12">
        <div className="text-center">
          <div className="bg-blue-100 rounded-lg p-4 mb-4 inline-block">
            <span className="text-2xl">🔬</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Comprehensive Database
          </h3>
          <p className="text-gray-600">
            Access detailed information about Lysobacter strains with comprehensive test results and characteristics.
          </p>
        </div>

        <div className="text-center">
          <div className="bg-green-100 rounded-lg p-4 mb-4 inline-block">
            <span className="text-2xl">🧪</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Smart Identification
          </h3>
          <p className="text-gray-600">
            Use laboratory test results to identify unknown strains with advanced matching algorithms.
          </p>
        </div>

        <div className="text-center">
          <div className="bg-purple-100 rounded-lg p-4 mb-4 inline-block">
            <span className="text-2xl">📊</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Scientific Analysis
          </h3>
          <p className="text-gray-600">
            Analyze morphological, physiological, and biochemical properties with confidence scores.
          </p>
        </div>
      </div>

      {/* Statistics Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Database Statistics
        </h2>
        <div className="grid md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">157+</div>
            <div className="text-gray-600">Bacterial Strains</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-green-600 mb-2">6</div>
            <div className="text-gray-600">Test Categories</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-purple-600 mb-2">40+</div>
            <div className="text-gray-600">Test Parameters</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-orange-600 mb-2">100%</div>
            <div className="text-gray-600">Scientific Accuracy</div>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div className="py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          About LysoData-Miner
        </h2>
        <div className="prose prose-lg text-gray-600">
          <p className="mb-4">
            LysoData-Miner is a modern web-based platform designed for researchers and microbiologists 
            working with Lysobacter bacterial strains. Our database provides comprehensive information 
            about strain characteristics, including morphological, physiological, and biochemical properties.
          </p>
          <p className="mb-4">
            The platform features an advanced identification system that allows users to input laboratory 
            test results and receive ranked matches with confidence scores, facilitating accurate strain 
            identification and classification.
          </p>
          <p>
            Built with modern web technologies and scientific rigor, LysoData-Miner serves as a valuable 
            resource for bacterial taxonomy, research, and biotechnological applications.
          </p>
        </div>
      </div>
    </div>
  )
} 