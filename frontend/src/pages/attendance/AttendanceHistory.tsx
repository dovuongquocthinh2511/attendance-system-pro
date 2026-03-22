import { useState } from 'react'
import { Tabs, List, Tag, Card, Picker, Skeleton, ErrorBlock } from 'antd-mobile'
import { useQuery } from '@tanstack/react-query'
import { attendanceApi } from '../../api/attendance'
import { formatDate, formatTime, formatHours, googleMapsUrl } from '../../utils/format'

const currentDate = new Date()
const monthColumns = [
  Array.from({ length: 12 }, (_, i) => ({ label: `Month ${i + 1}`, value: i + 1 })),
  Array.from({ length: 5 }, (_, i) => ({ label: `${currentDate.getFullYear() - 2 + i}`, value: currentDate.getFullYear() - 2 + i })),
]

export default function AttendanceHistory() {
  const [month, setMonth] = useState(currentDate.getMonth() + 1)
  const [year, setYear] = useState(currentDate.getFullYear())
  const [pickerVisible, setPickerVisible] = useState(false)

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['attendance', 'history'],
    queryFn: () => attendanceApi.getHistory(50).then((r) => r.data.data),
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['attendance', 'summary', month, year],
    queryFn: () => attendanceApi.getSummary(month, year).then((r) => r.data.data),
  })

  return (
    <div>
      <Tabs defaultActiveKey="history">
        <Tabs.Tab title="History" key="history">
          <div style={{ padding: 12 }}>
            {historyLoading ? (
              <Skeleton.Paragraph lineCount={8} animated />
            ) : !history?.length ? (
              <ErrorBlock status="empty" title="No records yet" description="Check in to start tracking." />
            ) : (
              <List>
                {history.map((record) => (
                  <List.Item
                    key={record.id}
                    description={
                      <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                        {record.in_latitude && record.in_longitude && (
                          <div>
                            Check-in: <a href={googleMapsUrl(record.in_latitude, record.in_longitude)} target="_blank" rel="noopener noreferrer">View location</a>
                          </div>
                        )}
                        {record.out_latitude && record.out_longitude && (
                          <div>
                            Check-out: <a href={googleMapsUrl(record.out_latitude, record.out_longitude)} target="_blank" rel="noopener noreferrer">View location</a>
                          </div>
                        )}
                        {record.in_mode && <Tag style={{ marginTop: 4 }}>{record.in_mode}</Tag>}
                      </div>
                    }
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{formatDate(record.check_in)}</div>
                        <div style={{ fontSize: 13, color: '#666' }}>
                          {formatTime(record.check_in)} → {record.check_out ? formatTime(record.check_out) : '—'}
                        </div>
                      </div>
                      <Tag color="primary">
                        {record.worked_hours ? formatHours(record.worked_hours) : '—'}
                      </Tag>
                    </div>
                  </List.Item>
                ))}
              </List>
            )}
          </div>
        </Tabs.Tab>

        <Tabs.Tab title="Summary" key="summary">
          <div style={{ padding: 16 }}>
            <Card
              style={{ borderRadius: 12, marginBottom: 16, cursor: 'pointer' }}
              onClick={() => setPickerVisible(true)}
            >
              <div style={{ textAlign: 'center', fontSize: 16, fontWeight: 'bold' }}>
                Month {month} / {year}
              </div>
              <div style={{ textAlign: 'center', fontSize: 13, color: '#999' }}>Tap to change</div>
            </Card>

            <Picker
              columns={monthColumns}
              visible={pickerVisible}
              onClose={() => setPickerVisible(false)}
              value={[month, year]}
              onConfirm={(val) => {
                setMonth(val[0] as number)
                setYear(val[1] as number)
              }}
            />

            {summaryLoading ? (
              <Skeleton.Paragraph lineCount={4} animated />
            ) : summary ? (
              <Card style={{ borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center', padding: '16px 0' }}>
                  <div>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: '#1677ff' }}>
                      {formatHours(summary.total_hours)}
                    </div>
                    <div style={{ fontSize: 13, color: '#999' }}>Total Hours</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: '#00b578' }}>
                      {summary.attendance_count}
                    </div>
                    <div style={{ fontSize: 13, color: '#999' }}>Days</div>
                  </div>
                </div>
              </Card>
            ) : (
              <ErrorBlock status="empty" title="No data" description="No attendance records for this period." />
            )}
          </div>
        </Tabs.Tab>
      </Tabs>
    </div>
  )
}
