import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, DatePicker, message, Tag, Popconfirm } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, MinusCircleOutlined, DownloadOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { workpieceOutApi, productionPlansApi, customerApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

// Sub-component so useWatch is called at component top-level (not inside a callback)
function OutItemRow({ name, currentItems, onRemove }) {
  const form = Form.useFormInstance()
  const planItemId = Form.useWatch(['items', name, 'production_plan_item_id'], form)
  const planItem = currentItems.find(it => it.id === planItemId)
  const availableQty = planItem ? Number(planItem.remaining_quantity) : null

  return (
    <Space key={name} style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 8 }} size="small">
      <div style={{ width: 32, lineHeight: '32px' }}>{name + 1}</div>
      <Form.Item name={[name, 'production_plan_item_id']} style={{ flex: 1, marginBottom: 0 }}>
        <Select placeholder="选择零件"
          onChange={(planItemId) => {
            const pi = currentItems.find(it => it.id === planItemId)
            if (pi) {
              form.setFieldsValue({
                items: { [name]: {
                  casting_id: pi.casting_id,
                  quantity: pi.remaining_quantity,
                  unit_price: pi.unit_price
                }}
              })
            }
          }}>
          {currentItems.map(it => (
            <Select.Option key={it.id} value={it.id} disabled={Number(it.remaining_quantity) <= 0}>
              零件ID:{it.casting_id} | 可发:{it.remaining_quantity}件 | 单价:¥{it.unit_price ?? '-'}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
      <div style={{ width: 100, lineHeight: '32px', color: '#52c41a', fontWeight: 500, textAlign: 'center' }}>
        {availableQty != null ? `${availableQty}件` : '-'}
      </div>
      <Form.Item name={[name, 'quantity']} rules={[{ required: true }]}
        style={{ width: 90, marginBottom: 0 }}>
        <Input type="number" placeholder="数量" />
      </Form.Item>
      <Form.Item name={[name, 'unit_price']}
        style={{ width: 90, marginBottom: 0 }}>
        <Input type="number" placeholder="单价" />
      </Form.Item>
      <Button type="text" danger icon={<MinusCircleOutlined />} onClick={() => onRemove(name)} />
    </Space>
  )
}

function WorkpieceOuts() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['workpiece-outs', page, pageSize, searchText],
    queryFn: async () => {
      const res = await workpieceOutApi.list({ page, page_size: pageSize, search: searchText })
      return res
    }
  })

  const { data: customers } = useQuery({
    queryKey: ['customers-for-out'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data: plans } = useQuery({
    queryKey: ['production-plans-for-out', 'all'],
    queryFn: () => productionPlansApi.list({ page: 1, page_size: 500 })
  })

  const createMutation = useMutation({
    mutationFn: (data) => workpieceOutApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workpiece-outs'] })
      message.success('出库记录创建成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '创建失败')
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => workpieceOutApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workpiece-outs'] })
      message.success('出库记录更新成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '更新失败')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => workpieceOutApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workpiece-outs'] })
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
    const plan = plans?.items?.find(p => p.id === record.production_plan_id)
    form.setFieldsValue({
      delivery_note_no: record.delivery_note_no,
      production_plan_id: record.production_plan_id,
      customer_id: record.customer_id,
      delivery_date: record.delivery_date ? dayjs(record.delivery_date) : null,
      shipping_address: record.shipping_address,
      status: record.status,
      notes: record.notes,
      items: (record.items || []).map(it => {
        const planItem = plan?.items?.find(pi => pi.id === it.production_plan_item_id)
        const available = planItem
          ? Number(planItem.remaining_quantity) + Number(it.quantity)
          : Number(it.quantity)
        return {
          production_plan_item_id: it.production_plan_item_id,
          casting_id: it.casting_id,
          quantity: available,
          unit_price: it.unit_price
        }
      })
    })
  }

  const handleSubmit = (values) => {
    const payload = {
      ...values,
      delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD') : null
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const getStatusTag = (status) => {
    const colors = { pending: 'orange', shipped: 'blue', completed: 'green', cancelled: 'red' }
    const labels = { pending: '待发货', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
    return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '交货单号', dataIndex: 'delivery_note_no' },
      { title: '客户', dataIndex: 'customer_name' },
      { title: '关联生产计划', dataIndex: 'plan_no' },
      { title: '零件种数', dataIndex: 'item_count' },
      { title: '发货日期', dataIndex: 'delivery_date' },
      { title: '发货地址', dataIndex: 'shipping_address' },
      { title: '状态', dataIndex: 'status_label' },
      { title: '备注', dataIndex: 'notes' },
    ]
    const exportData = (data?.items || []).map(r => {
      const statusMap = { pending: '待发货', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
      const plan = plans?.items?.find(p => p.id === r.production_plan_id)
      return {
        ...r,
        customer_name: customers?.items?.find(c => c.id === r.customer_id)?.name || r.customer_id,
        plan_no: plan?.plan_no || r.production_plan_id,
        delivery_date: r.delivery_date ? r.delivery_date.slice(0, 10) : '',
        status_label: statusMap[r.status] || r.status,
      }
    })
    exportToExcel(exportCols, exportData, '工件出库')
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '交货单号', dataIndex: 'delivery_note_no', key: 'delivery_note_no' },
    { title: '客户ID', dataIndex: 'customer_id', key: 'customer_id', width: 80 },
    { title: '零件种数', key: 'item_count', width: 90,
      render: (_, record) => record.items?.length ?? 0 },
    { title: '发货日期', dataIndex: 'delivery_date', key: 'delivery_date', width: 120 },
    { title: '状态', dataIndex: 'status', key: 'status', render: getStatusTag },
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

  const itemColumns = [
    { title: '零件ID', dataIndex: 'casting_id', key: 'casting_id', width: 80 },
    { title: '发货数量', dataIndex: 'quantity', key: 'quantity', width: 90 },
    { title: '单价', dataIndex: 'unit_price', key: 'unit_price', width: 80,
      render: (v) => v != null ? `¥${Number(v).toFixed(2)}` : '-' },
    { title: '小计', key: 'subtotal', width: 90,
      render: (_, r) => r.unit_price != null ? `¥${(Number(r.quantity) * Number(r.unit_price)).toFixed(2)}` : '-' }
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
        summary={() => {
          const total = (record.items || []).reduce((sum, it) => {
            return sum + (it.unit_price != null ? Number(it.quantity) * Number(it.unit_price) : 0)
          }, 0)
          return (
            <Table.Summary.Row>
              <Table.Summary.Cell index={0} colSpan={2}><strong>合计</strong></Table.Summary.Cell>
              <Table.Summary.Cell index={1}><strong>¥{total.toFixed(2)}</strong></Table.Summary.Cell>
            </Table.Summary.Row>
          )
        }}
      />
    </div>
  )

  const selectedPlanId = Form.useWatch('production_plan_id', form)
  const currentPlan = plans?.items?.find(p => p.id === selectedPlanId)
  const currentItems = currentPlan?.items || []

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>工件出库</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            新增出库
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
        dataSource={(data?.items ?? [])}
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
        title={editingId ? '编辑出库记录' : '新增出库记录'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
        width={800}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="delivery_note_no" label="交货单号" rules={[{ required: true }]}>
            <Input placeholder="如：DO-2026-001" disabled={!!editingId} />
          </Form.Item>
          <Form.Item name="production_plan_id" label="关联生产计划" rules={[{ required: true }]}
            onValuesChange={(changed) => {
              if (changed.production_plan_id) {
                const plan = plans?.items?.find(p => p.id === changed.production_plan_id)
                if (plan) {
                  form.setFieldsValue({ customer_id: plan.customer_id })
                  form.setFieldValue('items', plan.items
                    .filter(it => Number(it.remaining_quantity) > 0)
                    .map(it => ({
                      production_plan_item_id: it.id,
                      casting_id: it.casting_id,
                      quantity: it.remaining_quantity,
                      unit_price: it.unit_price
                    }))
                  )
                }
              }
            }}>
            <Select placeholder="选择生产计划" showSearch optionFilterProp="children">
              {(plans?.items ?? []).map(p => (
                <Select.Option key={p.id} value={p.id}>
                  {p.plan_no} ({p.items?.length ?? 0}种零件)
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="出库零件明细" style={{ marginBottom: 8 }}>
            <Form.List name="items">
              {(fields, { add, remove }) => (
                <>
                  <div style={{ display: 'flex', gap: 8, fontWeight: 500, fontSize: 12, color: '#999', marginBottom: 4 }}>
                    <div style={{ width: 32 }}>#</div>
                    <div style={{ flex: 1 }}>零件</div>
                    <div style={{ width: 100, textAlign: 'center' }}>可发数量</div>
                    <div style={{ width: 90 }}>发货数量</div>
                    <div style={{ width: 90 }}>单价</div>
                    <div style={{ width: 32 }}></div>
                  </div>
                  {fields.map(({ key, name }) => (
                    <OutItemRow
                      key={key}
                      name={name}
                      currentItems={currentItems}
                      onRemove={remove}
                    />
                  ))}
                  <Button type="dashed" onClick={() => add()} block style={{ marginTop: 4 }}>
                    + 添加零件行
                  </Button>
                </>
              )}
            </Form.List>
          </Form.Item>

          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="delivery_date" label="发货日期" style={{ flex: 1 }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="shipping_address" label="发货地址" style={{ flex: 1 }}>
              <Input placeholder="收货地址" />
            </Form.Item>
          </Space>
          <Form.Item name="status" label="状态" initialValue="pending">
            <Select>
              <Select.Option value="pending">待发货</Select.Option>
              <Select.Option value="shipped">已发货</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
              <Select.Option value="cancelled">已取消</Select.Option>
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

export default WorkpieceOuts
