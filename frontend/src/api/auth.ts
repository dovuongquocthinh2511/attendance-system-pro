import apiClient from './client'
import type {
  APIResponse, TokenResponse, ActionResponse,
  LoginRequest, ForgotPasswordRequest, ResetPasswordRequest,
} from '../types'

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<APIResponse<TokenResponse>>('/auth/login', data),

  logout: () =>
    apiClient.post<APIResponse<ActionResponse>>('/auth/logout'),

  refresh: () =>
    apiClient.post<APIResponse<TokenResponse>>('/auth/refresh'),

  forgotPassword: (data: ForgotPasswordRequest) =>
    apiClient.post<APIResponse<ActionResponse>>('/auth/forgot-password', data),

  resetPassword: (data: ResetPasswordRequest) =>
    apiClient.post<APIResponse<ActionResponse>>('/auth/reset-password', data),
}
