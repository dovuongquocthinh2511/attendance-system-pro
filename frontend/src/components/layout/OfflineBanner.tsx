import { useContext } from 'react'
import { AppContext } from '../../contexts/AppContext'

export default function OfflineBanner() {
  const app = useContext(AppContext)
  if (!app || app.isOnline) return null

  return (
    <div
      style={{
        background: '#ff8f1f',
        color: 'white',
        textAlign: 'center',
        padding: '6px 16px',
        fontSize: 13,
      }}
    >
      No internet connection. Some features are unavailable.
    </div>
  )
}
