import apiClient from './client'
import type {
  APIResponse, ActionResponse, AttendanceStatusResponse,
  OdooAttendance, AttendanceSummaryResponse,
  CheckInRequest, CheckOutRequest,
} from '../types'

export const attendanceApi = {
  getStatus: () =>
    apiClient.get<APIResponse<AttendanceStatusResponse>>('/attendance/status'),

  checkIn: (data: CheckInRequest) =>
    apiClient.post<APIResponse<ActionResponse>>('/attendance/check-in', data),

  checkOut: (data: CheckOutRequest) =>
    apiClient.post<APIResponse<ActionResponse>>('/attendance/check-out', data),

  getHistory: (limit = 20) =>
    apiClient.get<APIResponse<OdooAttendance[]>>('/attendance/history', { params: { limit } }),

  getSummary: (month: number, year: number) =>
    apiClient.get<APIResponse<AttendanceSummaryResponse>>('/attendance/summary', { params: { month, year } }),
}
