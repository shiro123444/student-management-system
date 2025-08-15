/**
 * API service for Educational QA Bot
 * Handles communication with the backend API
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios'

// Types
interface ChatRequest {
  query: string
  session_id?: string
  context?: string
  include_sources?: boolean
  max_sources?: number
}

interface SourceDocument {
  id: string
  title: string
  content_preview: string
  relevance_score: number
  document_type: string
  metadata: Record<string, any>
}

interface ChatResponse {
  session_id: string
  response: string
  sources: SourceDocument[]
  confidence_score: number
  processing_time_ms: number
  suggested_followups: string[]
}

interface HealthResponse {
  status: string
  timestamp: string
  version: string
  system_info: Record<string, any>
}

interface IngestResponse {
  file_id: string
  progress_id: string
  message: string
  filename: string
}

interface ProgressStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
  result?: any
  error?: string
}

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add timestamp to prevent caching
        config.params = {
          ...config.params,
          _t: Date.now(),
        }
        return config
      },
      (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error)
        
        // Handle specific error cases
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timeout - please try again')
        }
        
        if (error.response?.status === 404) {
          throw new Error('Service not found')
        }
        
        if (error.response?.status >= 500) {
          throw new Error('Server error - please try again later')
        }
        
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        }
        
        throw new Error(error.message || 'An unexpected error occurred')
      }
    )
  }

  // Health check
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response: AxiosResponse<HealthResponse> = await this.client.get('/api/health')
      return response.data
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }

  // Send chat message
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response: AxiosResponse<ChatResponse> = await this.client.post('/api/chat', request)
      return response.data
    } catch (error) {
      console.error('Send message failed:', error)
      throw error
    }
  }

  // Get chat history
  async getChatHistory(sessionId: string, limit: number = 50): Promise<any[]> {
    try {
      const response = await this.client.get(`/api/chat/history/${sessionId}`, {
        params: { limit }
      })
      return response.data
    } catch (error) {
      console.error('Get chat history failed:', error)
      throw error
    }
  }

  // Clear chat history
  async clearChatHistory(sessionId: string): Promise<{ message: string }> {
    try {
      const response = await this.client.delete(`/api/chat/history/${sessionId}`)
      return response.data
    } catch (error) {
      console.error('Clear chat history failed:', error)
      throw error
    }
  }

  // Upload file for ingestion
  async uploadFile(
    file: File,
    documentType: string = 'educational_content',
    metadata: Record<string, any> = {}
  ): Promise<IngestResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_type', documentType)
      formData.append('metadata', JSON.stringify(metadata))

      const response: AxiosResponse<IngestResponse> = await this.client.post(
        '/api/ingest/file',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 1 minute for file uploads
        }
      )
      return response.data
    } catch (error) {
      console.error('File upload failed:', error)
      throw error
    }
  }

  // Get ingestion status
  async getIngestionStatus(progressId: string): Promise<ProgressStatus> {
    try {
      const response: AxiosResponse<ProgressStatus> = await this.client.get(
        `/api/ingest/status/${progressId}`
      )
      return response.data
    } catch (error) {
      console.error('Get ingestion status failed:', error)
      throw error
    }
  }

  // Generate report
  async generateReport(
    reportType: string,
    options: {
      startDate?: string
      endDate?: string
      format?: string
      includeAnalytics?: boolean
    } = {}
  ): Promise<{ report_id: string; progress_id: string; message: string }> {
    try {
      const params = new URLSearchParams({
        report_type: reportType,
        ...options,
      })

      const response = await this.client.post(`/api/export/report?${params}`)
      return response.data
    } catch (error) {
      console.error('Generate report failed:', error)
      throw error
    }
  }

  // Download report
  async downloadReport(reportId: string): Promise<Blob> {
    try {
      const response = await this.client.get(`/api/export/report/${reportId}`, {
        responseType: 'blob',
      })
      return response.data
    } catch (error) {
      console.error('Download report failed:', error)
      throw error
    }
  }

  // Export knowledge graph
  async exportKnowledgeGraph(
    format: string = 'json',
    includeEmbeddings: boolean = false
  ): Promise<any> {
    try {
      const response = await this.client.get('/api/export/knowledge-graph', {
        params: {
          format,
          include_embeddings: includeEmbeddings,
        },
      })
      return response.data
    } catch (error) {
      console.error('Export knowledge graph failed:', error)
      throw error
    }
  }

  // Get analytics data
  async getAnalytics(
    metricTypes: string[] = [],
    aggregationLevel: string = 'daily'
  ): Promise<any> {
    try {
      const response = await this.client.get('/api/export/analytics', {
        params: {
          metric_types: metricTypes,
          aggregation_level: aggregationLevel,
        },
      })
      return response.data
    } catch (error) {
      console.error('Get analytics failed:', error)
      throw error
    }
  }

  // Generic GET request
  async get<T = any>(endpoint: string, params?: Record<string, any>): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.get(endpoint, { params })
      return response.data
    } catch (error) {
      console.error(`GET ${endpoint} failed:`, error)
      throw error
    }
  }

  // Generic POST request
  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.post(endpoint, data)
      return response.data
    } catch (error) {
      console.error(`POST ${endpoint} failed:`, error)
      throw error
    }
  }

  // Generic PUT request
  async put<T = any>(endpoint: string, data?: any): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.put(endpoint, data)
      return response.data
    } catch (error) {
      console.error(`PUT ${endpoint} failed:`, error)
      throw error
    }
  }

  // Generic DELETE request
  async delete<T = any>(endpoint: string): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.delete(endpoint)
      return response.data
    } catch (error) {
      console.error(`DELETE ${endpoint} failed:`, error)
      throw error
    }
  }
}

// Create and export API instance
export const api = new ApiService()

// Export specific API modules for better organization
export const chatApi = {
  healthCheck: () => api.healthCheck(),
  sendMessage: (request: ChatRequest) => api.sendMessage(request),
  getChatHistory: (sessionId: string, limit?: number) => api.getChatHistory(sessionId, limit),
  clearChatHistory: (sessionId: string) => api.clearChatHistory(sessionId),
}

export const ingestApi = {
  uploadFile: (file: File, documentType?: string, metadata?: Record<string, any>) =>
    api.uploadFile(file, documentType, metadata),
  getStatus: (progressId: string) => api.getIngestionStatus(progressId),
}

export const exportApi = {
  generateReport: (reportType: string, options?: any) => api.generateReport(reportType, options),
  downloadReport: (reportId: string) => api.downloadReport(reportId),
  exportKnowledgeGraph: (format?: string, includeEmbeddings?: boolean) =>
    api.exportKnowledgeGraph(format, includeEmbeddings),
  getAnalytics: (metricTypes?: string[], aggregationLevel?: string) =>
    api.getAnalytics(metricTypes, aggregationLevel),
}

// Export types
export type {
  ChatRequest,
  ChatResponse,
  SourceDocument,
  HealthResponse,
  IngestResponse,
  ProgressStatus,
}