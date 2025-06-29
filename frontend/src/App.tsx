import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import SpeciesBrowser from './pages/SpeciesBrowser'
import SpeciesDetail from './pages/SpeciesDetail'
import StrainDetail from './pages/StrainDetail'
import About from './pages/About'
import Identification from './pages/Identification'

function App() {
  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Identification />} />
          <Route path="/strains" element={<SpeciesBrowser />} />
          <Route path="/strains/species/:scientificName" element={<SpeciesDetail />} />
          <Route path="/strains/:strainId" element={<StrainDetail />} />
          <Route path="/identify" element={<Navigate to="/" replace />} />
          <Route path="/about" element={<About />} />
          <Route path="/identification" element={<Identification />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App; 