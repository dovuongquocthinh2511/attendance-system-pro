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
