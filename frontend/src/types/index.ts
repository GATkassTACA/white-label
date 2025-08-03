export interface BrandingConfig {
  company_name: string
  primary_color: string
  secondary_color?: string
  welcome_message: string
  logo_url?: string
  chat_placeholder: string
  footer_text: string
  features?: {
    documents_enabled: boolean
    file_upload_enabled: boolean
    real_time_chat: boolean
  }
}

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  status?: 'sending' | 'sent' | 'delivered' | 'error'
}

export interface ChatRoom {
  id: string
  name: string
  participants: number
  last_message?: Message
  created_at: Date
}

export interface DocumentProcessingResult {
  success: boolean
  text?: string
  method?: string
  pages?: number
  total_chars?: number
  metadata?: Record<string, any>
  error?: string
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}
