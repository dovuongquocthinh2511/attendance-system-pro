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
