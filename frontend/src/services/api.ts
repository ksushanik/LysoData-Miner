import { StrainData, TestResult } from '../types';
import type { TestCategory, Test } from '../types';
import { StrainFormValues } from '../components/StrainForm'
import axios from 'axios';

// Автоматическое определение API URL
const isDevelopment = (window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1') && 
                      window.location.port === '3000'; // Только Vite dev server
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000/api'  // Development (Vite dev server)
  : '/api';                      // Production (относительный путь через Nginx)

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
    const response = await api.post('/strains/', data);
    return response.data.strain_id;
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

export const fetchSpecies = async () => {
  const res = await api.get('/species');
  return res.data;
}

// Универсальная функция для API запросов с правильным URL
export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}; 