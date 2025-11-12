// User types
export interface User {
  id: string
  email: string
  name: string
  role: string
  status: string
  is_active?: boolean
  is_admin?: boolean
  created_at: string
  updated_at: string
  date_of_birth?: string
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  name: string
  password: string
  date_of_birth: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface TwoFactorSetupResponse {
  secret: string
  qr_code: string
}

// Document types
export interface Document {
  id: string
  user_id: string
  document_type_id: string
  file_path: string
  file_size: number
  mime_type: string
  status: "pending" | "approved" | "rejected"
  uploaded_at: string
  verified_at?: string
  verified_by?: string
  rejection_reason?: string
}

export interface DocumentType {
  id: string
  name: string
  description?: string
  required_for_verification: boolean
  max_file_size: number
  allowed_mime_types: string[]
}

// Permission types
export interface Role {
  id: string
  name: string
  description?: string
  created_at: string
}

export interface Permission {
  id: string
  resource: string
  action: string
  description?: string
}

// Analytics types
export interface SystemMetrics {
  total_users: number
  active_users: number
  total_documents: number
  pending_documents: number
  total_api_calls: number
  avg_response_time: number
}

// API response types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// Service health types
export interface ServiceHealth {
  service: string
  status: "healthy" | "unhealthy" | "starting"
  uptime: number
  response_time: number
  last_checked: string
}

