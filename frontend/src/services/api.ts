import { Strain } from '../types';
import type { TestCategory, Test } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const headersJSON = { 'Content-Type': 'application/json' } as const;

export interface StrainPayload {
  strain_identifier: string;
  scientific_name?: string;
  common_name?: string;
  description?: string;
  isolation_source?: string;
  isolation_location?: string;
  isolation_date?: string;
  source_id?: number;
  notes?: string;
  is_active?: boolean;
  test_results?: any[];
}

export interface TestCategoryWithTests extends TestCategory {
  tests: Test[]
  test_count?: number
}

export const fetchStrainDetails = async (strainId: string): Promise<Strain> => {
    const response = await fetch(`${API_BASE_URL}/strains/${strainId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: Strain = await response.json();
    return data;
};

export const createStrain = async (payload: StrainPayload): Promise<number> => {
  const res = await fetch(`${API_BASE_URL}/strains/`, {
    method: 'POST',
    headers: headersJSON,
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.strain_id as number;
};

export const updateStrain = async (id: number, payload: Partial<StrainPayload>) => {
  const res = await fetch(`${API_BASE_URL}/strains/${id}`, {
    method: 'PUT',
    headers: headersJSON,
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text());
};

export const deleteStrain = async (id: number, soft: boolean = true) => {
  const res = await fetch(`${API_BASE_URL}/strains/${id}?soft=${soft}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error(await res.text());
};

export const fetchTestCategories = async (includeTests: boolean = true): Promise<TestCategoryWithTests[]> => {
  const res = await fetch(`${API_BASE_URL}/tests/categories?include_tests=${includeTests}`)
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.categories as TestCategoryWithTests[]
} 