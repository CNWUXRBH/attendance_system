import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, message } from 'antd';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import {
  DashboardOutlined,
  TeamOutlined,
  CalendarOutlined,
  BarChartOutlined,
  WarningOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: <Link to="/">数据看板</Link> },
  { key: '/employee', icon: <TeamOutlined />, label: <Link to="/employee">人员管理</Link> },
  { key: '/attendance', icon: <CalendarOutlined />, label: <Link to="/attendance">考勤记录</Link> },
  { key: '/schedule', icon: <CalendarOutlined />, label: <Link to="/schedule">排班管理</Link> },
  { key: '/report', icon: <BarChartOutlined />, label: <Link to="/report">报表统计</Link> },
  { key: '/exception', icon: <WarningOutlined />, label: <Link to="/exception">异常设定</Link> },
];

// 定义退出登录处理函数
const handleLogout = (navigate) => {
  localStorage.removeItem('token');
  message.success('退出登录成功');
  navigate('/login');
};

const getUserMenuItems = (navigate) => [
  {
    key: 'profile',
    icon: <UserOutlined />,
    label: <Link to="/my/profile">个人中心</Link>,
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: <Link to="/my/settings">个人设置</Link>,
  },
  {
    type: 'divider',
  },
  {
    key: 'logout',
    icon: <LogoutOutlined />,
    label: '退出登录',
    onClick: () => handleLogout(navigate),
  },
];

const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const userMenuItems = getUserMenuItems(navigate);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div className="logo" />
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['/']} items={menuItems} />
      </Sider>
      <Layout className="site-layout">
        <Header className="site-layout-background" style={{ padding: '0 16px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Dropdown menu={{items: userMenuItems}}>
            <span className="ant-dropdown-link" onClick={(e) => e.preventDefault()}>
              <Avatar icon={<UserOutlined />} />
            </span>
          </Dropdown>
        </Header>
        <Content style={{ margin: '16px' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;