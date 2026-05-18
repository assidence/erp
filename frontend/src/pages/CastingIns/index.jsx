import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, DatePicker, message, Tag } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { castingInApi, foundryApi, castingApi, customerApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

function CastingIns() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['casting-ins', page, pageSize, searchText],
    queryFn: async () => {
      const res = await castingInApi.list({ page, page_size: pageSize, search: searchText })
      return res
    }
  })

  const { data: customers } = useQuery({
    queryKey: ['customers-for-casting-ins'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data: foundries } = useQuery({
    queryKey: ['foundries-for-casting-ins'],
    queryFn: () => foundryApi.list({ page: 1, page_size: 100 })
  })

  const { data: allCastings } = useQuery({
    queryKey: ['castings-for-casting-ins'],
    queryFn: () => castingApi.list({ page: 1, page_size: 500 })
  })

  const createMutation = useMutation({
    mutationFn: (data) => castingInApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['casting-ins'])
      message.success('入库记录创建成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '创建失败')
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => castingInApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['casting-ins'])
      message.success('入库记录更新成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '更新失败')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => castingInApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['casting-ins'])
      message.success('删除成功')
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
      ...record,
      incoming_date: record.incoming_date ? dayjs(record.incoming_date) : null,
    })
  }

  const handleSubmit = (values) => {
    const payload = {
      ...values,
      incoming_date: values.incoming_date ? values.incoming_date.format('YYYY-MM-DDTHH:mm:ss') : null,
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const getStatusTag = (status) => {
    const colors = { pending: 'orange', approved: 'green', rejected: 'red' }
    const labels = { pending: '待审核', approved: '已审核', rejected: '已拒绝' }
    return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '交货单号', dataIndex: 'delivery_note_no' },
      { title: '客户', dataIndex: 'customer_name' },
      { title: '铸造厂', dataIndex: 'foundry_name' },
      { title: '铸件', dataIndex: 'casting_name' },
      { title: '零件号', dataIndex: 'casting_part_number' },
      { title: '数量', dataIndex: 'quantity' },
      { title: '入库日期', dataIndex: 'incoming_date' },
      { title: '收货人', dataIndex: 'received_by' },
      { title: '状态', dataIndex: 'status' },
      { title: '备注', dataIndex: 'notes' },
    ]
    const exportData = (data?.items || []).map(r => ({
      ...r,
      customer_name: customers?.items?.find(c => c.id === r.customer_id)?.name || r.customer_id,
      incoming_date: r.incoming_date ? r.incoming_date.slice(0, 10) : '',
      status: getStatusTag(r.status)?.props?.children || r.status,
    }))
    exportToExcel(exportCols, exportData, '铸件入库')
  }

  // Compute name fields for table display
  const ciItems = (data?.items ?? []).map(r => ({
    ...r,
    _customer_name: customers?.items?.find(c => c.id === r.customer_id)?.name || r.customer_id || '-',
  }))

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '交货单号', dataIndex: 'delivery_note_no', key: 'delivery_note_no' },
    { title: '客户', dataIndex: '_customer_name', key: 'customer_id', width: 100 },
    { title: '铸造厂', dataIndex: 'foundry_name', key: 'foundry_name', width: 120 },
    { title: '铸件', dataIndex: 'casting_name', key: 'casting_name',
      render: (_, r) => r.casting_name ? `${r.casting_name} (${r.casting_part_number || r.casting_id})` : r.casting_id },
    { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80 },
    { title: '入库日期', dataIndex: 'incoming_date', key: 'incoming_date', width: 120 },
    { title: '状态', dataIndex: 'status', key: 'status', render: getStatusTag },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => deleteMutation.mutate(record.id)}>删除</Button>
        </Space>
      )
    }
  ]

  const detailColumns = [
    { title: '铸造厂', dataIndex: 'foundry_name', key: 'foundry_name' },
    { title: '联系人', dataIndex: 'foundry_contact', key: 'foundry_contact' },
    { title: '电话', dataIndex: 'foundry_phone', key: 'foundry_phone' },
    { title: '铸件名称', dataIndex: 'casting_name', key: 'casting_name' },
    { title: '零件号', dataIndex: 'casting_part_number', key: 'casting_part_number' },
    { title: '数量', dataIndex: 'quantity', key: 'quantity' },
    { title: '入库日期', dataIndex: 'incoming_date', key: 'incoming_date' },
    { title: '收货人', dataIndex: 'received_by', key: 'received_by' },
    { title: '备注', dataIndex: 'notes', key: 'notes' },
  ]

  const expandedRowRender = (record) => (
    <div style={{ padding: '8px 0' }}>
      <Table
        size="small"
        dataSource={[record]}
        columns={detailColumns}
        rowKey="id"
        pagination={false}
        style={{ marginLeft: 32 }}
      />
    </div>
  )

  const selectedCustomerId = Form.useWatch('customer_id', form)
  const filteredCastings = (allCastings?.items ?? []).filter(c => c.customer_id === selectedCustomerId)

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>铸件入库</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            新增入库
          </Button>
        </Space>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索交货单号..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => { setSearchText(e.target.value); setPage(1) }}
        />
      </div>

      <Table
        columns={columns}
        dataSource={ciItems}
        rowKey="id"
        loading={isLoading}
        expandable={{ expandedRowRender }}
        pagination={{
          current: page,
          pageSize,
          total: data?.total ?? 0,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps) }
        }}
      />

      <Modal
        title={editingId ? '编辑入库记录' : '新增入库记录'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="delivery_note_no" label="交货单号" rules={[{ required: true }]}>
            <Input placeholder="DN-YYYY-NNN" />
          </Form.Item>
          <Form.Item name="customer_id" label="客户" rules={[{ required: true }]}>
            <Select placeholder="选择客户" showSearch optionFilterProp="children"
              onChange={() => form.setFieldValue('casting_id', null)}>
              {(customers?.items ?? []).map(c => (
                <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="foundry_id" label="铸造厂" rules={[{ required: true }]}>
            <Select placeholder="选择铸造厂" showSearch optionFilterProp="children">
              {(foundries?.items ?? []).map(f => (
                <Select.Option key={f.id} value={f.id}>
                  {f.name} {f.contact_person ? `(${f.contact_person})` : ''}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="casting_id" label="铸件" rules={[{ required: true }]}
            dependencies={['customer_id']}>
            <Select placeholder="先选择客户，再选择铸件" showSearch optionFilterProp="children"
              allowClear>
              {filteredCastings.map(c => (
                <Select.Option key={c.id} value={c.id}>
                  {c.name} ({c.part_number})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Space>
            <Form.Item name="quantity" label="数量" rules={[{ required: true }]}>
              <Input type="number" style={{ width: 150 }} />
            </Form.Item>
            <Form.Item name="incoming_date" label="入库日期" rules={[{ required: true }]}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Space>
          <Form.Item name="received_by" label="收货人">
            <Input />
          </Form.Item>
          <Form.Item name="status" label="状态" initialValue="pending">
            <Select>
              <Select.Option value="pending">待审核</Select.Option>
              <Select.Option value="approved">已审核</Select.Option>
              <Select.Option value="rejected">已拒绝</Select.Option>
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
    </div>
  )
}

export default CastingIns
