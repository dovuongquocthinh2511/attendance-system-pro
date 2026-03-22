import { useState, useEffect } from 'react'
import { Card, Button, Toast, Result } from 'antd-mobile'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { attendanceApi } from '../../api/attendance'
import { formatTime } from '../../utils/format'
import type { CheckInRequest } from '../../types'

function useElapsedTime(startTime: string | undefined) {
  const [elapsed, setElapsed] = useState('')
  useEffect(() => {
    if (!startTime) { setElapsed(''); return }
    const update = () => {
      const diff = Date.now() - new Date(startTime).getTime()
      const hours = Math.floor(diff / 3600000)
      const minutes = Math.floor((diff % 3600000) / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      setElapsed(`${hours}h ${minutes}m ${seconds}s`)
    }
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [startTime])
  return elapsed
}

function getGeoLocation(): Promise<{ latitude: number; longitude: number } | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) { resolve(null); return }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => resolve(null),
      { timeout: 10000, enableHighAccuracy: true }
    )
  })
}

export default function AttendanceStatus() {
  const queryClient = useQueryClient()

  const { data: status, isLoading } = useQuery({
    queryKey: ['attendance', 'status'],
    queryFn: () => attendanceApi.getStatus().then((r) => r.data.data),
  })

  const elapsed = useElapsedTime(status?.check_in_time)

  const checkInMutation = useMutation({
    mutationFn: async () => {
      const geo = await getGeoLocation()
      const payload: CheckInRequest = { mode: 'manual', ...geo }
      return attendanceApi.checkIn(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance', 'status'] })
      Toast.show({ icon: 'success', content: 'Checked in successfully' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Check-in failed' })
    },
  })

  const checkOutMutation = useMutation({
    mutationFn: async () => {
      const geo = await getGeoLocation()
      const payload: CheckInRequest = { mode: 'manual', ...geo }
      return attendanceApi.checkOut(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance', 'status'] })
      Toast.show({ icon: 'success', content: 'Checked out successfully' })
    },
    onError: (error: any) => {
      Toast.show({ icon: 'fail', content: error.response?.data?.error || 'Check-out failed' })
    },
  })

  if (isLoading) {
    return <div style={{ padding: 16 }}><Card><Result status="waiting" title="Loading..." /></Card></div>
  }

  const isCheckedIn = status?.is_checked_in

  return (
    <div style={{ padding: 16 }}>
      <Card style={{ borderRadius: 12, textAlign: 'center', padding: '32px 16px' }}>
        <div style={{ fontSize: 16, color: '#666', marginBottom: 8 }}>Current Status</div>
        <div style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 8, color: isCheckedIn ? '#00b578' : '#666' }}>
          {isCheckedIn ? 'Working' : 'Not Checked In'}
        </div>
        {isCheckedIn && status?.check_in_time && (
          <>
            <div style={{ fontSize: 14, color: '#999', marginBottom: 4 }}>
              Since {formatTime(status.check_in_time)}
            </div>
            <div style={{ fontSize: 32, fontWeight: 'bold', color: '#1677ff', marginBottom: 24 }}>
              {elapsed}
            </div>
          </>
        )}
        {!isCheckedIn && <div style={{ height: 24 }} />}
        <Button
          color={isCheckedIn ? 'danger' : 'success'}
          size="large"
          block
          loading={checkInMutation.isPending || checkOutMutation.isPending}
          onClick={() => isCheckedIn ? checkOutMutation.mutate() : checkInMutation.mutate()}
          style={{ borderRadius: 8, height: 48, fontSize: 18 }}
        >
          {isCheckedIn ? 'CHECK OUT' : 'CHECK IN'}
        </Button>
      </Card>
    </div>
  )
}
