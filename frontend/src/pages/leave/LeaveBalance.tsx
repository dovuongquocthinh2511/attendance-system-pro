import { useNavigate } from 'react-router-dom'
import { List, ProgressBar, Button, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { leaveApi } from '../../api/leave'

export default function LeaveBalance() {
  const navigate = useNavigate()

  const { data: balances, isLoading } = useQuery({
    queryKey: ['leave', 'balance'],
    queryFn: () => leaveApi.getBalance().then((r) => r.data.data),
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={6} animated /></div>

  return (
    <div style={{ padding: 16 }}>
      {!balances?.length ? (
        <ErrorBlock status="empty" title="No leave types" description="No leave allocations found." />
      ) : (
        <List>
          {balances.map((b) => {
            const percent = b.allocated > 0 ? (b.taken / b.allocated) * 100 : 0
            return (
              <List.Item
                key={b.type_id}
                description={
                  <div style={{ marginTop: 8 }}>
                    <ProgressBar percent={percent} style={{ '--fill-color': percent > 80 ? '#ff3141' : '#1677ff' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#999', marginTop: 4 }}>
                      <span>Taken: {b.taken} days</span>
                      <span>Allocated: {b.allocated} days</span>
                    </div>
                  </div>
                }
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 'bold' }}>{b.name}</span>
                  <span style={{ color: '#1677ff', fontWeight: 'bold' }}>{b.remaining} days left</span>
                </div>
              </List.Item>
            )
          })}
        </List>
      )}
      <div style={{ padding: '16px 0' }}>
        <Button block color="primary" size="large" onClick={() => navigate('/leave/request')}>
          New Leave Request
        </Button>
      </div>
    </div>
  )
}
