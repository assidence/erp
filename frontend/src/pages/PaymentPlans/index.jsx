import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, DatePicker, message, Tag, Popconfirm, Tooltip } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, WarningOutlined, CheckCircleOutlined, DownloadOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { paymentPlansApi, customerApi, workpieceOutApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

// Status config: pending(待收款) → invoiced(已开票) → paid(已收款) / partial(部分收款) / bad_debt(坏账)
const STATUS_CONFIG = {
  pending:    { color: 'orange', label: '待收款' },
  no_invoice: { color: 'purple', label: '不需开票' },
  invoiced:   { color: 'blue',   label: '已开票' },
  paid:       { color: 'green',  label: '已收款' },
  partial:    { color: 'cyan',   label: '部分收款' },
  bad_debt:   { color: 'red',    label: '坏账' },
}

function PaymentPlans() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const [filterCustomer, setFilterCustomer] = useState(null)
  const [filterStatus, setFilterStatus] = useState(null)
  const [filterOverdue, setFilterOverdue] = useState(null)  // true=已逾期, false=未逾期, null=全部
  const [filterSettled, setFilterSettled] = useState(null)  // true=已结算, false=未结算, null=全部

  const buildParams = () => {
    const p = { page, page_size: pageSize }
    if (filterCustomer) p.customer_id = filterCustomer
    if (filterStatus) p.status_filter = filterStatus
    if (filterOverdue !== null) p.overdue = filterOverdue
    if (filterSettled !== null) p.settled = filterSettled
    return p
  }

  const { data, isLoading } = useQuery({
    queryKey: ['payment-plans', page, pageSize, filterCustomer, filterStatus, filterOverdue, filterSettled],
    queryFn: async () => {
      const res = await paymentPlansApi.list(buildParams())
      return res
    }
  })

  const { data: customers } = useQuery({
    queryKey: ['customers-for-payment'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data: workpieceOuts } = useQuery({
    queryKey: ['workpiece-outs-for-payment'],
    queryFn: () => workpieceOutApi.list({ page: 1, page_size: 500 })
  })

  // Unaligned production plans
  const { data: unalignedPlans, isLoading: unalignedLoading } = useQuery({
    queryKey: ['payment-plans-unaligned'],
    queryFn: () => paymentPlansApi.getUnalignedPlans(),
    refetchInterval: 30000,
  })

  const createMutation = useMutation({
    mutationFn: (data) => paymentPlansApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['payment-plans'])
      queryClient.invalidateQueries(['payment-plans-unaligned'])
      message.success('收款计划创建成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '创建失败')
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => paymentPlansApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['payment-plans'])
      queryClient.invalidateQueries(['payment-plans-unaligned'])
      message.success('收款计划更新成功')
      handleModalClose()
    },
    onError: (err) => {
      message.error(err?.response?.data?.detail || '更新失败')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => paymentPlansApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['payment-plans'])
      queryClient.invalidateQueries(['payment-plans-unaligned'])
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
      expected_date: record.expected_date ? dayjs(record.expected_date) : null,
      actual_date: record.actual_date ? dayjs(record.actual_date) : null,
    })
  }

  const handleSubmit = (values) => {
    const payload = {
      ...values,
      expected_date: values.expected_date ? values.expected_date.format('YYYY-MM-DD') : null,
      actual_date: values.actual_date ? values.actual_date.format('YYYY-MM-DD') : null,
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const handleFilterChange = (key, value) => {
    if (key === 'customer') setFilterCustomer(value)
    if (key === 'status') setFilterStatus(value)
    if (key === 'overdue') setFilterOverdue(value ?? null)
    if (key === 'settled') setFilterSettled(value ?? null)
    setPage(1)
  }

  const getStatusTag = (status) => {
    const cfg = STATUS_CONFIG[status] || { color: 'default', label: status }
    return <Tag color={cfg.color}>{cfg.label}</Tag>
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '客户', dataIndex: 'customer_name' },
      { title: '出库单号', dataIndex: 'delivery_note_no' },
      { title: '应收金额', dataIndex: 'amount' },
      { title: '到期日', dataIndex: 'expected_date' },
      { title: '实际收款日', dataIndex: 'actual_date' },
      { title: '收款方式', dataIndex: 'payment_method' },
      { title: '状态', dataIndex: 'status_label' },
      { title: '备注', dataIndex: 'notes' },
    ]
    const exportData = (data?.items || []).map(p => ({
      ...p,
      customer_name: customers?.items?.find(c => c.id === p.customer_id)?.name || p.customer_id,
      delivery_note_no: workpieceOuts?.items?.find(w => w.id === p.workpiece_out_id)?.delivery_note_no || p.workpiece_out_id,
      expected_date: p.expected_date ? p.expected_date.slice(0, 10) : '',
      actual_date: p.actual_date ? p.actual_date.slice(0, 10) : '',
      status_label: STATUS_CONFIG[p.status]?.label || p.status,
    }))
    exportToExcel(exportCols, exportData, '收款计划')
  }

  const unalignedColumns = [
    { title: '计划编号', dataIndex: 'plan_no', key: 'plan_no', width: 130 },
    { title: '客户', dataIndex: 'customer_name', key: 'customer_name', width: 130,
      render: (name, r) => name || `客户${r.customer_id}` },
    { title: '截止日期', dataIndex: 'due_date', key: 'due_date', width: 110,
      render: (d) => d ? d.slice(0, 10) : '-' },
    { title: '计划状态', dataIndex: 'status', key: 'status', width: 90,
      render: (s) => getStatusTag(s) },
    { title: '出库记录', key: 'wo_status', width: 130,
      render: (_, r) => r.wo_count === 0
        ? <Tag>尚无出库</Tag>
        : <span>{r.completed_wo_count}/{r.wo_count} 张已完成</span> },
    { title: '未生成收款计划原因', dataIndex: 'reason', key: 'reason',
      render: (reason) => <span style={{ color: '#fa8c16' }}>{reason}</span> },
  ]

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '客户', dataIndex: 'customer_id', key: 'customer_id', width: 100,
      render: (cid) => customers?.items?.find(c => c.id === cid)?.name || cid },
    { title: '出库单号', dataIndex: 'workpiece_out_id', key: 'workpiece_out_id', width: 130,
      render: (wid) => workpieceOuts?.items?.find(w => w.id === wid)?.delivery_note_no || wid },
    {
      title: '应收金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (amount) => (
        <span style={{ color: '#1677ff', fontWeight: 500 }}>
          ¥{Number(amount)?.toLocaleString()}
        </span>
      )
    },
    { title: '到期日', dataIndex: 'expected_date', key: 'expected_date', width: 110,
      render: (d) => {
        if (!d) return <span style={{ color: '#999' }}>—</span>
        const isOverdue = new Date(d) < new Date()
        return (
          <Tooltip title={isOverdue ? '已逾期' : ''}>
            <span style={{ color: isOverdue ? '#ff4d4f' : undefined }}>
              {d.slice(0, 10)}
            </span>
          </Tooltip>
        )
      } },
    { title: '实际收款日', dataIndex: 'actual_date', key: 'actual_date', width: 110,
      render: (d) => d ? d.slice(0, 10) : <span style={{ color: '#999' }}>—</span> },
    { title: '收款方式', dataIndex: 'payment_method', key: 'payment_method', width: 100,
      render: (m) => m || <span style={{ color: '#999' }}>—</span> },
    { title: '状态', dataIndex: 'status', key: 'status', width: 90, render: getStatusTag },
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

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>收款计划</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出Excel
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            新增收款计划
          </Button>
        </Space>
      </div>

      {/* Filter row */}
      <Space wrap style={{ marginBottom: 16 }} size="middle">
        <Select
          placeholder="按客户筛选"
          allowClear
          style={{ width: 160 }}
          value={filterCustomer}
          onChange={(v) => handleFilterChange('customer', v || null)}
          options={customers?.items?.map(c => ({ value: c.id, label: c.name })) || []}
        />
        <Select
          placeholder="收款状态"
          allowClear
          style={{ width: 130 }}
          value={filterStatus}
          onChange={(v) => handleFilterChange('status', v || null)}
          options={[
            { value: 'pending', label: '待收款' },
            { value: 'no_invoice', label: '不需开票' },
            { value: 'invoiced', label: '已开票' },
            { value: 'paid', label: '已收款' },
            { value: 'partial', label: '部分收款' },
            { value: 'bad_debt', label: '坏账' },
          ]}
        />
        <Select
          placeholder="逾期状态"
          allowClear
          style={{ width: 130 }}
          value={filterOverdue}
          onChange={(v) => handleFilterChange('overdue', v)}
          options={[
            { value: true, label: '已逾期' },
            { value: false, label: '未逾期' },
          ]}
        />
        <Select
          placeholder="结算状态"
          allowClear
          style={{ width: 130 }}
          value={filterSettled}
          onChange={(v) => handleFilterChange('settled', v)}
          options={[
            { value: false, label: '未结算' },
            { value: true, label: '已结算' },
          ]}
        />
      </Space>

      {/* Unaligned Production Plans Section */}
      {unalignedPlans && unalignedPlans.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <WarningOutlined style={{ color: '#fa8c16', fontSize: 16 }} />
            <span style={{ fontWeight: 600, color: '#262626' }}>未生成收款计划的生产计划（{unalignedPlans.length}项）</span>
            <span style={{ color: '#8c8c8c', fontSize: 12 }}>— 以下生产计划尚未生成对应的收款计划，原因如下：</span>
          </div>
          <Table
            columns={unalignedColumns}
            dataSource={unalignedPlans}
            rowKey="id"
            loading={unalignedLoading}
            pagination={false}
            size="small"
            style={{ background: '#fffbe6', border: '1px solid #ffe58f', borderRadius: 6 }}
          />
        </div>
      )}

      {unalignedPlans && unalignedPlans.length === 0 && !unalignedLoading && (
        <div style={{ marginBottom: 16, padding: '8px 12px', background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 6, display: 'flex', alignItems: 'center', gap: 8 }}>
          <CheckCircleOutlined style={{ color: '#52c41a' }} />
          <span style={{ color: '#52c41a', fontWeight: 500 }}>所有生产计划均已生成收款计划</span>
        </div>
      )}

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
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
        title={editingId ? '编辑收款计划' : '新增收款计划'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="customer_id" label="客户" rules={[{ required: true }]}>
            <Select placeholder="选择客户" showSearch optionFilterProp="children">
              {(customers?.items ?? []).map(c => (
                <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="workpiece_out_id" label="关联出库单" rules={[{ required: true }]}>
            <Select placeholder="选择出库单">
              {(workpieceOuts?.items ?? []).map(w => (
                <Select.Option key={w.id} value={w.id}>
                  {w.delivery_note_no}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="amount" label="应收金额" rules={[{ required: true }]}>
            <Input type="number" prefix="¥" placeholder="0.00" />
          </Form.Item>
          <Space>
            <Form.Item name="expected_date" label="预期收款日期" style={{ flex: 1 }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="actual_date" label="实际收款日期" style={{ flex: 1 }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Space>
          <Form.Item name="payment_method" label="收款方式">
            <Select allowClear placeholder="选择收款方式">
              <Select.Option value="银行转账">银行转账</Select.Option>
              <Select.Option value="承兑汇票">承兑汇票</Select.Option>
              <Select.Option value="现金">现金</Select.Option>
              <Select.Option value="支票">支票</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="status" label="状态" initialValue="pending">
            <Select>
              <Select.Option value="pending">待收款</Select.Option>
              <Select.Option value="no_invoice">不需开票</Select.Option>
              <Select.Option value="invoiced">已开票</Select.Option>
              <Select.Option value="paid">已收款</Select.Option>
              <Select.Option value="partial">部分收款</Select.Option>
              <Select.Option value="bad_debt">坏账</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} placeholder="补充说明..." />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending || updateMutation.isPending}>
                提交
              </Button>
              <Button onClick={handleModalClose}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PaymentPlans
