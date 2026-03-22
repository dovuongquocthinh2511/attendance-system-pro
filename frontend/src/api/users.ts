import apiClient from './client'
import type {
  APIResponse, User, UserCreateRequest, UserUpdateRequest,
} from '../types'

export const usersApi = {
  createUser: (data: UserCreateRequest) =>
    apiClient.post<APIResponse<User>>('/users/', data),

  getUsers: (skip = 0, limit = 50) =>
    apiClient.get<APIResponse<User[]>>('/users/', { params: { skip, limit } }),

  updateUser: (userId: number, data: UserUpdateRequest) =>
    apiClient.put<APIResponse<User>>(`/users/${userId}`, data),

  deleteUser: (userId: number) =>
    apiClient.delete<APIResponse<User>>(`/users/${userId}`),

  getTeam: () =>
    apiClient.get<APIResponse<User[]>>('/users/team'),
}
