import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, DatePicker, message, Tag, Popconfirm, Upload, Image, Popover } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, MinusCircleOutlined, DownloadOutlined, PaperClipOutlined, UploadOutlined, FileOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { productionPlansApi, customerApi, castingApi, attachmentApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

function ProductionPlans() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [isAttachmentModalOpen, setIsAttachmentModalOpen] = useState(false)
  const [attachmentPlanId, setAttachmentPlanId] = useState(null)

  const { data, isLoading } = useQuery({
    queryKey: ['production-plans', page, pageSize, searchText],
    queryFn: async () => {
      const res = await productionPlansApi.list({ page, page_size: pageSize, search: searchText })
      return res
    }
  })

  const { data: customers } = useQuery({
    queryKey: ['customers-for-production'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data: allCastings } = useQuery({
    queryKey: ['castings-for-production'],
    queryFn: () => castingApi.list({ page: 1, page_size: 500 })
  })

  const { data: attachmentsData, refetch: refetchAttachments } = useQuery({
    queryKey: ['attachments', 'production_plans', attachmentPlanId],
    queryFn: () => attachmentApi.listByEntity('production_plans', attachmentPlanId),
    enabled: !!attachmentPlanId,
  })

  const createMutation = useMutation({
    mutationFn: (data) => productionPlansApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['production-plans'] })
      message.success('生产计划创建成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '创建失败')
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => productionPlansApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['production-plans'] })
      message.success('生产计划更新成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '更新失败')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => productionPlansApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['production-plans'] })
      message.success('删除成功')
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '删除失败')
    }
  })

  const uploadMutation = useMutation({
    mutationFn: ({ file, description }) =>
      attachmentApi.upload('production_plans', attachmentPlanId, file, description),
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
    form.setFieldsValue({
      plan_no: record.plan_no,
      customer_id: record.customer_id,
      start_date: record.start_date ? dayjs(record.start_date) : null,
      due_date: record.due_date ? dayjs(record.due_date) : null,
      status: record.status,
      notes: record.notes,
      items: (record.items || []).map(it => ({
        casting_id: it.casting_id,
        required_quantity: it.required_quantity,
        produced_quantity: it.produced_quantity,
        unit_price: it.unit_price
      }))
    })
  }

  const handleSubmit = (values) => {
    const id = editingId
    const payload = {
      ...values,
      start_date: values.start_date ? values.start_date.format('YYYY-MM-DDTHH:mm:ss') : null,
      due_date: values.due_date ? values.due_date.format('YYYY-MM-DDTHH:mm:ss') : null
    }
    if (id) {
      updateMutation.mutate({ id, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const getStatusTag = (status) => {
    const colors = { pending: 'blue', in_progress: 'processing', completed: 'success', delayed: 'error' }
    const labels = { pending: '计划中', in_progress: '进行中', completed: '已完成', delayed: '延期' }
    return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '计划编号', dataIndex: 'plan_no' },
      { title: '客户', dataIndex: 'customer_name' },
      { title: '零件种数', dataIndex: 'item_count' },
      { title: '开始日期', dataIndex: 'start_date' },
      { title: '截止日期', dataIndex: 'due_date' },
      { title: '状态', dataIndex: 'status_label' },
      { title: '备注', dataIndex: 'notes' },
    ]
    const exportData = (data?.items || []).map(p => {
      const statusMap = { pending: '计划中', in_progress: '进行中', completed: '已完成', delayed: '延期' }
      return {
        ...p,
        customer_name: customers?.items?.find(c => c.id === p.customer_id)?.name || p.customer_id,
        item_count: p.items?.length || 0,
        start_date: p.start_date ? p.start_date.slice(0, 10) : '',
        due_date: p.due_date ? p.due_date.slice(0, 10) : '',
        status_label: statusMap[p.status] || p.status,
      }
    })
    exportToExcel(exportCols, exportData, '生产计划')
  }

  const openAttachmentModal = (planId) => {
    setAttachmentPlanId(planId)
    setIsAttachmentModalOpen(true)
  }

  const isImageFile = (mimeType) => {
    return mimeType && mimeType.startsWith('image/')
  }

  const getFileUrl = (att) => {
    const relativePath = att.file_path.replace('/home/ubuntu/erp/uploads/', '')
    return '/uploads/' + relativePath
  }

  const itemColumns = [
    { title: '零件ID', dataIndex: 'casting_id', key: 'casting_id', width: 80 },
    { title: '需求数量', dataIndex: 'required_quantity', key: 'required_quantity', width: 100 },
    { title: '已完成', dataIndex: 'produced_quantity', key: 'produced_quantity', width: 80 },
    { title: '待发货', dataIndex: 'remaining_quantity', key: 'remaining_quantity', width: 80 },
    { title: '单价', dataIndex: 'unit_price', key: 'unit_price', width: 80,
      render: (v) => v != null ? '¥' + Number(v).toFixed(2) : '-' }
  ]

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '计划编号', dataIndex: 'plan_no', key: 'plan_no' },
    { title: '客户', dataIndex: 'customer_id', key: 'customer_id', width: 120,
      render: (cid) => customers?.items?.find(c => c.id === cid)?.name || cid || '-'
    },
    { title: '零件种数', key: 'item_count', width: 90,
      render: (_, record) => record.items?.length ?? 0 },
    { title: '开始日期', dataIndex: 'start_date', key: 'start_date', width: 120 },
    { title: '截止日期', dataIndex: 'due_date', key: 'due_date', width: 120 },
    { title: '状态', dataIndex: 'status', key: 'status', render: getStatusTag },
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
          <Popconfirm title="确认删除？" onConfirm={() => deleteMutation.mutate(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  const expandedRowRender = (record) => (
    <div style={{ padding: '8px 0' }}>
      <Table
        size="small"
        dataSource={record.items || []}
        columns={itemColumns}
        rowKey="id"
        pagination={false}
        style={{ marginLeft: 32 }}
      />
    </div>
  )

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>生产计划</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            新增计划
          </Button>
        </Space>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索计划编号..."
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
        expandable={{ expandedRowRender }}
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
        title={editingId ? '编辑生产计划' : '新增生产计划'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
        width={800}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="plan_no" label="计划编号（留空自动生成）" style={{ flex: 1 }}>
              <Input placeholder="留空则自动生成唯一编号" />
            </Form.Item>
            <Form.Item name="customer_id" label="客户" rules={[{ required: true }]} style={{ flex: 1 }}>
              <Select placeholder="选择客户" showSearch optionFilterProp="children">
                {(customers?.items ?? []).map(c => (
                  <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="start_date" label="开始日期" style={{ flex: 1 }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="due_date" label="截止日期" rules={[{ required: true }]} style={{ flex: 1 }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Form.Item label="零件明细">
            <Form.List name="items">
              {(fields, { add, remove }) => (
                <>
                  <div style={{ display: 'flex', gap: 8, fontWeight: 500, fontSize: 12, color: '#999', marginBottom: 4 }}>
                    <div style={{ width: 220 }}>零件</div>
                    <div style={{ width: 100 }}>需求数量</div>
                    <div style={{ width: 100 }}>已完成</div>
                    <div style={{ width: 100 }}>单价</div>
                    <div style={{ width: 32 }}></div>
                  </div>
                  {fields.map(({ key, name }) => (
                    <Space key={key} style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 8 }} size="small">
                      <Form.Item
                        name={[name, 'casting_id']}
                        rules={[{ required: true, message: '请选择零件' }]}
                        style={{ width: 220, marginBottom: 0 }}
                      >
                        <Select placeholder="选择零件" showSearch optionFilterProp="children"
                          onChange={(val) => {
                            const casting = allCastings?.items?.find(c => c.id === val)
                            if (casting?.latest_price != null) {
                              form.setFieldsValue({ items: { [name]: { unit_price: Number(casting.latest_price) } } })
                            }
                          }}>
                          {(allCastings?.items ?? []).map(c => (
                            <Select.Option key={c.id} value={c.id}>
                              {c.name} ({c.part_number}){c.latest_price ? ' ¥' + Number(c.latest_price).toFixed(2) : ''}
                            </Select.Option>
                          ))}
                        </Select>
                      </Form.Item>
                      <Form.Item name={[name, 'required_quantity']} rules={[{ required: true }]}
                        style={{ width: 100, marginBottom: 0 }}>
                        <Input type="number" placeholder="需求数量" />
                      </Form.Item>
                      <Form.Item name={[name, 'produced_quantity']}
                        style={{ width: 100, marginBottom: 0 }}>
                        <Input type="number" placeholder="已完成" defaultValue={0} />
                      </Form.Item>
                      <Form.Item name={[name, 'unit_price']}
                        style={{ width: 100, marginBottom: 0 }}>
                        <Input type="number" placeholder="单价" />
                      </Form.Item>
                      <Button type="text" danger icon={<MinusCircleOutlined />} onClick={() => remove(name)} />
                    </Space>
                  ))}
                  <Button type="dashed" onClick={() => add()} block style={{ marginTop: 4 }}>
                    + 添加零件
                  </Button>
                </>
              )}
            </Form.List>
          </Form.Item>

          <Form.Item name="status" label="状态" initialValue="pending">
            <Select>
              <Select.Option value="pending">计划中</Select.Option>
              <Select.Option value="in_progress">进行中</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
              <Select.Option value="delayed">延期</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} />
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
        onCancel={() => { setIsAttachmentModalOpen(false); setAttachmentPlanId(null) }}
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
            <p className="ant-upload-drag-icon"><UploadOutlined /></p>
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

export default ProductionPlans
