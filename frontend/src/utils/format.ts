import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'

dayjs.extend(duration)

export function formatDate(date: string): string {
  return dayjs(date).format('MMM DD, YYYY')
}

export function formatTime(datetime: string): string {
  return dayjs(datetime).format('HH:mm')
}

export function formatDateTime(datetime: string): string {
  return dayjs(datetime).format('MMM DD, YYYY HH:mm')
}

export function formatDuration(seconds: number): string {
  const d = dayjs.duration(seconds, 'seconds')
  const hours = Math.floor(d.asHours())
  const minutes = d.minutes()
  return `${hours}h ${minutes}m`
}

export function formatHours(hours: number): string {
  return `${hours.toFixed(1)}h`
}

export function googleMapsUrl(lat: number, lng: number): string {
  return `https://maps.google.com/?q=${lat},${lng}`
}
