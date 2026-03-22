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
