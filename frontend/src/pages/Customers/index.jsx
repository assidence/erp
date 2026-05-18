import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Input, Space, Drawer, Descriptions, Tag, Table, Card, List } from 'antd'
import { PlusOutlined, SearchOutlined, ShopOutlined, DownloadOutlined } from '@ant-design/icons'
import FormModal from '../../components/FormModal'
import { customerApi } from '../../api'
import { exportToExcel } from '../../utils/exportExcel'

export default function Customers() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingRecord, setEditingRecord] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedCustomer, setSelectedCustomer] = useState(null)

  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['customers', page, pageSize, search],
    queryFn: () => customerApi.list({ page, page_size: pageSize, search })
  })

  const { data: linkedFoundries } = useQuery({
    queryKey: ['customer-foundries', selectedCustomer?.id],
    queryFn: async () => {
      try {
        const c = await customerApi.get(selectedCustomer?.id)
        return c?.linked_foundries || []
      } catch (err) {
        if (err?.response?.status === 404) return []
        throw err
      }
    },
    enabled: !!selectedCustomer?.id
  })

  const createMutation = useMutation({
    mutationFn: (data) => customerApi.create(data),
    onSuccess: () => { queryClient.invalidateQueries(['customers']); setModalOpen(false) }
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => customerApi.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries(['customers']); setModalOpen(false); setEditingId(null) }
  })
  const deleteMutation = useMutation({
    mutationFn: (id) => customerApi.delete(id),
    onSuccess: (data, variables) => {
      // Update the list cache directly
      queryClient.setQueryData(['customers', page, pageSize, search], (old) => {
        if (!old) return old
        return {
          ...old,
          items: (old.items || []).filter(c => c.id !== variables),
          total: Math.max(0, (old.total || 0) - 1)
        }
      })
      // Cancel pending customer-foundries query for deleted customer
      queryClient.cancelQueries({ queryKey: ['customer-foundries', variables] })
      // If deleting the currently viewed customer, close detail panel
      if (selectedCustomer?.id === variables) {
        setSelectedCustomer(null)
        setDetailOpen(false)
      }
    }
  })

  const handleEdit = (record) => {
    setEditingRecord(record)
    setModalOpen(true)
  }
  const handleView = async (record) => {
    const detail = await customerApi.get(record.id)
    setSelectedCustomer(detail)
    setDetailOpen(true)
  }
  const handleDelete = (id) => deleteMutation.mutate(id)
  const handleSubmit = (values) => {
    if (editingRecord) {
      updateMutation.mutate({ id: editingRecord.id, data: values })
    } else {
      createMutation.mutate(values)
    }
  }

  const handleExport = () => {
    const exportCols = [
      { title: '名称', dataIndex: 'name' },
      { title: '联系人', dataIndex: 'contact_person' },
      { title: '电话', dataIndex: 'phone' },
      { title: '邮箱', dataIndex: 'email' },
      { title: '付款条款', dataIndex: 'payment_terms' },
      { title: '付款天数', dataIndex: 'payment_days' },
      { title: '地址', dataIndex: 'address' },
      { title: '状态', dataIndex: 'is_active' },
    ]
    const exportData = (data?.items || []).map(c => ({ ...c, is_active: c.is_active ? '活跃' : '停用' }))
    exportToExcel(exportCols, exportData, '客户管理')
  }

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '联系人', dataIndex: 'contact_person', key: 'contact_person' },
    { title: '电话', dataIndex: 'phone', key: 'phone' },
    { title: '付款条款', dataIndex: 'payment_terms', key: 'payment_terms' },
    { title: '付款天数', dataIndex: 'payment_days', key: 'payment_days' },
    {
      title: '状态', dataIndex: 'is_active', key: 'is_active',
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? '活跃' : '停用'}</Tag>
    },
    {
      title: '操作', key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={(e) => { e.stopPropagation(); handleEdit(record) }}>编辑</Button>
          <Button type="link" size="small" danger onClick={(e) => { e.stopPropagation(); handleDelete(record.id) }}>删除</Button>
        </Space>
      )
    },
  ]

  const fields = [
    { name: 'name', label: '客户名称', type: 'input', span: 12, rules: [{ required: true }] },
    { name: 'contact_person', label: '联系人', type: 'input', span: 12 },
    { name: 'phone', label: '电话', type: 'input', span: 12 },
    { name: 'email', label: '邮箱', type: 'input', span: 12 },
    { name: 'payment_terms', label: '付款条款', type: 'input', span: 12 },
    { name: 'payment_days', label: '付款天数', type: 'number', span: 12 },
    { name: 'is_active', label: '状态', type: 'switch', span: 12, initialValue: true },
    { name: 'address', label: '地址', type: 'textarea', span: 24 },
    { name: 'notes', label: '备注', type: 'textarea', span: 24 },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">客户管理</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出Excel</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建客户</Button>
        </Space>
      </div>
      <div className="filter-row">
        <Space>
          <Input
            placeholder="搜索客户名称..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            style={{ width: 300 }}
          />
        </Space>
      </div>
      <Table
        columns={columns}
        dataSource={data?.items || []}
        loading={isLoading}
        rowKey="id"
        pagination={{
          current: page,
          pageSize,
          total: data?.total || 0,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps) }
        }}
        onRow={(record) => ({ onClick: () => handleView(record), style: { cursor: 'pointer' } })}
      />
      <FormModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditingRecord(null) }}
        onSubmit={handleSubmit}
        title={editingRecord ? '编辑客户' : '新建客户'}
        loading={createMutation.isPending || updateMutation.isPending}
        fields={fields}
        initialValues={editingRecord || null}
      />
      <Drawer title="客户详情" open={detailOpen} onClose={() => setDetailOpen(false)} width={600}>
        {selectedCustomer && (
          <>
            <Descriptions column={1} bordered style={{ marginBottom: 24 }}>
              <Descriptions.Item label="名称">{selectedCustomer.name}</Descriptions.Item>
              <Descriptions.Item label="联系人">{selectedCustomer.contact_person}</Descriptions.Item>
              <Descriptions.Item label="电话">{selectedCustomer.phone}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{selectedCustomer.email}</Descriptions.Item>
              <Descriptions.Item label="付款条款">{selectedCustomer.payment_terms}</Descriptions.Item>
              <Descriptions.Item label="付款天数">{selectedCustomer.payment_days}</Descriptions.Item>
              <Descriptions.Item label="地址">{selectedCustomer.address}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={selectedCustomer.is_active ? 'green' : 'red'}>
                  {selectedCustomer.is_active ? '活跃' : '停用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="备注">{selectedCustomer.notes}</Descriptions.Item>
            </Descriptions>
            <Card title="关联的铸造厂" size="small">
              {linkedFoundries && linkedFoundries.length > 0 ? (
                <List
                  size="small"
                  dataSource={linkedFoundries}
                  renderItem={item => (
                    <List.Item>
                      <Space>
                        <ShopOutlined />
                        <span>{item.name}</span>
                        <span style={{ color: '#999' }}>({item.contact_person} - {item.phone})</span>
                      </Space>
                    </List.Item>
                  )}
                />
              ) : (
                <span style={{ color: '#999' }}>暂无关联的铸造厂</span>
              )}
            </Card>
          </>
        )}
      </Drawer>
    </div>
  )
}
