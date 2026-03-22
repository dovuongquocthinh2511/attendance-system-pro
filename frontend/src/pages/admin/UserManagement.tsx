import { useState } from 'react'
import { List, Tag, SearchBar, Button, Popup, Form, Input, Picker, Dialog, Toast, Skeleton, ErrorBlock, FloatingBubble } from 'antd-mobile'
import { AddOutline } from 'antd-mobile-icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../../api/users'
import type { User, UserCreateRequest, UserUpdateRequest } from '../../types'

const rolePicker = [[
  { label: 'Employee', value: 'employee' },
  { label: 'Manager', value: 'manager' },
  { label: 'Admin', value: 'admin' },
]]

export default function UserManagement() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [formVisible, setFormVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [rolePickerVisible, setRolePickerVisible] = useState(false)
  const [formRole, setFormRole] = useState('employee')

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.getUsers(0, 200).then((r) => r.data.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: UserCreateRequest) => usersApi.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      Toast.show({ icon: 'success', content: 'User created' })
      closeForm()
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to create user' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UserUpdateRequest }) => usersApi.updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      Toast.show({ icon: 'success', content: 'User updated' })
      closeForm()
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to update user' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => usersApi.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      Toast.show({ icon: 'success', content: 'User deleted' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to delete user' })
    },
  })

  const closeForm = () => {
    setFormVisible(false)
    setEditingUser(null)
    setFormRole('employee')
  }

  const openCreate = () => {
    setEditingUser(null)
    setFormRole('employee')
    setFormVisible(true)
  }

  const openEdit = (user: User) => {
    setEditingUser(user)
    setFormRole(user.role)
    setFormVisible(true)
  }

  const handleDelete = (user: User) => {
    Dialog.confirm({
      content: `Delete user ${user.email}? This cannot be undone.`,
      confirmText: 'Delete',
      onConfirm: () => deleteMutation.mutate(user.id),
    })
  }

  const handleSubmit = (values: any) => {
    const data = { ...values, role: formRole }
    if (editingUser) {
      if (!values.password) delete data.password
      updateMutation.mutate({ id: editingUser.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const filteredUsers = (users || []).filter((u) =>
    u.email.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>

  return (
    <div>
      <div style={{ padding: '12px 12px 0' }}>
        <SearchBar placeholder="Search by email" value={search} onChange={setSearch} />
      </div>

      {!filteredUsers.length ? (
        <ErrorBlock status="empty" title="No users found" style={{ padding: 48 }} />
      ) : (
        <List>
          {filteredUsers.map((user) => (
            <List.Item
              key={user.id}
              onClick={() => openEdit(user)}
              description={
                <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
                  <Tag color="primary">{user.role}</Tag>
                  <Tag color={user.is_active ? 'success' : 'default'}>{user.is_active ? 'Active' : 'Inactive'}</Tag>
                  {user.odoo_employee_id && <Tag color="warning">Odoo linked</Tag>}
                </div>
              }
              extra={
                <Button size="mini" color="danger" fill="none" onClick={(e) => { e.stopPropagation(); handleDelete(user) }}>
                  Delete
                </Button>
              }
            >
              {user.email}
            </List.Item>
          ))}
        </List>
      )}

      <FloatingBubble
        style={{ '--initial-position-bottom': '24px', '--initial-position-right': '24px', '--edge-distance': '24px' }}
        onClick={openCreate}
      >
        <AddOutline fontSize={24} />
      </FloatingBubble>

      <Popup visible={formVisible} onMaskClick={closeForm} bodyStyle={{ borderTopLeftRadius: 12, borderTopRightRadius: 12, padding: 24, maxHeight: '80vh', overflow: 'auto' }}>
        <h3 style={{ margin: '0 0 16px' }}>{editingUser ? 'Edit User' : 'Create User'}</h3>
        <Form
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={editingUser ? { email: editingUser.email, phone: editingUser.phone || '' } : {}}
          footer={
            <div style={{ display: 'flex', gap: 8 }}>
              <Button block onClick={closeForm}>Cancel</Button>
              <Button block type="submit" color="primary" loading={createMutation.isPending || updateMutation.isPending}>
                {editingUser ? 'Update' : 'Create'}
              </Button>
            </div>
          }
        >
          <Form.Item name="email" label="Email" rules={[{ required: true }]}>
            <Input placeholder="Email" type="email" />
          </Form.Item>
          <Form.Item name="phone" label="Phone">
            <Input placeholder="Phone (optional)" />
          </Form.Item>
          <Form.Item label="Role" onClick={() => setRolePickerVisible(true)}>
            <div style={{ padding: '4px 0' }}>{formRole}</div>
          </Form.Item>
          <Picker
            columns={rolePicker}
            visible={rolePickerVisible}
            onClose={() => setRolePickerVisible(false)}
            onConfirm={(val) => setFormRole(val[0] as string)}
          />
          {!editingUser && (
            <Form.Item name="password" label="Password" rules={[{ required: true, min: 6 }]}>
              <Input type="password" placeholder="Password (min 6 chars)" />
            </Form.Item>
          )}
          {editingUser && (
            <Form.Item name="password" label="New Password (optional)">
              <Input type="password" placeholder="Leave empty to keep current" />
            </Form.Item>
          )}
        </Form>
      </Popup>
    </div>
  )
}
