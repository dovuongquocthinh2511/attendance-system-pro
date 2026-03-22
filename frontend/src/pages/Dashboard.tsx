import { useNavigate } from 'react-router-dom'
import { Grid, Card, Badge, Skeleton, Tag } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth'
import { attendanceApi } from '../api/attendance'
import { leaveApi } from '../api/leave'

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
        <Grid.Item onClick={() => navigate('/attendance')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>⏰</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Attendance</div>
            {attendanceContent}
          </Card>
        </Grid.Item>

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

        <Grid.Item onClick={() => navigate('/leave/request')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>✍️</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Leave Request</div>
            <div style={{ fontSize: 13, color: '#666' }}>New request</div>
          </Card>
        </Grid.Item>

        <Grid.Item onClick={() => navigate('/profile')}>
          <Card style={{ borderRadius: 12, minHeight: 120 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>👤</div>
            <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Profile</div>
            <div style={{ fontSize: 13, color: '#666' }}>{user?.role}</div>
          </Card>
        </Grid.Item>

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

        {(user?.role === 'manager' || user?.role === 'admin') && (
          <Grid.Item onClick={() => navigate('/admin/users')}>
            <Card style={{ borderRadius: 12, minHeight: 120 }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>👥</div>
              <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>Team</div>
              <div style={{ fontSize: 13, color: '#666' }}>View team</div>
            </Card>
          </Grid.Item>
        )}

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
