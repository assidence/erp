import React, { useState } from 'react'
import { Layout, Menu } from 'antd'
import { DashboardOutlined, TeamOutlined, ShopOutlined, AppstoreOutlined, ImportOutlined, ExportOutlined, CalendarOutlined, DollarOutlined, WarningOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider, Header, Content } = Layout

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '数据看板' },
  { key: '/customers', icon: <TeamOutlined />, label: '客户管理' },
  { key: '/foundries', icon: <ShopOutlined />, label: '铸造厂管理' },
  { key: '/castings', icon: <AppstoreOutlined />, label: '铸件管理' },
  {
    key: '/production',
    icon: <CalendarOutlined />,
    label: '生产管理',
    children: [
      { key: '/casting-ins', icon: <ImportOutlined />, label: '铸件入库' },
      { key: '/production-plans', icon: <CalendarOutlined />, label: '生产计划' },
      { key: '/workpiece-outs', icon: <ExportOutlined />, label: '工件出库' },
    ],
  },
  { key: '/payment-plans', icon: <DollarOutlined />, label: '收款计划' },
  { key: '/quality-issues', icon: <WarningOutlined />, label: '质量问题' },
]

function AppLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const selectedKey = location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={220}
        style={{ position: 'sticky', top: 0, height: '100vh', overflow: 'auto' }}
      >
        <div className="sider-logo">
          {collapsed ? 'ERP' : 'ERP System'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          theme="dark"
          onClick={({ key }) => navigate(key)}
          style={{ height: 'calc(100% - 64px)' }}
        />
      </Sider>
      <Layout>
        <Header className="header-bar">
          <div className="header-title">机械加工厂ERP系统</div>
          <div className="header-right">
            <span className="version">v1.0.0</span>
            <span className="admin">管理员</span>
          </div>
        </Header>
        <Content>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout
