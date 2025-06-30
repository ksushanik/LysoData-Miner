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
import Dashboard from './pages/Dashboard'
import WikiPage from './pages/Docs/WikiPage'
import FAQPage from './pages/Docs/FAQPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/strains" element={<SpeciesBrowser />} />
        <Route path="/species" element={<Navigate to="/strains" replace />} />
        <Route path="/strains/new" element={<CreateStrainPage />} />
        <Route path="/strains/species/:name" element={<SpeciesDetail />} />
        <Route path="/strains/:strainId" element={<StrainDetail />} />
        <Route path="/strains/:strainId/edit" element={<EditStrainPage />} />
        <Route path="/identify" element={<Identification />} />
        <Route path="/about" element={<About />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/help" element={<WikiPage />} />
        <Route path="/wiki" element={<Navigate to="/help" replace />} />
        <Route path="/faq" element={<FAQPage />} />
      </Routes>
    </Layout>
  );
}

export default App; 