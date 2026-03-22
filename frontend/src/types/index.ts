// Auth types
export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  role: string
  odoo_employee_id: number
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  email: string
  otp: string
  new_password: string
}

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export interface ActionResponse {
  msg: string
  id?: number
  state?: string
}

export interface User {
  id: number
  email: string
  phone?: string
  role: string
  odoo_employee_id?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserCreateRequest {
  email: string
  phone?: string
  role?: string
  odoo_employee_id?: number
  is_active?: boolean
  password: string
}

export interface UserUpdateRequest {
  email?: string
  phone?: string
  role?: string
  odoo_employee_id?: number
  is_active?: boolean
  password?: string
}

export type OdooM2O = [number, string] | null

export interface AttendanceStatusResponse {
  is_checked_in: boolean
  check_in_time?: string
  record_id?: number
}

export interface CheckInRequest {
  latitude?: number
  longitude?: number
  ip_address?: string
  mode?: string
}

export interface CheckOutRequest {
  latitude?: number
  longitude?: number
  ip_address?: string
  mode?: string
}

export interface OdooAttendance {
  id: number
  employee_id: OdooM2O
  check_in: string
  check_out?: string
  worked_hours?: number
  in_latitude?: number
  in_longitude?: number
  in_mode?: string
  out_latitude?: number
  out_longitude?: number
  out_mode?: string
}

export interface AttendanceSummaryResponse {
  month: number
  year: number
  total_hours: number
  attendance_count: number
}

export interface LeaveCreateRequest {
  leave_type_id: number
  date_from: string
  date_to: string
  description?: string
}

export interface OdooLeave {
  id: number
  employee_id: OdooM2O
  holiday_status_id: OdooM2O
  request_date_from: string
  request_date_to: string
  state: string
  number_of_days: number
  name?: string
}

export interface LeaveBalanceResponse {
  type_id: number
  name: string
  remaining: number
  allocated: number
  taken: number
}

export interface OdooLeaveType {
  id: number
  name: string
  allocation_validation_type?: string
}

export interface OdooEmployee {
  id: number
  name: string
  job_title?: string
  department_id: OdooM2O
  work_email?: string
  mobile_phone?: string
  work_phone?: string
  work_location_id: OdooM2O
  parent_id: OdooM2O
  birthday?: string
  identification_id?: string
}

export interface ProfileUpdateRequest {
  mobile_phone?: string
  work_email?: string
  identification_id?: string
  birthday?: string
}

export interface OdooContract {
  id: number
  employee_id: OdooM2O
  name: string
  wage: number
  state: string
  date_start: string
  date_end?: string
  job_id: OdooM2O
  department_id: OdooM2O
}

export interface AuthUser {
  id: string
  role: string
  odoo_employee_id: number
  name?: string
  email?: string
}
