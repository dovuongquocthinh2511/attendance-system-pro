import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Toast, Card, List, Skeleton } from 'antd-mobile'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profileApi } from '../../api/profile'

export default function ProfileView() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.getProfile().then((r) => r.data.data),
  })

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, string>) => profileApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      Toast.show({ icon: 'success', content: 'Profile updated' })
      setEditing(false)
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Update failed' })
    },
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>
  if (!profile) return null

  const onFinish = (values: any) => {
    const data: Record<string, string> = {}
    if (values.mobile_phone) data.mobile_phone = values.mobile_phone
    if (values.work_email) data.work_email = values.work_email
    if (values.identification_id) data.identification_id = values.identification_id
    if (values.birthday) data.birthday = values.birthday
    updateMutation.mutate(data)
  }

  return (
    <div style={{ padding: 16 }}>
      <Card style={{ borderRadius: 12, marginBottom: 16 }}>
        <div style={{ textAlign: 'center', padding: '16px 0' }}>
          <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#1a1a2e', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 'bold', margin: '0 auto 12px' }}>
            {profile.name?.charAt(0) || 'U'}
          </div>
          <div style={{ fontSize: 20, fontWeight: 'bold' }}>{profile.name}</div>
          <div style={{ fontSize: 14, color: '#999' }}>{profile.job_title || 'Employee'}</div>
          <div style={{ fontSize: 13, color: '#999' }}>{profile.department_id?.[1] || ''}</div>
        </div>
      </Card>

      {editing ? (
        <Form
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            mobile_phone: profile.mobile_phone || '',
            work_email: profile.work_email || '',
            identification_id: profile.identification_id || '',
            birthday: profile.birthday || '',
          }}
          footer={
            <div style={{ display: 'flex', gap: 8 }}>
              <Button block onClick={() => setEditing(false)}>Cancel</Button>
              <Button block type="submit" color="primary" loading={updateMutation.isPending}>Save</Button>
            </div>
          }
        >
          <Form.Item name="mobile_phone" label="Mobile Phone">
            <Input placeholder="Mobile phone" />
          </Form.Item>
          <Form.Item name="work_email" label="Work Email">
            <Input placeholder="Work email" type="email" />
          </Form.Item>
          <Form.Item name="identification_id" label="ID Number">
            <Input placeholder="Identification number" />
          </Form.Item>
          <Form.Item name="birthday" label="Birthday">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      ) : (
        <>
          <List header="Personal Information">
            <List.Item extra={profile.work_email || '—'}>Email</List.Item>
            <List.Item extra={profile.mobile_phone || '—'}>Mobile</List.Item>
            <List.Item extra={profile.work_phone || '—'}>Work Phone</List.Item>
            <List.Item extra={profile.birthday || '—'}>Birthday</List.Item>
            <List.Item extra={profile.identification_id || '—'}>ID Number</List.Item>
            <List.Item extra={profile.work_location_id?.[1] || '—'}>Work Location</List.Item>
            <List.Item extra={profile.parent_id?.[1] || '—'}>Manager</List.Item>
          </List>
          <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            <Button block color="primary" onClick={() => setEditing(true)}>Edit Profile</Button>
            <Button block onClick={() => navigate('/profile/contract')}>View Contract</Button>
          </div>
        </>
      )}
    </div>
  )
}
