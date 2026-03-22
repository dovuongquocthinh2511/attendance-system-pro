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
