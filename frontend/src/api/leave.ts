import apiClient from './client'
import type {
  APIResponse, ActionResponse, LeaveCreateRequest,
  OdooLeave, LeaveBalanceResponse, OdooLeaveType,
} from '../types'

export const leaveApi = {
  createRequest: (data: LeaveCreateRequest) =>
    apiClient.post<APIResponse<ActionResponse>>('/leave/request', data),

  confirmRequest: (leaveId: number) =>
    apiClient.post<APIResponse<ActionResponse>>(`/leave/${leaveId}/confirm`),

  getHistory: () =>
    apiClient.get<APIResponse<OdooLeave[]>>('/leave/history'),

  getBalance: () =>
    apiClient.get<APIResponse<LeaveBalanceResponse[]>>('/leave/balance'),

  getTypes: () =>
    apiClient.get<APIResponse<OdooLeaveType[]>>('/leave/types'),

  approveRequest: (leaveId: number) =>
    apiClient.post<APIResponse<ActionResponse>>(`/leave/${leaveId}/approve`),

  rejectRequest: (leaveId: number) =>
    apiClient.post<APIResponse<ActionResponse>>(`/leave/${leaveId}/reject`),

  getPending: () =>
    apiClient.get<APIResponse<OdooLeave[]>>('/leave/pending'),
}
