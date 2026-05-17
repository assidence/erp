import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Input, Button, Checkbox, Popconfirm, message } from 'antd'
import {
  ShoppingOutlined,
  DollarOutlined,
  TeamOutlined, ShopOutlined, PlusOutlined, DeleteOutlined
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { todosApi } from '../../api'

async function fetchStats() {
  const res = await axios.get('/api/dashboard/stats')
  return res.data
}

async function fetchRecentActivity() {
  const res = await axios.get('/api/dashboard/recent')
  return res.data
}

const TYPE_CONFIG = {
  material_in:  { color: '#1677ff', bg: '#e6f4ff', label: '入库' },
  product_out:  { color: '#52c41a', bg: '#f6ffed', label: '出库' },
  production:   { color: '#722ed1', bg: '#f9f0ff', label: '生产' },
  payment:     { color: '#fa8c16', bg: '#fff7e6', label: '收款' },
  quality:     { color: '#f5222d', bg: '#fff1f0', label: '质量' },
}

function ActivityFeed({ items }) {
  if (!items || items.length === 0) {
    return (
      <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
        暂无活动记录
      </div>
    )
  }
  return (
    <div
      style={{
        height: 300,
        overflowY: 'auto',
        scrollBehavior: 'smooth',
      }}
    >
      <style>{`
        .activity-feed::-webkit-scrollbar { width: 4px; }
        .activity-feed::-webkit-scrollbar-track { background: transparent; }
        .activity-feed::-webkit-scrollbar-thumb { background: #d9d9d9; border-radius: 2px; }
      `}</style>
      {[...items, ...items].map((item, i) => {
        const cfg = TYPE_CONFIG[item.type] || { color: '#999', bg: '#f5f5f5', label: '其他' }
        return (
          <div key={`${item.id}-${i}`} style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 10,
            padding: '10px 4px',
            borderBottom: '1px solid #f0f0f0',
          }}>
            <span style={{
              background: cfg.bg,
              color: cfg.color,
              borderRadius: 4,
              padding: '2px 8px',
              fontSize: 12,
              fontWeight: 500,
              whiteSpace: 'nowrap',
              flexShrink: 0,
              marginTop: 2,
            }}>
              {cfg.label}
            </span>
            <span style={{ flex: 1, fontSize: 13, color: '#262626', lineHeight: '20px' }}>
              {item.description}
            </span>
            <span style={{ fontSize: 12, color: '#999', flexShrink: 0, marginTop: 2 }}>
              {item.time}
            </span>
          </div>
        )
      })}
    </div>
  )
}

function Dashboard() {
  const queryClient = useQueryClient()
  const [newTodo, setNewTodo] = useState('')

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchStats
  })

  const { data: recentActivity, isLoading: recentLoading } = useQuery({
    queryKey: ['dashboard-recent'],
    queryFn: fetchRecentActivity,
    refetchInterval: 30000,
  })

  const { data: todos = [], isLoading: todosLoading } = useQuery({
    queryKey: ['todos'],
    queryFn: () => todosApi.list()
  })

  useEffect(() => {
    const checkedTodos = todos.filter(t => t.is_done && t.completed_at)
    const now = new Date()
    const stale = checkedTodos.filter(t => {
      const diff = (now - new Date(t.completed_at)) / 1000 / 60 / 60
      return diff >= 24
    })
    if (stale.length > 0) {
      stale.forEach(t => {
        axios.delete(`/api/todos/${t.id}/`).catch(() => {})
      })
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    }
  }, [todos, queryClient])

  const createMutation = useMutation({
    mutationFn: (content) => todosApi.create({ content, is_done: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
      setNewTodo('')
    }
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_done }) => todosApi.update(id, { is_done }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['todos'] })
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => axios.delete(`/api/todos/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['todos'] })
  })

  const cleanupMutation = useMutation({
    mutationFn: () => todosApi.cleanup(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
      message.success('已清理已完成事项')
    }
  })

  const handleAddTodo = () => {
    if (!newTodo.trim()) return
    createMutation.mutate(newTodo.trim())
  }

  const pendingTodos = todos.filter(t => !t.is_done)
  const doneTodos = todos.filter(t => t.is_done)

  return (
    <div className="page-container">
      <div className="page-header">
        <h3 style={{margin: 0}}>仪表盘</h3>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="客户总数"
              value={stats?.totalCustomers ?? 0}
              prefix={<TeamOutlined />}
              loading={statsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="供应商总数"
              value={stats?.totalSuppliers ?? 0}
              prefix={<ShopOutlined />}
              loading={statsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="本月出库"
              value={stats?.monthlyOrders ?? 0}
              prefix={<ShoppingOutlined />}
              loading={statsLoading}
              suffix={<span style={{ fontSize: 14 }}>单</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待收款金额"
              value={stats?.pendingPayments ?? 0}
              prefix={<DollarOutlined />}
              suffix="元"
              loading={statsLoading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={16}>
          <Card
            title="最近活动"
            extra={<span style={{ fontSize: 12, color: '#999' }}>鼠标滚轮滚动</span>}
          >
            {recentLoading ? (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
                加载中...
              </div>
            ) : (
              <ActivityFeed items={recentActivity} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card
            title="待办事项"
            extra={
              <Popconfirm title="清理所有已完成事项？" onConfirm={() => cleanupMutation.mutate()}>
                <Button size="small" type="text" disabled={doneTodos.length === 0}>
                  清理已完成
                </Button>
              </Popconfirm>
            }
          >
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              <Input
                placeholder="输入新事项..."
                value={newTodo}
                onChange={(e) => setNewTodo(e.target.value)}
                onPressEnter={handleAddTodo}
                style={{ flex: 1 }}
              />
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAddTodo}
                loading={createMutation.isPending} />
            </div>

            {pendingTodos.length === 0 && doneTodos.length === 0 && (
              <div style={{ color: '#999', textAlign: 'center', padding: '16px 0' }}>
                暂无待办事项
              </div>
            )}
            {pendingTodos.map(todo => (
              <div key={todo.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Checkbox
                  checked={false}
                  onChange={() => toggleMutation.mutate({ id: todo.id, is_done: true })}
                />
                <span style={{ flex: 1 }}>{todo.content}</span>
                <Button type="text" size="small" danger icon={<DeleteOutlined />}
                  onClick={() => deleteMutation.mutate(todo.id)} />
              </div>
            ))}

            {doneTodos.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <div style={{ color: '#999', fontSize: 12, marginBottom: 4 }}>已完成</div>
                {doneTodos.map(todo => (
                  <div key={todo.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <Checkbox
                      checked={true}
                      onChange={() => toggleMutation.mutate({ id: todo.id, is_done: false })}
                    />
                    <span style={{ flex: 1, textDecoration: 'line-through', color: '#999' }}>{todo.content}</span>
                    <Button type="text" size="small" danger icon={<DeleteOutlined />}
                      onClick={() => deleteMutation.mutate(todo.id)} />
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
