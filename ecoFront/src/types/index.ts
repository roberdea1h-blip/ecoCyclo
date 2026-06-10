export interface User {
  id: string
  email: string
  username: string
  full_name: string
  avatar_url: string | null
  points: number
  role_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Report {
  id: string
  title: string
  description: string
  latitude: number
  longitude: number
  address: string | null
  status: 'pending' | 'in_progress' | 'cleaned'
  waste_type_id: string
  waste_type_name: string
  estimated_quantity: number | null
  image_url: string | null
  user_id: string
  user_name: string
  cleaner_id: string | null
  cleaner_name: string | null
  cleaned_at: string | null
  created_at: string
  updated_at: string
}

export interface ReportCreate {
  title: string
  description: string
  latitude: number
  longitude: number
  address?: string
  waste_type_id: string
  estimated_quantity?: number
}

export interface ReportUpdate {
  title?: string
  description?: string
  status?: string
  waste_type_id?: string
}

export interface Reward {
  id: string
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
  id: string
  user_id: string
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
}

export interface WasteType {
  id: string
  name: string
  description: string | null
  icon: string | null
  points_per_report: number
  created_at: string
  updated_at: string
}

export interface WasteTypeCreate {
  name: string
  description?: string
  icon?: string
  points_per_report?: number
}

export interface WasteTypeUpdate {
  name?: string
  description?: string
  icon?: string
  points_per_report?: number
}

export interface PointTransaction {
  id: string
  type: 'earned' | 'redeemed' | 'adjustment'
  points: number
  description: string | null
  reference_id: string | null
  created_at: string
}
