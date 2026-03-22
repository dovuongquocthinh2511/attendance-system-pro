import { List, Button, Dialog, Toast, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'
import { formatDate } from '../../utils/format'

export default function PendingApprovals() {
  const queryClient = useQueryClient()

  const { data: pending, isLoading } = useQuery({
    queryKey: ['leave', 'pending'],
    queryFn: () => leaveApi.getPending().then((r) => r.data.data),
  })

  const approveMutation = useMutation({
    mutationFn: (leaveId: number) => leaveApi.approveRequest(leaveId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave', 'pending'] })
      Toast.show({ icon: 'success', content: 'Leave approved' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to approve' })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: (leaveId: number) => leaveApi.rejectRequest(leaveId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave', 'pending'] })
      Toast.show({ icon: 'success', content: 'Leave rejected' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Failed to reject' })
    },
  })

  const handleApprove = (leaveId: number, name: string) => {
    Dialog.confirm({
      content: `Approve leave request for ${name}?`,
      onConfirm: () => approveMutation.mutate(leaveId),
    })
  }

  const handleReject = (leaveId: number, name: string) => {
    Dialog.confirm({
      content: `Reject leave request for ${name}?`,
      onConfirm: () => rejectMutation.mutate(leaveId),
    })
  }

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>

  if (!pending?.length) {
    return <ErrorBlock status="empty" title="All caught up!" description="No pending requests." style={{ padding: 48 }} />
  }

  return (
    <div style={{ padding: 12 }}>
      <List>
        {pending.map((leave) => {
          const employeeName = leave.employee_id?.[1] || 'Employee'
          return (
            <List.Item
              key={leave.id}
              description={
                <div>
                  <div style={{ fontSize: 13, color: '#999', marginTop: 4 }}>
                    {formatDate(leave.request_date_from)} → {formatDate(leave.request_date_to)} ({leave.number_of_days} days)
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    <Button
                      size="small"
                      color="success"
                      onClick={() => handleApprove(leave.id, employeeName)}
                      loading={approveMutation.isPending}
                    >
                      Approve
                    </Button>
                    <Button
                      size="small"
                      color="danger"
                      onClick={() => handleReject(leave.id, employeeName)}
                      loading={rejectMutation.isPending}
                    >
                      Reject
                    </Button>
                  </div>
                </div>
              }
            >
              <div>
                <span style={{ fontWeight: 'bold' }}>{employeeName}</span>
                <span style={{ fontSize: 13, color: '#666', marginLeft: 8 }}>
                  {leave.holiday_status_id?.[1] || 'Leave'}
                </span>
              </div>
            </List.Item>
          )
        })}
      </List>
    </div>
  )
}
