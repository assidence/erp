import React, { useState } from 'react'
import { Upload, Button, Image, message } from 'antd'
import { UploadOutlined } from '@ant-design/icons'

export default function ImageUpload({ maxCount = 5, value = [], onChange }) {
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewImage, setPreviewImage] = useState('')
  
  const fileList = (value || []).map((url, i) => ({
    uid: i,
    name: url,
    status: 'done',
    url: url
  }))
  
  const handleChange = ({ fileList: newList }) => {
    const urls = newList.filter(f => f.status === 'done').map(f => f.url || f.response?.url)
    onChange?.(urls)
  }
  
  const handlePreview = (file) => {
    setPreviewImage(file.url || file.response?.url || '')
    setPreviewOpen(true)
  }
  
  const uploadProps = {
    name: 'file',
    action: '/api/upload/',
    listType: 'picture-card',
    fileList,
    onChange: handleChange,
    onPreview: handlePreview,
    beforeUpload: (file) => {
      const isImg = file.type.startsWith('image/')
      if (!isImg) message.error('只能上传图片文件')
      return isImg
    }
  }
  
  return (
    <div>
      <Upload {...uploadProps} multiple>
        {fileList.length < maxCount && <Button icon={<UploadOutlined />}>上传图片</Button>}
      </Upload>
      <Image style={{ display: 'none' }} src={previewImage} preview={{ open: previewOpen, src: previewImage }} />
    </div>
  )
}
