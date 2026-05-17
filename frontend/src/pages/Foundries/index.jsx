import React, { useState } from 'react'
import { Table, Button, Input, Space, Modal, Form, Select, message } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { foundryApi, customerApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

const { confirm } = Modal

function Foundries() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data: customers } = useQuery({
    queryKey: ['customers-for-foundry'],
    queryFn: () => customerApi.list({ page: 1, page_size: 100 })
  })

  const { data, isLoading } = useQuery({
    queryKey: ['foundries', page, pageSize, searchText],
    queryFn: async () => {
      const res = await foundryApi.list({ page, page_size: pageSize, search: searchText })
      return res
    }
  })

  const createMutation = useMutation({
    mutationFn: (data) => foundryApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['foundries'])
      message.success('铸造厂创建成功')
      handleModalClose()
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => foundryApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['foundries'])
      message.success('铸造厂更新成功')
      handleModalClose()
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => foundryApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['foundries'])
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
    form.setFieldsValue(record)
  }

  const handleDelete = (id) => {
    confirm({
      title: '确认删除',
      content: '确定要删除这个铸造厂吗？',
      onOk: () => deleteMutation.mutate(id)
    })
  }

  const handleSubmit = (values) => {
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: values })
    } else {
      createMutation.mutate(values)
    }
  }

  const handleExport = () => {
    const exportCols = [
      { title: 'ID', dataIndex: 'id' },
      { title: '铸造厂名称', dataIndex: 'name' },
      { title: '联系人', dataIndex: 'contact_person' },
      { title: '联系电话', dataIndex: 'phone' },
      { title: '地址', dataIndex: 'address' },
    ]
    exportToExcel(exportCols, data?.items || [], '铸造厂管理')
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '铸造厂名称', dataIndex: 'name', key: 'name' },
    { title: '联系人', dataIndex: 'contact_person', key: 'contact_person' },
    { title: '联系电话', dataIndex: 'phone', key: 'phone' },
    { title: '地址', dataIndex: 'address', key: 'address' },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      )
    }
  ]

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>铸造厂管理</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            新增铸造厂
          </Button>
        </Space>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索铸造厂名称..."
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
        title={editingId ? '编辑铸造厂' : '新增铸造厂'}
        open={isModalOpen}
        onCancel={handleModalClose}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="铸造厂名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="contact_person" label="联系人">
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="联系电话">
            <Input />
          </Form.Item>
          <Form.Item name="address" label="地址">
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

export default Foundries
