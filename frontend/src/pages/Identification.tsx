import React, { useState } from 'react';
import IdentificationForm from '../components/IdentificationForm';
import IdentificationResultsModal from '../components/IdentificationResultsModal';
import type { IdentificationResponse } from '../types';

export const Identification: React.FC = () => {
  const [results, setResults] = useState<IdentificationResponse | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleResults = (newResults: IdentificationResponse) => {
    setResults(newResults);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="container mx-auto px-4">
      {/* Page Header */}
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Strain Identification Tool
        </h1>
        <p className="text-lg text-muted-foreground">
          Identify Lysobacter strains based on laboratory test results.
        </p>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto">
        <IdentificationForm onResults={handleResults} />
      </div>
      
      {/* Results Modal */}
      {results && (
        <IdentificationResultsModal
          results={results}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
        />
      )}

      {/* About Section */}
      <div className="mt-20 text-center">
        <div className="bg-white rounded-xl shadow-md border border-border p-8">
          <h3 className="text-2xl font-bold text-foreground mb-4">
            About the System
          </h3>
          <p className="text-muted-foreground leading-relaxed max-w-3xl mx-auto">
            LysoData-Miner is a web service for identifying Lysobacter strains based on morphological, physiological, and biochemical characteristics. The system uses modern comparison algorithms with automatic calculation of the degree of compliance and confidence in the identification results.
          </p>
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-primary/5 rounded-lg p-4">
              <h4 className="font-semibold text-foreground mb-1">Morphological Tests</h4>
              <p className="text-xs text-muted-foreground">
                Colony shape, pigmentation, cell morphology
              </p>
            </div>
            <div className="bg-green-500/5 rounded-lg p-4">
              <h4 className="font-semibold text-foreground mb-1">Physiological Tests</h4>
              <p className="text-xs text-muted-foreground">
                Temperature, pH, growth conditions
              </p>
            </div>
            <div className="bg-purple-500/5 rounded-lg p-4">
              <h4 className="font-semibold text-foreground mb-1">Biochemical Tests</h4>
              <p className="text-xs text-muted-foreground">
                Enzymatic activity, substrate catabolism
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Identification; 