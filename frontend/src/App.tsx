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
