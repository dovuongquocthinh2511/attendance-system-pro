import { List, Tag, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../../api/profile'
import { formatDate } from '../../utils/format'

const stateColors: Record<string, string> = {
  open: 'success',
  draft: 'default',
  close: 'danger',
}

export default function ContractView() {
  const { data: contract, isLoading, error } = useQuery({
    queryKey: ['profile', 'contract'],
    queryFn: () => profileApi.getContract().then((r) => r.data.data),
  })

  if (isLoading) return <div style={{ padding: 16 }}><Skeleton.Paragraph lineCount={6} animated /></div>
  if (error || !contract) return <ErrorBlock status="empty" title="No contract found" style={{ padding: 48 }} />

  return (
    <div style={{ padding: 16 }}>
      <List header="Contract Details">
        <List.Item extra={contract.name}>Contract</List.Item>
        <List.Item extra={
          <Tag color={(stateColors[contract.state] || 'default') as any}>
            {contract.state}
          </Tag>
        }>Status</List.Item>
        <List.Item extra={contract.wage?.toLocaleString()}>Wage</List.Item>
        <List.Item extra={formatDate(contract.date_start)}>Start Date</List.Item>
        <List.Item extra={contract.date_end ? formatDate(contract.date_end) : '—'}>End Date</List.Item>
        <List.Item extra={contract.job_id?.[1] || '—'}>Job Position</List.Item>
        <List.Item extra={contract.department_id?.[1] || '—'}>Department</List.Item>
      </List>
    </div>
  )
}
