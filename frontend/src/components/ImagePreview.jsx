import React from 'react'
import { Image } from 'antd'

export default function ImagePreview({ images = [], count = 3 }) {
  if (!images || images.length === 0) return <span style={{ color: '#999' }}>无图片</span>
  
  const visible = images.slice(0, count)
  const extra = images.length - count
  
  return (
    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
      {visible.map((img, i) => (
        <Image
          key={i}
          src={img.url || img}
          width={40}
          height={40}
          style={{ objectFit: 'cover', borderRadius: 4 }}
          preview={{ src: img.url || img }}
        />
      ))}
      {extra > 0 && <span style={{ lineHeight: '40px', color: '#999' }}>+{extra}</span>}
    </div>
  )
}
