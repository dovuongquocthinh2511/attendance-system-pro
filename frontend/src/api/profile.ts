import apiClient from './client'
import type {
  APIResponse, ActionResponse, OdooEmployee,
  ProfileUpdateRequest, OdooContract,
} from '../types'

export const profileApi = {
  getProfile: () =>
    apiClient.get<APIResponse<OdooEmployee>>('/profile/'),

  updateProfile: (data: ProfileUpdateRequest) =>
    apiClient.put<APIResponse<ActionResponse>>('/profile/', data),

  getContract: () =>
    apiClient.get<APIResponse<OdooContract>>('/profile/contract'),
}
