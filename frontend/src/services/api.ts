import { StrainData, TestResult } from '../types';
import type { TestCategory, Test } from '../types';
import { StrainFormValues } from '../components/StrainForm'
import axios from 'axios';

// Автоматическое определение API URL
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000/api'  // Development
  : '/api';                      // Production (относительный путь)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
    const response = await api.get(`/strains/${strainId}`);
    return response.data;
};

export const createStrain = async (data: StrainFormValues) => {
  try {
    const response = await api.post('/strains/create/', data);
    return response.data;
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Failed to create strain';
    throw new Error(errorMsg);
  }
};

export const updateStrain = (strainId: number, data: StrainPayload) =>
  api.patch(`/strains/${strainId}/update/`, data).then((res) => res.data)

export const deleteStrain = async (id: number, soft: boolean = true) => {
  const res = await api.delete(`/strains/${id}?soft=${soft}`);
  return res.data;
};

export const fetchTestCategories = async (includeTests: boolean = true): Promise<TestCategoryWithTests[]> => {
  const res = await api.get(`/tests/categories?include_tests=${includeTests}`);
  return res.data.categories as TestCategoryWithTests[];
}

export const getDashboardStats = async () => {
  const res = await api.get('/stats/');
  return res.data;
} 