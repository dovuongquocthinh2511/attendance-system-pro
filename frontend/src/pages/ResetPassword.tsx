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
        <Form onFinish={onFinish} layout="vertical" initialValues={{ email }} footer={
          <Button block type="submit" color="primary" size="large" loading={loading}>
            Reset Password
          </Button>
        }>
          <Form.Item name="email" label="Email" rules={[{ required: true }]}>
            <Input placeholder="Email" type="email" readOnly={!!email} />
          </Form.Item>
          <Form.Item name="otp" label="OTP Code" rules={[{ required: true, message: 'Enter the OTP from your email' }]}>
            <Input placeholder="6-digit code" maxLength={6} />
          </Form.Item>
          <Form.Item name="new_password" label="New Password" rules={[{ required: true, message: 'Min 6 characters' }]}>
            <Input type="password" placeholder="New password" />
          </Form.Item>
        </Form>
      </div>
    </div>
  )
}
