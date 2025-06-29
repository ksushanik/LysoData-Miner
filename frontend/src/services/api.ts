import { Strain } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const fetchStrainDetails = async (strainId: string): Promise<Strain> => {
    const response = await fetch(`${API_BASE_URL}/strains/${strainId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: Strain = await response.json();
    return data;
}; 