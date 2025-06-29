import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import SpeciesBrowser from './pages/SpeciesBrowser'
import SpeciesDetail from './pages/SpeciesDetail'
import StrainDetail from './pages/StrainDetail'
import About from './pages/About'
import Identification from './pages/Identification'
import ComparePage from './pages/ComparePage'
import CreateStrainPage from './pages/CreateStrainPage'
import EditStrainPage from './pages/EditStrainPage'

function App() {
  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Identification />} />
          <Route path="/strains" element={<SpeciesBrowser />} />
          <Route path="/strains/species/:scientificName" element={<SpeciesDetail />} />
          <Route path="/strains/:strainId" element={<StrainDetail />} />
          <Route path="/strains/new" element={<CreateStrainPage />} />
          <Route path="/strains/:strainId/edit" element={<EditStrainPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/compare" element={<ComparePage />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App; 