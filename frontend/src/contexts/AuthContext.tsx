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
