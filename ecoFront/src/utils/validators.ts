import { z } from 'zod'

export const emailSchema = z.string().email('Correo electrónico inválido')

export const passwordSchema = z.string().min(6, 'Mínimo 6 caracteres')

export const loginSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
})

export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  full_name: z.string().min(2, 'Mínimo 2 caracteres'),
})

export const reportSchema = z.object({
  title: z.string().min(3, 'Mínimo 3 caracteres').max(100, 'Máximo 100 caracteres'),
  description: z.string().min(10, 'Mínimo 10 caracteres').max(500, 'Máximo 500 caracteres'),
  waste_type_id: z.number({ required_error: 'Selecciona un tipo de residuo' }),
  address: z.string().optional(),
})

export const profileSchema = z.object({
  full_name: z.string().min(2, 'Mínimo 2 caracteres'),
})

export const rewardSchema = z.object({
  name: z.string().min(3, 'Mínimo 3 caracteres'),
  description: z.string().min(10, 'Mínimo 10 caracteres'),
  points_cost: z.number().min(1, 'Debe ser mayor a 0'),
  stock: z.number().min(0, 'No puede ser negativo'),
})
