import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, DatePicker, message, Tag, Drawer, Descriptions, Timeline, Card, Statistic, Row, Col } from 'antd'
import { PlusOutlined, SearchOutlined, HistoryOutlined, InboxOutlined, SendOutlined, AppstoreOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { castingInApi, foundryApi, castingApi, customerApi, castingInventoryApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

function CastingInventory() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [transactionDrawer, setTransactionDrawer] = useState(false)
  const [selectedCasting, setSelectedCasting] = useState(null)

  // Casting inventory overview
  const { data: inventory, isLoading: invLoading } = useQuery({
    queryKey: ['casting-inventory'],
    queryFn: () => castingInventoryApi.list()
  })

  // Transaction history for selected casting
  const { data: transactions, isLoading: txLoading } = useQuery({
    queryKey: ['casting-transactions', selectedCasting?.id],
    queryFn: () => castingInventoryApi.getTransactions(selectedCasting.id),
    enabled: !!selectedCasting?.id
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
      queryClient.invalidateQueries(['casting-inventory'])
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
      queryClient.invalidateQueries(['casting-inventory'])
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
      queryClient.invalidateQueries(['casting-inventory'])
      message.success('删除成功')
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '删除失败')
    }
  })

  const handleAdd = () => {
    setEditingId(null)
    setIsModalOpen(true)
    form.resetFields()
    form.setFieldsValue({ status: 'pending' })
  }

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

  const openTransactions = (castingId, castingName) => {
    setSelectedCasting({ id: castingId, name: castingName })
    setTransactionDrawer(true)
  }

  // Merge inventory data with search
  const filteredItems = (inventory?.items || []).filter(item =>
    !searchText ||
    item.casting_name?.includes(searchText) ||
    item.casting_part_number?.includes(searchText)
  )

  const paginatedItems = filteredItems.slice((page - 1) * pageSize, page * pageSize)

  // Compute totals for stat cards
  const totalIncoming = (inventory?.items || []).reduce((s, i) => s + i.incoming, 0)
  const totalAllocated = (inventory?.items || []).reduce((s, i) => s + i.allocated, 0)
  const totalAvailable = (inventory?.items || []).reduce((s, i) => s + i.available, 0)

  const getStatusTag = (status) => {
    const colors = { pending: 'orange', approved: 'green', rejected: 'red' }
    const labels = { pending: '待审核', approved: '已审核', rejected: '已拒绝' }
    return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
  }

  const inventoryColumns = [
    {
      title: '零件编码',
      dataIndex: 'casting_part_number',
      key: 'casting_part_number',
      width: 120,
      render: (v, r) => (
        <a onClick={() => openTransactions(r.casting_id, r.casting_name)}>
          {v} <HistoryOutlined style={{ fontSize: 11, marginLeft: 4 }} />
        </a>
      )
    },
    {
      title: '零件名称',
      dataIndex: 'casting_name',
      key: 'casting_name',
      width: 150,
    },
    {
      title: '入库数量',
      dataIndex: 'incoming',
      key: 'incoming',
      width: 100,
      render: (v) => <span style={{ color: '#52c41a' }}>{Number(v).toFixed(2)}</span>
    },
    {
      title: '已分配',
      dataIndex: 'allocated',
      key: 'allocated',
      width: 100,
      render: (v) => <span style={{ color: '#faad14' }}>{Number(v).toFixed(2)}</span>
    },
    {
      title: '已出库',
      dataIndex: 'shipped',
      key: 'shipped',
      width: 100,
      render: (v) => <span style={{ color: '#ff4d4f' }}>{Number(v).toFixed(2)}</span>
    },
    {
      title: '可用库存',
      dataIndex: 'available',
      key: 'available',
      width: 100,
      render: (v) => (
        <span style={{
          color: v > 0 ? '#1677ff' : '#ff4d4f',
          fontWeight: v <= 0 ? 'bold' : 'normal'
        }}>
          {Number(v).toFixed(2)}
        </span>
      )
    },
    {
      title: '单价',
      dataIndex: 'latest_price',
      key: 'latest_price',
      width: 90,
      render: (v) => v ? '¥' + Number(v).toFixed(2) : '-'
    },
  ]

  // 入库记录表格列
  const { data: castingIns } = useQuery({
    queryKey: ['casting-ins', page, pageSize, searchText],
    queryFn: () => castingInApi.list({ page, page_size: pageSize, search: searchText })
  })

  const ciItems = (castingIns?.items || []).map(r => ({
    ...r,
    _foundry_name: foundries?.items?.find(f => f.id === r.foundry_id)?.name || r.foundry_id || '-',
  }))

  const ciColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '交货单号', dataIndex: 'delivery_note_no', key: 'delivery_note_no' },
    { title: '铸造厂', dataIndex: 'foundry_name', key: 'foundry_name', width: 120 },
    { title: '铸件', dataIndex: 'casting_name', key: 'casting_name',
      render: (_, r) => r.casting_name ? `${r.casting_name} (${r.casting_part_number})` : r.casting_id },
    { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80 },
    { title: '入库日期', dataIndex: 'incoming_date', key: 'incoming_date', width: 120 },
    { title: '状态', dataIndex: 'status', key: 'status', render: getStatusTag },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => handleEdit(record)}>编辑</Button>
          <Button size="small" danger onClick={() => deleteMutation.mutate(record.id)}>删除</Button>
        </Space>
      )
    }
  ]

  const selectedCustomerId = Form.useWatch('customer_id', form)
  const filteredCastings = (allCastings?.items || []).filter(c => c.customer_id === selectedCustomerId)

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>铸件库存</h1>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            记录入库
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="总入库"
              value={totalIncoming}
              precision={2}
              prefix={<InboxOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="已分配"
              value={totalAllocated}
              precision={2}
              prefix={<AppstoreOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="可用库存"
              value={totalAvailable}
              precision={2}
              prefix={<InboxOutlined style={{ color: '#1677ff' }} />}
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="铸件种类"
              value={inventory?.total || 0}
              prefix={<AppstoreOutlined style={{ color: '#722ed1' }} />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 库存概览表格 */}
      <Card title="库存明细" size="small" style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 12 }}>
          <Input
            placeholder="搜索零件编码或名称..."
            prefix={<SearchOutlined />}
            style={{ width: 250 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>
        <Table
          columns={inventoryColumns}
          dataSource={paginatedItems}
          rowKey="casting_id"
          loading={invLoading}
          pagination={false}
          size="small"
        />
        {filteredItems.length > pageSize && (
          <div style={{ marginTop: 8, textAlign: 'right' }}>
            <span>共 {filteredItems.length} 种零件，</span>
            <Button size="small" onClick={() => setPageSize(p => p + 10)}>加载更多</Button>
          </div>
        )}
      </Card>

      {/* 入库记录表格 */}
      <Card title="入库流水记录" size="small">
        <Table
          columns={ciColumns}
          dataSource={ciItems}
          rowKey="id"
          loading={castingIns?.isLoading}
          pagination={{
            current: page,
            pageSize,
            total: castingIns?.total || 0,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p, ps) => { setPage(p); setPageSize(ps) }
          }}
        />
      </Card>

      {/* 新增/编辑入库记录 */}
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
              {(customers?.items || []).map(c => (
                <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="foundry_id" label="铸造厂" rules={[{ required: true }]}>
            <Select placeholder="选择铸造厂" showSearch optionFilterProp="children">
              {(foundries?.items || []).map(f => (
                <Select.Option key={f.id} value={f.id}>
                  {f.name} {f.contact_person ? `(${f.contact_person})` : ''}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="casting_id" label="铸件" rules={[{ required: true }]}
            dependencies={['customer_id']}>
            <Select placeholder="先选择客户，再选择铸件" showSearch optionFilterProp="children" allowClear>
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
          <Form.Item name="status" label="状态">
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

      {/* 流水账抽屉 */}
      <Drawer
        title={selectedCasting ? `${selectedCasting.name} — 库存流水` : '库存流水'}
        open={transactionDrawer}
        onClose={() => { setTransactionDrawer(false); setSelectedCasting(null) }}
        width={500}
      >
        {transactions && (
          <>
            {transactions.casting && (
              <Descriptions column={2} size="small" bordered style={{ marginBottom: 16 }}>
                <Descriptions.Item label="零件编码">{transactions.casting.part_number}</Descriptions.Item>
                <Descriptions.Item label="零件名称">{transactions.casting.name}</Descriptions.Item>
              </Descriptions>
            )}
            {transactions.transactions && transactions.transactions.length > 0 ? (
              <Timeline
                items={transactions.transactions.map(tx => ({
                  color: tx.type === 'incoming' ? 'green' : 'red',
                  children: (
                    <div>
                      <div style={{ fontWeight: 500 }}>
                        {tx.type === 'incoming' ? (
                          <InboxOutlined style={{ color: '#52c41a', marginRight: 6 }} />
                        ) : (
                          <SendOutlined style={{ color: '#ff4d4f', marginRight: 6 }} />
                        )}
                        {tx.source} —{' '}
                        <span style={{ color: tx.type === 'incoming' ? '#52c41a' : '#ff4d4f', fontWeight: 'bold' }}>
                          {tx.type === 'incoming' ? '+' : ''}{tx.quantity}
                        </span>
                      </div>
                      <div style={{ color: '#999', fontSize: 12 }}>
                        单号：{tx.ref_no} | 日期：{tx.date ? dayjs(tx.date).format('YYYY-MM-DD') : '-'}
                      </div>
                      {tx.status && (
                        <div style={{ marginTop: 2 }}>
                          {getStatusTag(tx.status)}
                        </div>
                      )}
                      {tx.notes && (
                        <div style={{ color: '#666', fontSize: 12, marginTop: 2 }}>备注：{tx.notes}</div>
                      )}
                    </div>
                  )
                }))}
              />
            ) : (
              <div style={{ textAlign: 'center', color: '#999', padding: '32px 0' }}>
                暂无流水记录
              </div>
            )}
          </>
        )}
      </Drawer>
    </div>
  )
}

export default CastingInventory
