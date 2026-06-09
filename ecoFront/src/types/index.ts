export interface User {
  id: number
  email: string
  username: string
  full_name: string
  avatar_url: string | null
  points: number
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Report {
  id: number
  title: string
  description: string
  latitude: number
  longitude: number
  address: string | null
  status: 'pending' | 'in_progress' | 'resolved' | 'rejected'
  waste_type_id: number
  waste_type_name: string
  image_url: string | null
  user_id: number
  user_name: string
  created_at: string
  updated_at: string
}

export interface ReportCreate {
  title: string
  description: string
  latitude: number
  longitude: number
  address?: string
  waste_type_id: number
  image?: File
}

export interface ReportUpdate {
  title?: string
  description?: string
  status?: string
  waste_type_id?: number
}

export interface Reward {
  id: number
  name: string
  description: string
  points_cost: number
  stock: number
  image_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RewardCreate {
  name: string
  description: string
  points_cost: number
  stock: number
  image_url?: string
}

export interface Notification {
  id: number
  user_id: number
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
}

export interface WasteType {
  id: number
  name: string
  description: string
  icon: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
