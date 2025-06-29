import { StrainData, TestResult } from '../types';
import type { TestCategory, Test } from '../types';
import { StrainFormValues } from '../components/StrainForm'
import api from '../services/api'

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

export interface StrainDetailsResponse {
  strain: StrainData;
  test_results: TestResult[];
}

export const fetchStrainDetails = async (strainId: string): Promise<StrainDetailsResponse> => {
    const response = await fetch(`${API_BASE_URL}/strains/${strainId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: StrainDetailsResponse = await response.json();
    return data;
};

export const createStrain = async (data: StrainFormValues) => {
  const response = await fetch(`${API_BASE_URL}/strains/create/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create strain');
  }
  return response.json();
};

export const updateStrain = (strainId: number, data: StrainPayload) =>
  api.patch(`/strains/${strainId}/update/`, data).then((res) => res.data)

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

export const getDashboardStats = async () => {
  const res = await fetch(`${API_BASE_URL}/stats/`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
} 