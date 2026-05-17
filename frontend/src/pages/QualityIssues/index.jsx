import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, DatePicker, message, Tag, Popconfirm } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { qualityIssuesApi, customerApi, castingApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

function QualityIssues() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['quality-issues', page, pageSize, searchText],
    queryFn: async () => {
      const res = await qualityIssuesApi.list({ page, page_size: pageSize, search: searchText })
      return res
    }
  })

  const { data: customers } = useQuery({
    queryKey: ['customers-for-qi'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data: castings } = useQuery({
    queryKey: ['castings-for-qi'],
    queryFn: () => castingApi.list({ page: 1, page_size: 100 })
  })

  const createMutation = useMutation({
    mutationFn: (data) => qualityIssuesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['quality-issues'])
      message.success('质量问题记录创建成功')
      handleModalClose()
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => qualityIssuesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['quality-issues'])
      message.success('质量问题记录更新成功')
      handleModalClose()
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => qualityIssuesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['quality-issues'])
      message.success('删除成功')
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
      issue_date: record.issue_date ? dayjs(record.issue_date) : null,
      resolved_at: record.resolved_at ? dayjs(record.resolved_at) : null
    })
  }

  const handleSubmit = (values) => {
    const payload = {
      ...values,
      issue_date: values.issue_date ? values.issue_date.format('YYYY-MM-DD') : null,
      resolved_at: values.resolved_at ? values.resolved_at.format('YYYY-MM-DD') : null
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const getSeverityTag = (severity) => {
    const colors = { low: 'green', medium: 'orange', high: 'red', critical: 'purple' }
    const labels = { low: '轻微', medium: '一般', high: '严重', critical: '危急' }
    return <Tag color={colors[severity] || 'default'}>{labels[severity] || severity}</Tag>
  }

  const getStatusTag = (status) => {
    const colors = { open: 'red', investigating: 'orange', resolved: 'green', closed: 'blue' }
    const labels = { open: '待处理', investigating: '调查中', resolved: '已解决', closed: '已关闭' }
    return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '客户', dataIndex: 'customer_name' },
      { title: '铸件', dataIndex: 'casting_name' },
      { title: '问题类型', dataIndex: 'issue_type' },
      { title: '描述', dataIndex: 'description' },
      { title: '严重程度', dataIndex: 'severity_label' },
      { title: '状态', dataIndex: 'status_label' },
      { title: '问题日期', dataIndex: 'issue_date' },
      { title: '解决日期', dataIndex: 'resolved_at' },
      { title: '备注', dataIndex: 'notes' },
    ]
    const severityMap = { low: '轻微', medium: '一般', high: '严重', critical: '危急' }
    const statusMap = { open: '待处理', investigating: '调查中', resolved: '已解决', closed: '已关闭' }
    const exportData = (data?.items || []).map(r => ({
      ...r,
      customer_name: customers?.items?.find(c => c.id === r.customer_id)?.name || r.customer_id,
      casting_name: castings?.items?.find(c => c.id === r.casting_id)?.name || r.casting_id,
      severity_label: severityMap[r.severity] || r.severity,
      status_label: statusMap[r.status] || r.status,
      issue_date: r.issue_date ? r.issue_date.slice(0, 10) : '',
      resolved_at: r.resolved_at ? r.resolved_at.slice(0, 10) : '',
    }))
    exportToExcel(exportCols, exportData, '质量问题')
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '客户ID', dataIndex: 'customer_id', key: 'customer_id', width: 80 },
    { title: '铸件ID', dataIndex: 'casting_id', key: 'casting_id', width: 80 },
    { title: '问题类型', dataIndex: 'issue_type', key: 'issue_type', width: 120 },
    { title: '问题描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: '严重程度', dataIndex: 'severity', key: 'severity', render: getSeverityTag },
    { title: '状态', dataIndex: 'status', key: 'status', render: getStatusTag },
    { title: '发现日期', dataIndex: 'created_at', key: 'created_at', width: 120 },
    { title: '解决日期', dataIndex: 'resolved_at', key: 'resolved_at', width: 120 },
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
        <h1>质量问题</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            记录质量问题
          </Button>
        </Space>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索问题描述..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => { setSearchText(e.target.value); setPage(1) }}
        />
      </div>

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total || 0,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps) }
        }}
      />

      <Modal
        title={editingId ? '编辑质量问题' : '新增质量问题'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="customer_id" label="客户" rules={[{ required: true }]}>
            <Select placeholder="选择客户" showSearch optionFilterProp="children">
              {customers?.items?.map(c => (
                <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="casting_id" label="铸件" rules={[{ required: true }]}>
            <Select placeholder="选择铸件" showSearch optionFilterProp="children">
              {castings?.items?.map(c => (
                <Select.Option key={c.id} value={c.id}>{c.name} ({c.part_number})</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="issue_type" label="问题类型" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="问题描述" rules={[{ required: true }]}>
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="severity" label="严重程度" initialValue="medium">
            <Select>
              <Select.Option value="low">轻微</Select.Option>
              <Select.Option value="medium">一般</Select.Option>
              <Select.Option value="high">严重</Select.Option>
              <Select.Option value="critical">危急</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="status" label="状态" initialValue="open">
            <Select>
              <Select.Option value="open">待处理</Select.Option>
              <Select.Option value="investigating">调查中</Select.Option>
              <Select.Option value="resolved">已解决</Select.Option>
              <Select.Option value="closed">已关闭</Select.Option>
            </Select>
          </Form.Item>
          <Space>
            <Form.Item name="issue_date" label="发现日期">
              <DatePicker />
            </Form.Item>
            <Form.Item name="resolved_at" label="解决日期">
              <DatePicker />
            </Form.Item>
          </Space>
          <Form.Item name="resolution" label="解决方案">
            <Input.TextArea rows={2} />
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

export default QualityIssues
