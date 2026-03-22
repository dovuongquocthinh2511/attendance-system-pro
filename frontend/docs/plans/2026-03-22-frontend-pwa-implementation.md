# Frontend PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a mobile-first PWA frontend for Bestmix Pro HR with React + Vite + antd-mobile, connecting to the existing FastAPI backend.

**Architecture:** Monolith SPA with role-adaptive dashboard. Hamburger menu + dashboard grid navigation. React Context for auth/app state, TanStack Query for server state. Offline-aware (app shell cached, actions require online).

**Tech Stack:** React 19, TypeScript, Vite, vite-plugin-pwa, antd-mobile, TanStack Query, Axios, React Router v7, dayjs

**Spec:** `frontend/docs/specs/2026-03-22-frontend-pwa-design.md`

**Working directory:** `/mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro/frontend`

---

## Phase 1: Project Scaffolding

### Task 1: Initialize Vite + React + TypeScript project

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`
- Create: `frontend/.env`
- Create: `frontend/.env.example`
- Create: `frontend/src/vite-env.d.ts`
- Create: `frontend/src/main.tsx` (placeholder)
- Create: `frontend/src/App.tsx` (placeholder)

- [ ] **Step 1: Scaffold Vite project**

```bash
cd /mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro
rm -f frontend/README.md
cd frontend
npm create vite@latest . -- --template react-ts
```

Accept overwrite if prompted. This creates the base structure.

- [ ] **Step 2: Install all dependencies**

```bash
cd /mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro/frontend
npm install antd-mobile @tanstack/react-query react-router-dom axios dayjs
npm install -D vite-plugin-pwa
```

- [ ] **Step 3: Create environment files**

`.env`:
```
VITE_API_URL=http://localhost:8000
```

`.env.example`:
```
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 4: Configure vite.config.ts with PWA**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'Bestmix Pro HR',
        short_name: 'Bestmix',
        description: 'HR Attendance & Leave Management',
        theme_color: '#1a1a2e',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        navigateFallback: 'index.html',
      },
      devOptions: {
        enabled: true,
        type: 'module',
        navigateFallback: 'index.html',
      },
    }),
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

- [ ] **Step 5: Update index.html with PWA meta tags**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
    <meta name="theme-color" content="#1a1a2e" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <title>Bestmix Pro HR</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create placeholder PWA icons in public/**

Create simple SVG favicon and placeholder PNGs:

`public/favicon.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="20" fill="#1a1a2e"/><text x="50" y="65" font-size="50" text-anchor="middle" fill="white" font-family="Arial">B</text></svg>
```

`public/robots.txt`:
```
User-agent: *
Allow: /
```

For `pwa-192x192.png`, `pwa-512x512.png`, `apple-touch-icon.png`: create minimal placeholder PNGs (can be replaced later with proper icons). Use the favicon.svg converted or just copy a simple 1x1 PNG for now.

- [ ] **Step 7: Update vite-env.d.ts**

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

- [ ] **Step 8: Verify dev server starts**

```bash
cd /mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro/frontend
npm run dev
```

Expected: Dev server starts at http://localhost:3000, default Vite page loads.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): scaffold Vite + React + TypeScript + PWA project"
```

---

## Phase 2: Foundation Layer (Types, Utils, API Client)

### Task 2: TypeScript type definitions

**Files:**
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: Create all TypeScript interfaces matching backend schemas**

```typescript
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

// Generic API response wrapper
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

// User types
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

// Odoo Many2one type: [id, "Display Name"] or null
export type OdooM2O = [number, string] | null

// Attendance types
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

// Leave types
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

// Profile types
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

// Auth context user (decoded from JWT + login response + profile)
export interface AuthUser {
  id: string
  role: string
  odoo_employee_id: number
  name?: string
  email?: string
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/
git commit -m "feat(frontend): add TypeScript type definitions matching backend schemas"
```

---

### Task 3: Utility modules (token storage + formatters)

**Files:**
- Create: `frontend/src/utils/token.ts`
- Create: `frontend/src/utils/format.ts`

- [ ] **Step 1: Create token storage utilities**

```typescript
// src/utils/token.ts
const TOKEN_KEY = 'bestmix_token'

export function saveToken(token: string, rememberMe: boolean): void {
  if (rememberMe) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    sessionStorage.setItem(TOKEN_KEY, token)
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(TOKEN_KEY)
}
```

- [ ] **Step 2: Create format utilities**

```typescript
// src/utils/format.ts
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'

dayjs.extend(duration)

export function formatDate(date: string): string {
  return dayjs(date).format('MMM DD, YYYY')
}

export function formatTime(datetime: string): string {
  return dayjs(datetime).format('HH:mm')
}

export function formatDateTime(datetime: string): string {
  return dayjs(datetime).format('MMM DD, YYYY HH:mm')
}

export function formatDuration(seconds: number): string {
  const d = dayjs.duration(seconds, 'seconds')
  const hours = Math.floor(d.asHours())
  const minutes = d.minutes()
  return `${hours}h ${minutes}m`
}

export function formatHours(hours: number): string {
  return `${hours.toFixed(1)}h`
}

export function googleMapsUrl(lat: number, lng: number): string {
  return `https://maps.google.com/?q=${lat},${lng}`
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/utils/
git commit -m "feat(frontend): add token storage and format utilities"
```

---

### Task 4: Axios API client with interceptors

**Files:**
- Create: `frontend/src/api/client.ts`

- [ ] **Step 1: Create Axios client with request/response interceptors**

```typescript
// src/api/client.ts
import axios from 'axios'
import { getToken, clearToken, saveToken } from '../utils/token'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach token
apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401 refresh + errors
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Network error - suppress, let useOnlineStatus handle UI
    if (!error.response) {
      return Promise.reject(error)
    }

    // 401 - try refresh
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const token = getToken()
        if (!token) {
          throw new Error('No token')
        }
        const response = await axios.post(
          `${apiClient.defaults.baseURL}/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        )
        const newToken = response.data.data.access_token
        // Preserve remember-me preference: if token was in localStorage, keep it there
        const rememberMe = localStorage.getItem('bestmix_token') !== null
        saveToken(newToken, rememberMe)
        processQueue(null, newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        clearToken()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/client.ts
git commit -m "feat(frontend): add Axios client with token refresh interceptor"
```

---

### Task 5: API modules (auth, attendance, leave, profile, users)

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/attendance.ts`
- Create: `frontend/src/api/leave.ts`
- Create: `frontend/src/api/profile.ts`
- Create: `frontend/src/api/users.ts`

- [ ] **Step 1: Create auth API module**

```typescript
// src/api/auth.ts
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
```

- [ ] **Step 2: Create attendance API module**

```typescript
// src/api/attendance.ts
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
```

- [ ] **Step 3: Create leave API module**

```typescript
// src/api/leave.ts
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
```

- [ ] **Step 4: Create profile API module**

```typescript
// src/api/profile.ts
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
```

- [ ] **Step 5: Create users API module**

```typescript
// src/api/users.ts
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
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/
git commit -m "feat(frontend): add API modules for auth, attendance, leave, profile, users"
```

---

## Phase 3: Contexts & Hooks

### Task 6: Auth context and app context

**Files:**
- Create: `frontend/src/contexts/AuthContext.tsx`
- Create: `frontend/src/contexts/AppContext.tsx`
- Create: `frontend/src/hooks/useAuth.ts`
- Create: `frontend/src/hooks/useOnlineStatus.ts`

- [ ] **Step 1: Create AuthContext**

```typescript
// src/contexts/AuthContext.tsx
import { createContext, useState, useCallback, useMemo, useEffect, type ReactNode } from 'react'
import type { AuthUser, LoginRequest } from '../types'
import { authApi } from '../api/auth'
import { getToken, saveToken, clearToken } from '../utils/token'

interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (data: LoginRequest, rememberMe: boolean) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | null>(null)

function decodeToken(token: string): AuthUser | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    if (payload.exp * 1000 < Date.now()) return null
    return {
      id: payload.sub,
      role: payload.role,
      odoo_employee_id: payload.odoo_employee_id,
    }
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (token) {
      const decoded = decodeToken(token)
      if (decoded) {
        setUser(decoded)
      } else {
        clearToken()
      }
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (data: LoginRequest, rememberMe: boolean) => {
    const response = await authApi.login(data)
    const { access_token } = response.data.data!
    saveToken(access_token, rememberMe)
    const decoded = decodeToken(access_token)
    if (decoded) {
      // Store login email for sidebar display
      decoded.email = data.username
    }
    setUser(decoded)
  }, [])

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } catch {
      // Ignore logout API errors
    }
    clearToken()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout]
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
```

- [ ] **Step 2: Create AppContext**

```typescript
// src/contexts/AppContext.tsx
import { createContext, useState, useMemo, type ReactNode } from 'react'
import { useOnlineStatus } from '../hooks/useOnlineStatus'

interface AppContextType {
  isOnline: boolean
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

export const AppContext = createContext<AppContextType | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const isOnline = useOnlineStatus()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const value = useMemo(
    () => ({ isOnline, sidebarOpen, setSidebarOpen }),
    [isOnline, sidebarOpen]
  )

  return <AppContext value={value}>{children}</AppContext>
}
```

- [ ] **Step 3: Create hooks**

```typescript
// src/hooks/useAuth.ts
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

```typescript
// src/hooks/useOnlineStatus.ts
import { useState, useEffect } from 'react'

export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  useEffect(() => {
    const goOnline = () => setIsOnline(true)
    const goOffline = () => setIsOnline(false)
    window.addEventListener('online', goOnline)
    window.addEventListener('offline', goOffline)
    return () => {
      window.removeEventListener('online', goOnline)
      window.removeEventListener('offline', goOffline)
    }
  }, [])

  return isOnline
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/contexts/ frontend/src/hooks/
git commit -m "feat(frontend): add AuthContext, AppContext, and custom hooks"
```

---

## Phase 4: Layout & Common Components

### Task 7: Common components (ProtectedRoute, RoleGuard, PageLoading)

**Files:**
- Create: `frontend/src/components/common/ProtectedRoute.tsx`
- Create: `frontend/src/components/common/RoleGuard.tsx`
- Create: `frontend/src/components/common/PageLoading.tsx`

- [ ] **Step 1: Create ProtectedRoute**

```typescript
// src/components/common/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import PageLoading from './PageLoading'

interface Props {
  allowedRoles?: string[]
}

export default function ProtectedRoute({ allowedRoles }: Props) {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) return <PageLoading />

  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
```

- [ ] **Step 2: Create RoleGuard**

```typescript
// src/components/common/RoleGuard.tsx
import type { ReactNode } from 'react'
import { useAuth } from '../../hooks/useAuth'

interface Props {
  roles: string[]
  children: ReactNode
}

export default function RoleGuard({ roles, children }: Props) {
  const { user } = useAuth()
  if (!user || !roles.includes(user.role)) return null
  return <>{children}</>
}
```

- [ ] **Step 3: Create PageLoading**

```typescript
// src/components/common/PageLoading.tsx
import { Skeleton } from 'antd-mobile'

export default function PageLoading() {
  return (
    <div style={{ padding: 16 }}>
      <Skeleton.Title animated />
      <Skeleton.Paragraph lineCount={5} animated />
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/common/
git commit -m "feat(frontend): add ProtectedRoute, RoleGuard, PageLoading components"
```

---

### Task 8: App layout (hamburger + sidebar + offline banner)

**Files:**
- Create: `frontend/src/components/layout/AppLayout.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/components/layout/OfflineBanner.tsx`

- [ ] **Step 1: Create OfflineBanner**

```typescript
// src/components/layout/OfflineBanner.tsx
import { useContext } from 'react'
import { AppContext } from '../../contexts/AppContext'

export default function OfflineBanner() {
  const app = useContext(AppContext)
  if (!app || app.isOnline) return null

  return (
    <div
      style={{
        background: '#ff8f1f',
        color: 'white',
        textAlign: 'center',
        padding: '6px 16px',
        fontSize: 13,
      }}
    >
      No internet connection. Some features are unavailable.
    </div>
  )
}
```

- [ ] **Step 2: Create Sidebar**

```typescript
// src/components/layout/Sidebar.tsx
import { useContext } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Popup, List, Tag } from 'antd-mobile'
import {
  AppOutline, ClockCircleOutline, FileOutline,
  CalendarOutline, EditSOutline, HistogramOutline,
  CheckCircleOutline, UserOutline, SetOutline,
} from 'antd-mobile-icons'
import { AppContext } from '../../contexts/AppContext'
import { useAuth } from '../../hooks/useAuth'

const menuItems = [
  { label: 'Dashboard', path: '/', icon: <AppOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'Attendance', path: '/attendance', icon: <ClockCircleOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'Attendance History', path: '/attendance/history', icon: <HistogramOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'Leave Balance', path: '/leave', icon: <CalendarOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'New Leave Request', path: '/leave/request', icon: <EditSOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'Leave History', path: '/leave/history', icon: <FileOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'Pending Approvals', path: '/leave/pending', icon: <CheckCircleOutline />, roles: ['manager', 'admin'] },
  { label: 'Profile', path: '/profile', icon: <UserOutline />, roles: ['employee', 'manager', 'admin'] },
  { label: 'User Management', path: '/admin/users', icon: <SetOutline />, roles: ['admin'] },
]

export default function Sidebar() {
  const app = useContext(AppContext)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  if (!app || !user) return null

  const filteredItems = menuItems.filter((item) => item.roles.includes(user.role))

  const handleNavigate = (path: string) => {
    navigate(path)
    app.setSidebarOpen(false)
  }

  const handleLogout = async () => {
    app.setSidebarOpen(false)
    await logout()
    navigate('/login')
  }

  return (
    <Popup
      visible={app.sidebarOpen}
      onMaskClick={() => app.setSidebarOpen(false)}
      position="left"
      bodyStyle={{ width: '75vw', maxWidth: 320 }}
    >
      <div style={{ padding: '24px 16px 12px', borderBottom: '1px solid #eee' }}>
        <div style={{ fontSize: 18, fontWeight: 'bold' }}>{user.name || user.email || user.id}</div>
        <div style={{ fontSize: 13, color: '#999' }}>{user.email}</div>
        <Tag color="primary" style={{ marginTop: 4 }}>{user.role}</Tag>
      </div>
      <List>
        {filteredItems.map((item) => (
          <List.Item
            key={item.path}
            prefix={item.icon}
            onClick={() => handleNavigate(item.path)}
            style={{
              color: location.pathname === item.path ? '#1677ff' : undefined,
            }}
          >
            {item.label}
          </List.Item>
        ))}
        <List.Item
          prefix={<ClockCircleOutline />}
          onClick={handleLogout}
          style={{ color: '#ff3141' }}
        >
          Logout
        </List.Item>
      </List>
    </Popup>
  )
}
```

- [ ] **Step 3: Create AppLayout**

```typescript
// src/components/layout/AppLayout.tsx
import { useContext } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { NavBar } from 'antd-mobile'
import { UnorderedListOutline } from 'antd-mobile-icons'
import { AppContext } from '../../contexts/AppContext'
import { useAuth } from '../../hooks/useAuth'
import Sidebar from './Sidebar'
import OfflineBanner from './OfflineBanner'

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/attendance': 'Attendance',
  '/attendance/history': 'Attendance History',
  '/leave': 'Leave Balance',
  '/leave/request': 'New Leave Request',
  '/leave/history': 'Leave History',
  '/leave/pending': 'Pending Approvals',
  '/profile': 'Profile',
  '/profile/contract': 'Contract',
  '/admin/users': 'User Management',
}

export default function AppLayout() {
  const app = useContext(AppContext)
  const { user } = useAuth()
  const location = useLocation()

  const title = pageTitles[location.pathname] || 'Bestmix Pro'
  const initial = user?.role?.charAt(0).toUpperCase() || 'U'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <NavBar
        backIcon={<UnorderedListOutline />}
        onBack={() => app?.setSidebarOpen(true)}
        right={
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: '#1a1a2e',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 14,
              fontWeight: 'bold',
            }}
          >
            {initial}
          </div>
        }
        style={{ background: '#1a1a2e', color: 'white' }}
      >
        {title}
      </NavBar>
      <OfflineBanner />
      <div style={{ flex: 1, overflow: 'auto', background: '#f5f5f5' }}>
        <Outlet />
      </div>
      <Sidebar />
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/
git commit -m "feat(frontend): add AppLayout with hamburger sidebar and offline banner"
```

---

## Phase 5: Auth Pages

### Task 9: Login, ForgotPassword, ResetPassword pages

**Files:**
- Create: `frontend/src/pages/Login.tsx`
- Create: `frontend/src/pages/ForgotPassword.tsx`
- Create: `frontend/src/pages/ResetPassword.tsx`

- [ ] **Step 1: Create Login page**

```typescript
// src/pages/Login.tsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Form, Input, Button, Checkbox, Toast } from 'antd-mobile'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      await login(values, rememberMe)
      navigate('/', { replace: true })
    } catch (error: any) {
      const msg = error.response?.data?.error || 'Login failed'
      Toast.show({ icon: 'fail', content: msg })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 24, background: '#1a1a2e' }}>
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <h1 style={{ color: 'white', fontSize: 28, margin: 0 }}>Bestmix Pro</h1>
        <p style={{ color: 'rgba(255,255,255,0.6)', marginTop: 8 }}>HR Management System</p>
      </div>
      <div style={{ background: 'white', borderRadius: 12, padding: '24px 16px' }}>
        <Form onFinish={onFinish} layout="vertical" footer={
          <Button block type="submit" color="primary" size="large" loading={loading}>
            Sign In
          </Button>
        }>
          <Form.Item name="username" label="Email or Phone" rules={[{ required: true, message: 'Please enter email or phone' }]}>
            <Input placeholder="Enter email or phone" autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true, message: 'Please enter password' }]}>
            <Input type="password" placeholder="Enter password" autoComplete="current-password" />
          </Form.Item>
        </Form>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12, padding: '0 4px' }}>
          <Checkbox checked={rememberMe} onChange={setRememberMe} style={{ fontSize: 14 }}>
            Remember me
          </Checkbox>
          <Link to="/forgot-password" style={{ fontSize: 14, color: '#1677ff' }}>
            Forgot password?
          </Link>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create ForgotPassword page**

```typescript
// src/pages/ForgotPassword.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Toast, NavBar } from 'antd-mobile'
import { authApi } from '../api/auth'

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: { email: string }) => {
    setLoading(true)
    try {
      await authApi.forgotPassword(values)
      Toast.show({ icon: 'success', content: 'OTP sent to your email' })
      navigate('/reset-password', { state: { email: values.email } })
    } catch (error: any) {
      const msg = error.response?.data?.error || 'Failed to send OTP'
      Toast.show({ icon: 'fail', content: msg })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <NavBar onBack={() => navigate('/login')}>Forgot Password</NavBar>
      <div style={{ padding: 24 }}>
        <p style={{ color: '#666', marginBottom: 24 }}>
          Enter your email address and we will send you an OTP to reset your password.
        </p>
        <Form onFinish={onFinish} layout="vertical" footer={
          <Button block type="submit" color="primary" size="large" loading={loading}>
            Send OTP
          </Button>
        }>
          <Form.Item name="email" label="Email" rules={[{ required: true, message: 'Please enter your email' }]}>
            <Input placeholder="Enter your email" type="email" />
          </Form.Item>
        </Form>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create ResetPassword page**

```typescript
// src/pages/ResetPassword.tsx
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Form, Input, Button, Toast, NavBar } from 'antd-mobile'
import { authApi } from '../api/auth'

export default function ResetPassword() {
  const navigate = useNavigate()
  const location = useLocation()
  const email = (location.state as { email?: string })?.email || ''
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: { email: string; otp: string; new_password: string }) => {
    setLoading(true)
    try {
      await authApi.resetPassword(values)
      Toast.show({ icon: 'success', content: 'Password reset successfully' })
      navigate('/login', { replace: true })
    } catch (error: any) {
      const msg = error.response?.data?.error || 'Failed to reset password'
      Toast.show({ icon: 'fail', content: msg })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <NavBar onBack={() => navigate('/forgot-password')}>Reset Password</NavBar>
      <div style={{ padding: 24 }}>
        <Form
          onFinish={onFinish}
          layout="vertical"
          initialValues={{ email }}
          footer={
            <Button block type="submit" color="primary" size="large" loading={loading}>
              Reset Password
            </Button>
          }
        >
          <Form.Item name="email" label="Email" rules={[{ required: true }]}>
            <Input placeholder="Email" type="email" readOnly={!!email} />
          </Form.Item>
          <Form.Item name="otp" label="OTP Code" rules={[{ required: true, message: 'Enter the OTP from your email' }]}>
            <Input placeholder="6-digit code" maxLength={6} />
          </Form.Item>
          <Form.Item name="new_password" label="New Password" rules={[{ required: true, min: 6, message: 'Min 6 characters' }]}>
            <Input type="password" placeholder="New password" />
          </Form.Item>
        </Form>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Login.tsx frontend/src/pages/ForgotPassword.tsx frontend/src/pages/ResetPassword.tsx
git commit -m "feat(frontend): add Login, ForgotPassword, ResetPassword pages"
```

---

## Phase 6: Dashboard

### Task 10: Dashboard page with role-adaptive tiles

**Files:**
- Create: `frontend/src/pages/Dashboard.tsx`

- [ ] **Step 1: Create Dashboard**

```typescript
// src/pages/Dashboard.tsx
import { useNavigate } from 'react-router-dom'
import { Grid, Card, Badge, Skeleton, Tag } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth'
import { attendanceApi } from '../api/attendance'
import { leaveApi } from '../api/leave'
import { formatDuration } from '../utils/format'

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: statusData, isLoading: statusLoading } = useQuery({
    queryKey: ['attendance', 'status'],
    queryFn: () => attendanceApi.getStatus().then((r) => r.data.data),
  })

  const { data: balanceData, isLoading: balanceLoading } = useQuery({
    queryKey: ['leave', 'balance'],
    queryFn: () => leaveApi.getBalance().then((r) => r.data.data),
  })

  const { data: pendingData, isLoading: pendingLoading } = useQuery({
    queryKey: ['leave', 'pending'],
    queryFn: () => leaveApi.getPending().then((r) => r.data.data),
    enabled: user?.role === 'manager' || user?.role === 'admin',
  })

  const totalRemaining = balanceData?.reduce((sum, b) => sum + b.remaining, 0) ?? 0

  const attendanceContent = statusLoading ? (
    <Skeleton.Paragraph lineCount={2} animated />
  ) : statusData?.is_checked_in ? (
    <Tag color="success">Working</Tag>
  ) : (
    <Tag color="default">Not checked in</Tag>
  )

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ margin: '0 0 16px', fontSize: 20 }}>
        Welcome back
      </h2>
      <Grid columns={2} gap={12}>
        {/* Attendance tile */}
        <Grid.Item onClick={() => navigate('/attendance')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>⏰</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Attendance</div>
            {attendanceContent}
          </Card>
        </Grid.Item>

        {/* Leave Balance tile */}
        <Grid.Item onClick={() => navigate('/leave')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>📅</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Leave Balance</div>
            {balanceLoading ? (
              <Skeleton.Paragraph lineCount={1} animated />
            ) : (
              <div style={{ fontSize: 13, color: '#666' }}>{totalRemaining} days remaining</div>
            )}
          </Card>
        </Grid.Item>

        {/* Leave Request tile */}
        <Grid.Item onClick={() => navigate('/leave/request')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>✍️</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Leave Request</div>
            <div style={{ fontSize: 13, color: '#666' }}>New request</div>
          </Card>
        </Grid.Item>

        {/* Profile tile */}
        <Grid.Item onClick={() => navigate('/profile')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>👤</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Profile</div>
            <div style={{ fontSize: 13, color: '#666' }}>{user?.role}</div>
          </Card>
        </Grid.Item>

        {/* Manager/Admin: Pending Approvals tile */}
        {(user?.role === 'manager' || user?.role === 'admin') && (
          <Grid.Item onClick={() => navigate('/leave/pending')}>
            <Card style={{ borderRadius: 12, minHeight: 120 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>✅</div>
              <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Pending Approvals</div>
              {pendingLoading ? (
                <Skeleton.Paragraph lineCount={1} animated />
              ) : (
                <Badge content={pendingData?.length || 0} style={{ '--right': '-10px', '--top': '-4px' }}>
                  <span style={{ fontSize: 13, color: '#666' }}>{pendingData?.length || 0} pending</span>
                </Badge>
              )}
            </Card>
          </Grid.Item>
        )}

        {/* Manager/Admin: Team tile */}
        {(user?.role === 'manager' || user?.role === 'admin') && (
          <Grid.Item onClick={() => navigate('/admin/users')}>
            <Card style={{ borderRadius: 12, minHeight: 120 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>👥</div>
              <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Team</div>
              <div style={{ fontSize: 13, color: '#666' }}>View team</div>
            </Card>
          </Grid.Item>
        )}

        {/* Admin: User Management tile */}
        {user?.role === 'admin' && (
          <Grid.Item onClick={() => navigate('/admin/users')}>
            <Card style={{ borderRadius: 12, minHeight: 120 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>⚙️</div>
              <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>User Management</div>
              <div style={{ fontSize: 13, color: '#666' }}>Manage users</div>
            </Card>
          </Grid.Item>
        )}
      </Grid>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Dashboard.tsx
git commit -m "feat(frontend): add role-adaptive Dashboard with data tiles"
```

---

## Phase 7: Attendance Pages

### Task 11: AttendanceStatus page (check-in/out + timer)

**Files:**
- Create: `frontend/src/pages/attendance/AttendanceStatus.tsx`

- [ ] **Step 1: Create AttendanceStatus with live timer and GPS**

```typescript
// src/pages/attendance/AttendanceStatus.tsx
import { useState, useEffect } from 'react'
import { Card, Button, Toast, Result } from 'antd-mobile'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { attendanceApi } from '../../api/attendance'
import { formatTime } from '../../utils/format'
import type { CheckInRequest } from '../../types'

function useElapsedTime(startTime: string | undefined) {
  const [elapsed, setElapsed] = useState('')
  useEffect(() => {
    if (!startTime) { setElapsed(''); return }
    const update = () => {
      const diff = Date.now() - new Date(startTime).getTime()
      const hours = Math.floor(diff / 3600000)
      const minutes = Math.floor((diff % 3600000) / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      setElapsed(`${hours}h ${minutes}m ${seconds}s`)
    }
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [startTime])
  return elapsed
}

function getGeoLocation(): Promise<{ latitude: number; longitude: number } | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) { resolve(null); return }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => resolve(null),
      { timeout: 10000, enableHighAccuracy: true }
    )
  })
}

export default function AttendanceStatus() {
  const queryClient = useQueryClient()

  const { data: status, isLoading } = useQuery({
    queryKey: ['attendance', 'status'],
    queryFn: () => attendanceApi.getStatus().then((r) => r.data.data),
  })

  const elapsed = useElapsedTime(status?.check_in_time)

  const checkInMutation = useMutation({
    mutationFn: async () => {
      const geo = await getGeoLocation()
      const payload: CheckInRequest = { mode: 'manual', ...geo }
      return attendanceApi.checkIn(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance', 'status'] })
      Toast.show({ icon: 'success', content: 'Checked in successfully' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Check-in failed' })
    },
  })

  const checkOutMutation = useMutation({
    mutationFn: async () => {
      const geo = await getGeoLocation()
      const payload: CheckInRequest = { mode: 'manual', ...geo }
      return attendanceApi.checkOut(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance', 'status'] })
      Toast.show({ icon: 'success', content: 'Checked out successfully' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Check-out failed' })
    },
  })

  if (isLoading) {
    return <div style={{ padding: 16 }}><Card><Result status="waiting" title="Loading..." /></Card></div>
  }

  const isCheckedIn = status?.is_checked_in

  return (
    <div style={{ padding: 16 }}>
      <Card style={{ borderRadius: 12, textAlign: 'center', padding: '32px 16px' }}>
        <div style={{ fontSize: 16, color: '#666', marginBottom: 8 }}>Current Status</div>
        <div style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 8, color: isCheckedIn ? '#00b578' : '#666' }}>
          {isCheckedIn ? 'Working' : 'Not Checked In'}
        </div>
        {isCheckedIn && status?.check_in_time && (
          <>
            <div style={{ fontSize: 14, color: '#999', marginBottom: 4 }}>
              Since {formatTime(status.check_in_time)}
            </div>
            <div style={{ fontSize: 32, fontWeight: 'bold', color: '#1677ff', marginBottom: 24 }}>
              {elapsed}
            </div>
          </>
        )}
        {!isCheckedIn && <div style={{ height: 24 }} />}
        <Button
          color={isCheckedIn ? 'danger' : 'success'}
          size="large"
          block
          loading={checkInMutation.isPending || checkOutMutation.isPending}
          onClick={() => isCheckedIn ? checkOutMutation.mutate() : checkInMutation.mutate()}
          style={{ borderRadius: 8, height: 48, fontSize: 18 }}
        >
          {isCheckedIn ? 'CHECK OUT' : 'CHECK IN'}
        </Button>
      </Card>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/attendance/AttendanceStatus.tsx
git commit -m "feat(frontend): add AttendanceStatus page with live timer and GPS"
```

---

### Task 12: AttendanceHistory page (history + summary tabs)

**Files:**
- Create: `frontend/src/pages/attendance/AttendanceHistory.tsx`

- [ ] **Step 1: Create AttendanceHistory with tabs**

```typescript
// src/pages/attendance/AttendanceHistory.tsx
import { useState } from 'react'
import { Tabs, List, Tag, Card, Picker, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { attendanceApi } from '../../api/attendance'
import { formatDate, formatTime, formatHours, googleMapsUrl } from '../../utils/format'

const currentDate = new Date()
const monthColumns = [
  Array.from({ length: 12 }, (_, i) => ({ label: `Month ${i + 1}`, value: i + 1 })),
  Array.from({ length: 5 }, (_, i) => ({ label: `${currentDate.getFullYear() - 2 + i}`, value: currentDate.getFullYear() - 2 + i })),
]

export default function AttendanceHistory() {
  const [month, setMonth] = useState(currentDate.getMonth() + 1)
  const [year, setYear] = useState(currentDate.getFullYear())
  const [pickerVisible, setPickerVisible] = useState(false)

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['attendance', 'history'],
    queryFn: () => attendanceApi.getHistory(50).then((r) => r.data.data),
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['attendance', 'summary', month, year],
    queryFn: () => attendanceApi.getSummary(month, year).then((r) => r.data.data),
  })

  return (
    <div>
      <Tabs defaultActiveKey="history">
        <Tabs.Tab title="History" key="history">
          <div style={{ padding: 12 }}>
            {historyLoading ? (
              <Skeleton.Paragraph lineCount={8} animated />
            ) : !history?.length ? (
              <ErrorBlock status="empty" title="No records yet" description="Check in to start tracking." />
            ) : (
              <List>
                {history.map((record) => (
                  <List.Item
                    key={record.id}
                    description={
                      <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                        {record.in_latitude && record.in_longitude && (
                          <div>
                            Check-in: <a href={googleMapsUrl(record.in_latitude, record.in_longitude)} target="_blank" rel="noopener noreferrer">View location</a>
                          </div>
                        )}
                        {record.out_latitude && record.out_longitude && (
                          <div>
                            Check-out: <a href={googleMapsUrl(record.out_latitude, record.out_longitude)} target="_blank" rel="noopener noreferrer">View location</a>
                          </div>
                        )}
                        {record.in_mode && <Tag style={{ marginTop: 4 }}>{record.in_mode}</Tag>}
                      </div>
                    }
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{formatDate(record.check_in)}</div>
                        <div style={{ fontSize: 13, color: '#666' }}>
                          {formatTime(record.check_in)} → {record.check_out ? formatTime(record.check_out) : '—'}
                        </div>
                      </div>
                      <Tag color="primary">
                        {record.worked_hours ? formatHours(record.worked_hours) : '—'}
                      </Tag>
                    </div>
                  </List.Item>
                ))}
              </List>
            )}
          </div>
        </Tabs.Tab>

        <Tabs.Tab title="Summary" key="summary">
          <div style={{ padding: 16 }}>
            <Card
              style={{ borderRadius: 12, marginBottom: 16, cursor: 'pointer' }}
              onClick={() => setPickerVisible(true)}
            >
              <div style={{ textAlign: 'center', fontSize: 16, fontWeight: 'bold' }}>
                Month {month} / {year}
              </div>
              <div style={{ textAlign: 'center', fontSize: 13, color: '#999' }}>Tap to change</div>
            </Card>

            <Picker
              columns={monthColumns}
              visible={pickerVisible}
              onClose={() => setPickerVisible(false)}
              value={[month, year]}
              onConfirm={(val) => {
                setMonth(val[0] as number)
                setYear(val[1] as number)
              }}
            />

            {summaryLoading ? (
              <Skeleton.Paragraph lineCount={4} animated />
            ) : summary ? (
              <Card style={{ borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center', padding: '16px 0' }}>
                  <div>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: '#1677ff' }}>
                      {formatHours(summary.total_hours)}
                    </div>
                    <div style={{ fontSize: 13, color: '#999' }}>Total Hours</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: '#00b578' }}>
                      {summary.attendance_count}
                    </div>
                    <div style={{ fontSize: 13, color: '#999' }}>Days</div>
                  </div>
                </div>
              </Card>
            ) : (
              <ErrorBlock status="empty" title="No data" description="No attendance records for this period." />
            )}
          </div>
        </Tabs.Tab>
      </Tabs>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/attendance/AttendanceHistory.tsx
git commit -m "feat(frontend): add AttendanceHistory page with GPS links and monthly summary"
```

---

## Phase 8: Leave Pages

### Task 13: LeaveBalance and LeaveRequest pages

**Files:**
- Create: `frontend/src/pages/leave/LeaveBalance.tsx`
- Create: `frontend/src/pages/leave/LeaveRequest.tsx`

- [ ] **Step 1: Create LeaveBalance**

```typescript
// src/pages/leave/LeaveBalance.tsx
import { useNavigate } from 'react-router-dom'
import { List, ProgressBar, Button, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'

export default function LeaveBalance() {
  const navigate = useNavigate()

  const { data: balances, isLoading } = useQuery({
    queryKey: ['leave', 'balance'],
    queryFn: () => leaveApi.getBalance().then((r) => r.data.data),
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={6} animated /></div>

  return (
    <div style={{ padding: 16 }}>
      {!balances?.length ? (
        <ErrorBlock status="empty" title="No leave types" description="No leave allocations found." />
      ) : (
        <List>
          {balances.map((b) => {
            const percent = b.allocated > 0 ? (b.taken / b.allocated) * 100 : 0
            return (
              <List.Item
                key={b.type_id}
                description={
                  <div style={{ marginTop: 8 }}>
                    <ProgressBar percent={percent} style={{ '--fill-color': percent > 80 ? '#ff3141' : '#1677ff' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#999', marginTop: 4 }}>
                      <span>Taken: {b.taken} days</span>
                      <span>Allocated: {b.allocated} days</span>
                    </div>
                  </div>
                }
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 'bold' }}>{b.name}</span>
                  <span style={{ color: '#1677ff', fontWeight: 'bold' }}>{b.remaining} days left</span>
                </div>
              </List.Item>
            )
          })}
        </List>
      )}
      <div style={{ padding: '16px 0' }}>
        <Button block color="primary" size="large" onClick={() => navigate('/leave/request')}>
          New Leave Request
        </Button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create LeaveRequest**

```typescript
// src/pages/leave/LeaveRequest.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Button, Toast, Picker, DatePicker, TextArea } from 'antd-mobile'
import { useQuery, useMutation } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'
import dayjs from 'dayjs'

export default function LeaveRequest() {
  const navigate = useNavigate()
  const [leaveTypeId, setLeaveTypeId] = useState<number | null>(null)
  const [leaveTypeName, setLeaveTypeName] = useState('')
  const [dateFrom, setDateFrom] = useState<Date | null>(null)
  const [dateTo, setDateTo] = useState<Date | null>(null)
  const [description, setDescription] = useState('')
  const [typePickerVisible, setTypePickerVisible] = useState(false)

  const { data: leaveTypes } = useQuery({
    queryKey: ['leave', 'types'],
    queryFn: () => leaveApi.getTypes().then((r) => r.data.data),
  })

  const typeColumns = [
    (leaveTypes || []).map((t) => ({ label: t.name, value: t.id })),
  ]

  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!leaveTypeId || !dateFrom || !dateTo) throw new Error('Please fill all fields')
      const res = await leaveApi.createRequest({
        leave_type_id: leaveTypeId,
        date_from: dayjs(dateFrom).format('YYYY-MM-DD'),
        date_to: dayjs(dateTo).format('YYYY-MM-DD'),
        description: description || undefined,
      })
      const leaveId = res.data.data?.id
      if (leaveId) {
        await leaveApi.confirmRequest(leaveId)
      }
      return res
    },
    onSuccess: () => {
      Toast.show({ icon: 'success', content: 'Leave request submitted' })
      navigate('/leave/history')
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || error.message || 'Failed to submit' })
    },
  })

  return (
    <div style={{ padding: 16 }}>
      <Form layout="vertical">
        <Form.Item label="Leave Type" onClick={() => setTypePickerVisible(true)}>
          <div style={{ color: leaveTypeName ? '#333' : '#ccc', padding: '4px 0' }}>
            {leaveTypeName || 'Select leave type'}
          </div>
        </Form.Item>

        <Picker
          columns={typeColumns}
          visible={typePickerVisible}
          onClose={() => setTypePickerVisible(false)}
          onConfirm={(val) => {
            setLeaveTypeId(val[0] as number)
            const found = leaveTypes?.find((t) => t.id === val[0])
            setLeaveTypeName(found?.name || '')
          }}
        />

        <Form.Item label="From Date">
          <DatePicker
            min={new Date()}
            value={dateFrom}
            onConfirm={setDateFrom}
          >
            {(value) => value ? dayjs(value).format('YYYY-MM-DD') : <span style={{ color: '#ccc' }}>Select date</span>}
          </DatePicker>
        </Form.Item>

        <Form.Item label="To Date">
          <DatePicker
            min={dateFrom || new Date()}
            value={dateTo}
            onConfirm={setDateTo}
          >
            {(value) => value ? dayjs(value).format('YYYY-MM-DD') : <span style={{ color: '#ccc' }}>Select date</span>}
          </DatePicker>
        </Form.Item>

        <Form.Item label="Description (optional)">
          <TextArea
            placeholder="Reason for leave..."
            value={description}
            onChange={setDescription}
            rows={3}
          />
        </Form.Item>
      </Form>

      <Button
        block
        color="primary"
        size="large"
        loading={submitMutation.isPending}
        onClick={() => submitMutation.mutate()}
        style={{ marginTop: 16 }}
      >
        Submit Request
      </Button>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/leave/LeaveBalance.tsx frontend/src/pages/leave/LeaveRequest.tsx
git commit -m "feat(frontend): add LeaveBalance and LeaveRequest pages"
```

---

### Task 14: LeaveHistory and PendingApprovals pages

**Files:**
- Create: `frontend/src/pages/leave/LeaveHistory.tsx`
- Create: `frontend/src/pages/leave/PendingApprovals.tsx`

- [ ] **Step 1: Create LeaveHistory**

```typescript
// src/pages/leave/LeaveHistory.tsx
import { List, Tag, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'
import { formatDate } from '../../utils/format'

const stateColors: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: 'Draft' },
  confirm: { color: 'warning', label: 'Pending' },
  validate: { color: 'success', label: 'Approved' },
  refuse: { color: 'danger', label: 'Rejected' },
}

export default function LeaveHistory() {
  const { data: leaves, isLoading } = useQuery({
    queryKey: ['leave', 'history'],
    queryFn: () => leaveApi.getHistory().then((r) => r.data.data),
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>

  if (!leaves?.length) {
    return <ErrorBlock status="empty" title="No leave requests yet" style={{ padding: 48 }} />
  }

  return (
    <div style={{ padding: 12 }}>
      <List>
        {leaves.map((leave) => {
          const state = stateColors[leave.state] || stateColors.draft
          return (
            <List.Item
              key={leave.id}
              description={
                <div style={{ fontSize: 13, color: '#999', marginTop: 4 }}>
                  {formatDate(leave.request_date_from)} → {formatDate(leave.request_date_to)}
                  {leave.name && <div style={{ marginTop: 2 }}>{leave.name}</div>}
                </div>
              }
              extra={<Tag color={state.color as any}>{state.label}</Tag>}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 'bold' }}>
                  {leave.holiday_status_id?.[1] || 'Leave'}
                </span>
                <span style={{ fontSize: 13, color: '#666' }}>{leave.number_of_days} days</span>
              </div>
            </List.Item>
          )
        })}
      </List>
    </div>
  )
}
```

- [ ] **Step 2: Create PendingApprovals**

```typescript
// src/pages/leave/PendingApprovals.tsx
import { List, Button, Dialog, Toast, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'
import { formatDate } from '../../utils/format'

export default function PendingApprovals() {
  const queryClient = useQueryClient()

  const { data: pending, isLoading } = useQuery({
    queryKey: ['leave', 'pending'],
    queryFn: () => leaveApi.getPending().then((r) => r.data.data),
  })

  const approveMutation = useMutation({
    mutationFn: (leaveId: number) => leaveApi.approveRequest(leaveId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave', 'pending'] })
      Toast.show({ icon: 'success', content: 'Leave approved' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to approve' })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: (leaveId: number) => leaveApi.rejectRequest(leaveId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave', 'pending'] })
      Toast.show({ icon: 'success', content: 'Leave rejected' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to reject' })
    },
  })

  const handleApprove = (leaveId: number, name: string) => {
    Dialog.confirm({
      content: `Approve leave request for ${name}?`,
      onConfirm: () => approveMutation.mutate(leaveId),
    })
  }

  const handleReject = (leaveId: number, name: string) => {
    Dialog.confirm({
      content: `Reject leave request for ${name}?`,
      onConfirm: () => rejectMutation.mutate(leaveId),
    })
  }

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>

  if (!pending?.length) {
    return <ErrorBlock status="empty" title="All caught up!" description="No pending requests." style={{ padding: 48 }} />
  }

  return (
    <div style={{ padding: 12 }}>
      <List>
        {pending.map((leave) => {
          const employeeName = leave.employee_id?.[1] || 'Employee'
          return (
            <List.Item
              key={leave.id}
              description={
                <div>
                  <div style={{ fontSize: 13, color: '#999', marginTop: 4 }}>
                    {formatDate(leave.request_date_from)} → {formatDate(leave.request_date_to)} ({leave.number_of_days} days)
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    <Button
                      size="small"
                      color="success"
                      onClick={() => handleApprove(leave.id, employeeName)}
                      loading={approveMutation.isPending}
                    >
                      Approve
                    </Button>
                    <Button
                      size="small"
                      color="danger"
                      onClick={() => handleReject(leave.id, employeeName)}
                      loading={rejectMutation.isPending}
                    >
                      Reject
                    </Button>
                  </div>
                </div>
              }
            >
              <div>
                <span style={{ fontWeight: 'bold' }}>{employeeName}</span>
                <span style={{ fontSize: 13, color: '#666', marginLeft: 8 }}>
                  {leave.holiday_status_id?.[1] || 'Leave'}
                </span>
              </div>
            </List.Item>
          )
        })}
      </List>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/leave/LeaveHistory.tsx frontend/src/pages/leave/PendingApprovals.tsx
git commit -m "feat(frontend): add LeaveHistory and PendingApprovals pages"
```

---

## Phase 9: Profile & Admin Pages

### Task 15: ProfileView and ContractView pages

**Files:**
- Create: `frontend/src/pages/profile/ProfileView.tsx`
- Create: `frontend/src/pages/profile/ContractView.tsx`

- [ ] **Step 1: Create ProfileView**

```typescript
// src/pages/profile/ProfileView.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Toast, Card, List, Skeleton, DatePicker } from 'antd-mobile'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profileApi } from '../../api/profile'
import dayjs from 'dayjs'

export default function ProfileView() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.getProfile().then((r) => r.data.data),
  })

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, string>) => profileApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      Toast.show({ icon: 'success', content: 'Profile updated' })
      setEditing(false)
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Update failed' })
    },
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>
  if (!profile) return null

  const onFinish = (values: any) => {
    const data: Record<string, string> = {}
    if (values.mobile_phone) data.mobile_phone = values.mobile_phone
    if (values.work_email) data.work_email = values.work_email
    if (values.identification_id) data.identification_id = values.identification_id
    if (values.birthday) data.birthday = values.birthday
    updateMutation.mutate(data)
  }

  return (
    <div style={{ padding: 16 }}>
      <Card style={{ borderRadius: 12, marginBottom: 16 }}>
        <div style={{ textAlign: 'center', padding: '16px 0' }}>
          <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#1a1a2e', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 'bold', margin: '0 auto 12px' }}>
            {profile.name?.charAt(0) || 'U'}
          </div>
          <div style={{ fontSize: 20, fontWeight: 'bold' }}>{profile.name}</div>
          <div style={{ fontSize: 14, color: '#999' }}>{profile.job_title || 'Employee'}</div>
          <div style={{ fontSize: 13, color: '#999' }}>{profile.department_id?.[1] || ''}</div>
        </div>
      </Card>

      {editing ? (
        <Form
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            mobile_phone: profile.mobile_phone || '',
            work_email: profile.work_email || '',
            identification_id: profile.identification_id || '',
            birthday: profile.birthday || '',
          }}
          footer={
            <div style={{ display: 'flex', gap: 8 }}>
              <Button block onClick={() => setEditing(false)}>Cancel</Button>
              <Button block type="submit" color="primary" loading={updateMutation.isPending}>Save</Button>
            </div>
          }
        >
          <Form.Item name="mobile_phone" label="Mobile Phone">
            <Input placeholder="Mobile phone" />
          </Form.Item>
          <Form.Item name="work_email" label="Work Email">
            <Input placeholder="Work email" type="email" />
          </Form.Item>
          <Form.Item name="identification_id" label="ID Number">
            <Input placeholder="Identification number" />
          </Form.Item>
          <Form.Item name="birthday" label="Birthday">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      ) : (
        <>
          <List header="Personal Information">
            <List.Item extra={profile.work_email || '—'}>Email</List.Item>
            <List.Item extra={profile.mobile_phone || '—'}>Mobile</List.Item>
            <List.Item extra={profile.work_phone || '—'}>Work Phone</List.Item>
            <List.Item extra={profile.birthday || '—'}>Birthday</List.Item>
            <List.Item extra={profile.identification_id || '—'}>ID Number</List.Item>
            <List.Item extra={profile.work_location_id?.[1] || '—'}>Work Location</List.Item>
            <List.Item extra={profile.parent_id?.[1] || '—'}>Manager</List.Item>
          </List>
          <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            <Button block color="primary" onClick={() => setEditing(true)}>Edit Profile</Button>
            <Button block onClick={() => navigate('/profile/contract')}>View Contract</Button>
          </div>
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Create ContractView**

```typescript
// src/pages/profile/ContractView.tsx
import { List, Tag, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../../api/profile'
import { formatDate } from '../../utils/format'

const stateColors: Record<string, string> = {
  open: 'success',
  draft: 'default',
  close: 'danger',
}

export default function ContractView() {
  const { data: contract, isLoading, error } = useQuery({
    queryKey: ['profile', 'contract'],
    queryFn: () => profileApi.getContract().then((r) => r.data.data),
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={6} animated /></div>
  if (error || !contract) return <ErrorBlock status="empty" title="No contract found" style={{ padding: 48 }} />

  return (
    <div style={{ padding: 16 }}>
      <List header="Contract Details">
        <List.Item extra={contract.name}>Contract</List.Item>
        <List.Item extra={
          <Tag color={(stateColors[contract.state] || 'default') as any}>
            {contract.state}
          </Tag>
        }>Status</List.Item>
        <List.Item extra={contract.wage?.toLocaleString()}>Wage</List.Item>
        <List.Item extra={formatDate(contract.date_start)}>Start Date</List.Item>
        <List.Item extra={contract.date_end ? formatDate(contract.date_end) : '—'}>End Date</List.Item>
        <List.Item extra={contract.job_id?.[1] || '—'}>Job Position</List.Item>
        <List.Item extra={contract.department_id?.[1] || '—'}>Department</List.Item>
      </List>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/profile/
git commit -m "feat(frontend): add ProfileView and ContractView pages"
```

---

### Task 16: UserManagement page (admin)

**Files:**
- Create: `frontend/src/pages/admin/UserManagement.tsx`

- [ ] **Step 1: Create UserManagement**

```typescript
// src/pages/admin/UserManagement.tsx
import { useState } from 'react'
import { List, Tag, SearchBar, Button, Popup, Form, Input, Picker, Switch, Dialog, Toast, Skeleton, ErrorBlock, FloatingBubble } from 'antd-mobile'
import { AddOutline } from 'antd-mobile-icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../../api/users'
import type { User, UserCreateRequest, UserUpdateRequest } from '../../types'

const rolePicker = [[
  { label: 'Employee', value: 'employee' },
  { label: 'Manager', value: 'manager' },
  { label: 'Admin', value: 'admin' },
]]

export default function UserManagement() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [formVisible, setFormVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [rolePickerVisible, setRolePickerVisible] = useState(false)
  const [formRole, setFormRole] = useState('employee')

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.getUsers(0, 200).then((r) => r.data.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: UserCreateRequest) => usersApi.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      Toast.show({ icon: 'success', content: 'User created' })
      closeForm()
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to create user' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UserUpdateRequest }) => usersApi.updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      Toast.show({ icon: 'success', content: 'User updated' })
      closeForm()
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to update user' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => usersApi.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      Toast.show({ icon: 'success', content: 'User deleted' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to delete user' })
    },
  })

  const closeForm = () => {
    setFormVisible(false)
    setEditingUser(null)
    setFormRole('employee')
  }

  const openCreate = () => {
    setEditingUser(null)
    setFormRole('employee')
    setFormVisible(true)
  }

  const openEdit = (user: User) => {
    setEditingUser(user)
    setFormRole(user.role)
    setFormVisible(true)
  }

  const handleDelete = (user: User) => {
    Dialog.confirm({
      content: `Delete user ${user.email}? This cannot be undone.`,
      confirmText: 'Delete',
      onConfirm: () => deleteMutation.mutate(user.id),
    })
  }

  const handleSubmit = (values: any) => {
    const data = { ...values, role: formRole }
    if (editingUser) {
      delete data.password
      if (values.password) data.password = values.password
      updateMutation.mutate({ id: editingUser.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const filteredUsers = (users || []).filter((u) =>
    u.email.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>

  return (
    <div>
      <div style={{ padding: '12px 12px 0' }}>
        <SearchBar placeholder="Search by email" value={search} onChange={setSearch} />
      </div>

      {!filteredUsers.length ? (
        <ErrorBlock status="empty" title="No users found" style={{ padding: 48 }} />
      ) : (
        <List>
          {filteredUsers.map((user) => (
            <List.Item
              key={user.id}
              onClick={() => openEdit(user)}
              description={
                <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
                  <Tag color="primary">{user.role}</Tag>
                  <Tag color={user.is_active ? 'success' : 'default'}>{user.is_active ? 'Active' : 'Inactive'}</Tag>
                  {user.odoo_employee_id && <Tag color="warning">Odoo linked</Tag>}
                </div>
              }
              extra={
                <Button size="mini" color="danger" fill="none" onClick={(e) => { e.stopPropagation(); handleDelete(user) }}>
                  Delete
                </Button>
              }
            >
              {user.email}
            </List.Item>
          ))}
        </List>
      )}

      <FloatingBubble
        style={{ '--initial-position-bottom': '24px', '--initial-position-right': '24px', '--edge-distance': '24px' }}
        onClick={openCreate}
      >
        <AddOutline fontSize={24} />
      </FloatingBubble>

      <Popup visible={formVisible} onMaskClick={closeForm} bodyStyle={{ borderTopLeftRadius: 12, borderTopRightRadius: 12, padding: 24, maxHeight: '80vh', overflow: 'auto' }}>
        <h3 style={{ margin: '0 0 16px' }}>{editingUser ? 'Edit User' : 'Create User'}</h3>
        <Form
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={editingUser ? { email: editingUser.email, phone: editingUser.phone || '' } : {}}
          footer={
            <div style={{ display: 'flex', gap: 8 }}>
              <Button block onClick={closeForm}>Cancel</Button>
              <Button block type="submit" color="primary" loading={createMutation.isPending || updateMutation.isPending}>
                {editingUser ? 'Update' : 'Create'}
              </Button>
            </div>
          }
        >
          <Form.Item name="email" label="Email" rules={[{ required: true }]}>
            <Input placeholder="Email" type="email" />
          </Form.Item>
          <Form.Item name="phone" label="Phone">
            <Input placeholder="Phone (optional)" />
          </Form.Item>
          <Form.Item label="Role" onClick={() => setRolePickerVisible(true)}>
            <div style={{ padding: '4px 0' }}>{formRole}</div>
          </Form.Item>
          <Picker
            columns={rolePicker}
            visible={rolePickerVisible}
            onClose={() => setRolePickerVisible(false)}
            onConfirm={(val) => setFormRole(val[0] as string)}
          />
          {!editingUser && (
            <Form.Item name="password" label="Password" rules={[{ required: true, min: 6 }]}>
              <Input type="password" placeholder="Password (min 6 chars)" />
            </Form.Item>
          )}
          {editingUser && (
            <Form.Item name="password" label="New Password (optional)">
              <Input type="password" placeholder="Leave empty to keep current" />
            </Form.Item>
          )}
        </Form>
      </Popup>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/admin/
git commit -m "feat(frontend): add UserManagement page with CRUD operations"
```

---

## Phase 10: App Assembly & Router

### Task 17: Wire up App.tsx with router and providers, update main.tsx

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Create App.tsx with full router setup**

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { AppProvider } from './contexts/AppContext'
import AppLayout from './components/layout/AppLayout'
import ProtectedRoute from './components/common/ProtectedRoute'
import Login from './pages/Login'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Dashboard from './pages/Dashboard'
import AttendanceStatus from './pages/attendance/AttendanceStatus'
import AttendanceHistory from './pages/attendance/AttendanceHistory'
import LeaveBalance from './pages/leave/LeaveBalance'
import LeaveRequest from './pages/leave/LeaveRequest'
import LeaveHistory from './pages/leave/LeaveHistory'
import PendingApprovals from './pages/leave/PendingApprovals'
import ProfileView from './pages/profile/ProfileView'
import ContractView from './pages/profile/ContractView'
import UserManagement from './pages/admin/UserManagement'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: true,
      networkMode: 'online',
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <AppProvider>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />

              {/* Protected routes */}
              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/attendance" element={<AttendanceStatus />} />
                  <Route path="/attendance/history" element={<AttendanceHistory />} />
                  <Route path="/leave" element={<LeaveBalance />} />
                  <Route path="/leave/request" element={<LeaveRequest />} />
                  <Route path="/leave/history" element={<LeaveHistory />} />

                  {/* Manager + Admin routes */}
                  <Route element={<ProtectedRoute allowedRoles={['manager', 'admin']} />}>
                    <Route path="/leave/pending" element={<PendingApprovals />} />
                  </Route>

                  <Route path="/profile" element={<ProfileView />} />
                  <Route path="/profile/contract" element={<ContractView />} />

                  {/* Manager + Admin routes */}
                  <Route element={<ProtectedRoute allowedRoles={['manager', 'admin']} />}>
                    <Route path="/admin/users" element={<UserManagement />} />
                  </Route>
                </Route>
              </Route>
            </Routes>
          </AppProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
```

- [ ] **Step 2: Update main.tsx**

```typescript
// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 3: Remove Vite scaffold files that are no longer needed**

Delete: `src/App.css`, `src/index.css`, `src/assets/` (Vite defaults).

- [ ] **Step 4: Verify the app compiles and runs**

```bash
cd /mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro/frontend
npm run dev
```

Expected: App starts at http://localhost:3000, shows Login page. No TypeScript errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat(frontend): wire up App router, providers, and main entry point"
```

---

## Phase 11: Final Verification

### Task 18: End-to-end verification

- [ ] **Step 1: Run TypeScript check**

```bash
cd /mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro/frontend
npx tsc --noEmit
```

Expected: No TypeScript errors.

- [ ] **Step 2: Run production build**

```bash
npm run build
```

Expected: Build succeeds, output in `dist/`. PWA manifest generated.

- [ ] **Step 3: Preview production build**

```bash
npm run preview
```

Expected: App loads at preview URL. Login page renders. PWA manifest accessible.

- [ ] **Step 4: Verify PWA**

Open Chrome DevTools → Application tab:
- Manifest: should show "Bestmix Pro HR" with icons
- Service Worker: should be registered

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat(frontend): complete PWA frontend for Bestmix Pro HR"
```
