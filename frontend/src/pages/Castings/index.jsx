import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, message, Popconfirm, Upload, Image, Popover } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, DownloadOutlined, PaperClipOutlined, UploadOutlined, FileOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { castingApi, customerApi, attachmentApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

function Castings() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [isAttachmentModalOpen, setIsAttachmentModalOpen] = useState(false)
  const [attachmentCastingId, setAttachmentCastingId] = useState(null)

  const { data, isLoading } = useQuery({
    queryKey: ['castings', page, pageSize, searchText],
    queryFn: async () => {
      const res = await castingApi.list({ page, page_size: pageSize, search: searchText })
      return res
    }
  })

  const { data: customers } = useQuery({
    queryKey: ['customers-for-castings'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data: attachmentsData, refetch: refetchAttachments } = useQuery({
    queryKey: ['attachments', 'castings', attachmentCastingId],
    queryFn: () => attachmentApi.listByEntity('castings', attachmentCastingId),
    enabled: !!attachmentCastingId,
  })

  const createMutation = useMutation({
    mutationFn: (data) => castingApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['castings'] })
      message.success('铸造件创建成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '创建失败')
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => castingApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['castings'] })
      message.success('铸造件更新成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '更新失败')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => castingApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['castings'] })
      message.success('删除成功')
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '删除失败')
    }
  })

  const uploadMutation = useMutation({
    mutationFn: ({ file, description }) =>
      attachmentApi.upload('castings', attachmentCastingId, file, description),
    onSuccess: () => {
      message.success('附件上传成功')
      refetchAttachments()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '上传失败')
    }
  })

  const deleteAttachmentMutation = useMutation({
    mutationFn: (id) => attachmentApi.delete(id),
    onSuccess: () => {
      message.success('附件已删除')
      refetchAttachments()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '删除失败')
    }
  })

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingId(null)
    form.resetFields()
  }

  const handleEdit = (record) => {
    setEditingId(record.id)
    setIsModalOpen(true)
    form.setFieldsValue(record)
  }

  const handleSubmit = (values) => {
    const id = editingId
    if (id) {
      updateMutation.mutate({ id, data: values })
    } else {
      createMutation.mutate(values)
    }
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '所属客户', dataIndex: 'customer_name' },
      { title: '零件编码', dataIndex: 'part_number' },
      { title: '零件名称', dataIndex: 'name' },
      { title: '描述', dataIndex: 'description' },
      { title: '最新价格', dataIndex: 'latest_price' },
    ]
    const exportData = (data?.items || []).map(c => ({
      ...c,
      customer_name: customers?.items?.find(cu => cu.id === c.customer_id)?.name || c.customer_id,
      latest_price: c.latest_price != null ? '¥' + Number(c.latest_price).toFixed(2) : '',
    }))
    exportToExcel(exportCols, exportData, '铸件管理')
  }

  const openAttachmentModal = (castingId) => {
    setAttachmentCastingId(castingId)
    setIsAttachmentModalOpen(true)
  }

  const isImageFile = (mimeType) => {
    return mimeType && mimeType.startsWith('image/')
  }

  const getFileUrl = (att) => {
    const relativePath = att.file_path.replace('/home/ubuntu/erp/uploads/', '')
    return '/uploads/' + relativePath
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '所属客户', dataIndex: 'customer_id', key: 'customer_id', width: 120,
      render: (cid) => customers?.items?.find(cu => cu.id === cid)?.name || cid || '-'
    },
    { title: '零件编码', dataIndex: 'part_number', key: 'part_number' },
    { title: '零件名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: '最新价格', dataIndex: 'latest_price', key: 'latest_price', width: 100,
      render: (v) => v ? '¥' + Number(v).toFixed(2) : '-' },
    {
      title: '附件',
      key: 'attachments',
      width: 80,
      render: (_, record) => (
        <Button size="small" icon={<PaperClipOutlined />} onClick={() => openAttachmentModal(record.id)}>
          附件
        </Button>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => deleteMutation.mutate(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>铸造件管理</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            新增铸造件
          </Button>
        </Space>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索铸造件名称或编码..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => { setSearchText(e.target.value); setPage(1) }}
        />
      </div>

      <Table
        columns={columns}
        dataSource={(data?.items ?? [])}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total ?? 0,
          showSizeChanger: true,
          showTotal: (total) => '共 ' + total + ' 条',
          onChange: (p, ps) => { setPage(p); setPageSize(ps) }
        }}
      />

      <Modal
        title={editingId ? '编辑铸造件' : '新增铸造件'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="customer_id" label="所属客户" rules={[{ required: true }]}>
            <Select placeholder="选择客户" showSearch optionFilterProp="children">
              {(customers?.items ?? []).map(c => (
                <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="part_number" label="零件编码" rules={[{ required: true }]}>
            <Input placeholder="如：HX-001" />
          </Form.Item>
          <Form.Item name="name" label="零件名称" rules={[{ required: true }]}>
            <Input placeholder="如：发动机声异体" />
          </Form.Item>
          <Form.Item name="latest_price" label="最新采购单价">
            <Input type="number" placeholder="如：88.50" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={createMutation.isPending || updateMutation.isPending}>
              提交
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="附件管理"
        open={isAttachmentModalOpen}
        onCancel={() => { setIsAttachmentModalOpen(false); setAttachmentCastingId(null) }}
        footer={null}
        width={700}
      >
        <div style={{ marginBottom: 16 }}>
          <Upload.Dragger
            beforeUpload={(file) => { uploadMutation.mutate({ file, description: '' }); return false }}
            showUploadList={false}
            disabled={uploadMutation.isPending}
            multiple
          >
            <p className="ant-upload-drag-icon">
              <UploadOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件上传</p>
            <p className="ant-upload-hint">支持图片、PDF、Word、Excel等文件</p>
          </Upload.Dragger>
        </div>

        {(attachmentsData ?? []).length === 0 ? (
          <div style={{ textAlign: 'center', color: '#999', padding: '32px 0' }}>
            <FileOutlined style={{ fontSize: 32, marginBottom: 8 }} />
            <div>暂无附件</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
            {(attachmentsData ?? []).map(att => (
              <div key={att.id} style={{ width: 120, border: '1px solid #f0f0f0', borderRadius: 8, overflow: 'hidden', background: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
                {isImageFile(att.mime_type) ? (
                  <Popover content={<Image src={getFileUrl(att)} style={{ maxWidth: 400 }} />} title={att.file_name} trigger="click">
                    <div style={{ height: 100, overflow: 'hidden', cursor: 'pointer', background: '#fafafa' }}>
                      <img src={getFileUrl(att)} alt={att.file_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    </div>
                  </Popover>
                ) : (
                  <div style={{ height: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f5ff', cursor: 'pointer' }}
                    onClick={() => window.open(getFileUrl(att), '_blank')}>
                    <FileOutlined style={{ fontSize: 36, color: '#1677ff' }} />
                  </div>
                )}
                <div style={{ padding: '6px 8px', borderTop: '1px solid #f0f0f0' }}>
                  <div style={{ fontSize: 11, color: '#666', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={att.file_name}>{att.file_name}</div>
                  <div style={{ fontSize: 10, color: '#999' }}>{att.file_size ? (att.file_size / 1024).toFixed(1) + ' KB' : ''}</div>
                  <Popconfirm title="确定删除此附件？" onConfirm={() => deleteAttachmentMutation.mutate(att.id)} okText="删除" cancelText="取消">
                    <Button type="text" size="small" danger style={{ padding: '0 0', fontSize: 11 }}>删除</Button>
                  </Popconfirm>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Castings
