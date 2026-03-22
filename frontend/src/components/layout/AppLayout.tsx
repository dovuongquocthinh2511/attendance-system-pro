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
  const initial = user?.name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'

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
