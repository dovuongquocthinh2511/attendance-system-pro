import { List, Tag, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'
import { formatDate } from '../../utils/format'

const stateColors: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: 'Draft' },
  confirm: { color: 'warning', label: 'Pending' },
  validate: { color: 'success', label: 'Approved' },
  refuse: { color: 'danger', label: 'Rejected' },
}

export default function LeaveHistory() {
  const { data: leaves, isLoading } = useQuery({
    queryKey: ['leave', 'history'],
    queryFn: () => leaveApi.getHistory().then((r) => r.data.data),
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={8} animated /></div>

  if (!leaves?.length) {
    return <ErrorBlock status="empty" title="No leave requests yet" style={{ padding: 48 }} />
  }

  return (
    <div style={{ padding: 12 }}>
      <List>
        {leaves.map((leave) => {
          const state = stateColors[leave.state] || stateColors.draft
          return (
            <List.Item
              key={leave.id}
              description={
                <div style={{ fontSize: 13, color: '#999', marginTop: 4 }}>
                  {formatDate(leave.request_date_from)} → {formatDate(leave.request_date_to)}
                  {leave.name && <div style={{ marginTop: 2 }}>{leave.name}</div>}
                </div>
              }
              extra={<Tag color={state.color as any}>{state.label}</Tag>}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 'bold' }}>
                  {leave.holiday_status_id?.[1] || 'Leave'}
                </span>
                <span style={{ fontSize: 13, color: '#666' }}>{leave.number_of_days} days</span>
              </div>
            </List.Item>
          )
        })}
      </List>
    </div>
  )
}
