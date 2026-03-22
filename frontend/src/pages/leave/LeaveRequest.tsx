import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Button, Toast, Picker, DatePicker, TextArea } from 'antd-mobile'
import { useQuery, useMutation } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'
import dayjs from 'dayjs'

export default function LeaveRequest() {
  const navigate = useNavigate()
  const [leaveTypeId, setLeaveTypeId] = useState<number | null>(null)
  const [leaveTypeName, setLeaveTypeName] = useState('')
  const [dateFrom, setDateFrom] = useState<Date | null>(null)
  const [dateTo, setDateTo] = useState<Date | null>(null)
  const [description, setDescription] = useState('')
  const [typePickerVisible, setTypePickerVisible] = useState(false)

  const { data: leaveTypes } = useQuery({
    queryKey: ['leave', 'types'],
    queryFn: () => leaveApi.getTypes().then((r) => r.data.data),
  })

  const typeColumns = [
    (leaveTypes || []).map((t) => ({ label: t.name, value: t.id })),
  ]

  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!leaveTypeId || !dateFrom || !dateTo) throw new Error('Please fill all fields')
      const res = await leaveApi.createRequest({
        leave_type_id: leaveTypeId,
        date_from: dayjs(dateFrom).format('YYYY-MM-DD'),
        date_to: dayjs(dateTo).format('YYYY-MM-DD'),
        description: description || undefined,
      })
      const leaveId = res.data.data?.id
      if (leaveId) {
        await leaveApi.confirmRequest(leaveId)
      }
      return res
    },
    onSuccess: () => {
      Toast.show({ icon: 'success', content: 'Leave request submitted' })
      navigate('/leave/history')
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || error.message || 'Failed to submit' })
    },
  })

  return (
    <div style={{ padding: 16 }}>
      <Form layout="vertical">
        <Form.Item label="Leave Type" onClick={() => setTypePickerVisible(true)}>
          <div style={{ color: leaveTypeName ? '#333' : '#ccc', padding: '4px 0' }}>
            {leaveTypeName || 'Select leave type'}
          </div>
        </Form.Item>

        <Picker
          columns={typeColumns}
          visible={typePickerVisible}
          onClose={() => setTypePickerVisible(false)}
          onConfirm={(val) => {
            setLeaveTypeId(val[0] as number)
            const found = leaveTypes?.find((t) => t.id === val[0])
            setLeaveTypeName(found?.name || '')
          }}
        />

        <Form.Item label="From Date">
          <DatePicker
            min={new Date()}
            value={dateFrom}
            onConfirm={setDateFrom}
          >
            {(value) => value ? dayjs(value).format('YYYY-MM-DD') : <span style={{ color: '#ccc' }}>Select date</span>}
          </DatePicker>
        </Form.Item>

        <Form.Item label="To Date">
          <DatePicker
            min={dateFrom || new Date()}
            value={dateTo}
            onConfirm={setDateTo}
          >
            {(value) => value ? dayjs(value).format('YYYY-MM-DD') : <span style={{ color: '#ccc' }}>Select date</span>}
          </DatePicker>
        </Form.Item>

        <Form.Item label="Description (optional)">
          <TextArea
            placeholder="Reason for leave..."
            value={description}
            onChange={setDescription}
            rows={3}
          />
        </Form.Item>
      </Form>

      <Button
        block
        color="primary"
        size="large"
        loading={submitMutation.isPending}
        onClick={() => submitMutation.mutate()}
        style={{ marginTop: 16 }}
      >
        Submit Request
      </Button>
    </div>
  )
}
