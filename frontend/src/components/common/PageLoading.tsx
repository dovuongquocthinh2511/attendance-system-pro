import { Skeleton } from 'antd-mobile'

export default function PageLoading() {
  return (
    <div style={{ padding: 16 }}>
      <Skeleton.Title animated />
      <Skeleton.Paragraph lineCount={5} animated />
    </div>
  )
}
