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
