import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Layout, Menu, Typography, ConfigProvider, Button, message } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { FileTextOutlined, HistoryOutlined, UserOutlined, LogoutOutlined, TeamOutlined } from '@ant-design/icons';
import axios from 'axios';
import Login from './pages/Login';
import Home from './pages/Home';
import History from './pages/History';
import UserManagement from './pages/UserManagement';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

// 受保护的路由
function ProtectedRoute({ children, user, adminOnly = false }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }
  return children;
}

function AppLayout({ user, onLogout }) {
  const navigate = useNavigate();

  const menuItems = [
    {
      key: '/',
      icon: <FileTextOutlined />,
      label: '生成协议',
    },
  ];

  // 只有管理员能看到历史记录和用户管理
  if (user.role === 'admin') {
    menuItems.push(
      {
        key: '/history',
        icon: <HistoryOutlined />,
        label: '历史记录',
      },
      {
        key: '/users',
        icon: <TeamOutlined />,
        label: '用户管理',
      }
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#fff' }}>
        <Title level={3} style={{ margin: 0, marginRight: 40, color: '#1890ff' }}>
          📄 软件著作权合作协议生成器
        </Title>
        <Menu
          mode="horizontal"
          defaultSelectedKeys={['/']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, border: 'none' }}
        />
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <UserOutlined />
          <span>{user.username}</span>
          {user.role === 'admin' && (
            <span style={{ color: '#f5222d', fontSize: 12 }}>(管理员)</span>
          )}
          <Button type="link" icon={<LogoutOutlined />} onClick={onLogout}>
            登出
          </Button>
        </div>
      </Header>

      <Content style={{ padding: '24px 50px' }}>
        <div style={{ background: '#fff', padding: 24, minHeight: 380, borderRadius: 8 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
            <Route path="/users" element={<UserManagement />} />
          </Routes>
        </div>
      </Content>

      <Footer style={{ textAlign: 'center', color: '#999' }}>
        技术联系微信：H50799549
      </Footer>
    </Layout>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 检查登录状态
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/me', { withCredentials: true });
      if (response.data.ok) {
        setUser(response.data.data);
      }
    } catch (error) {
      // 未登录
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/api/logout', {}, { withCredentials: true });
    } catch (error) {
      // ignore
    }
    setUser(null);
    message.success('已登出');
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 100 }}>加载中...</div>;
  }

  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route
            path="/login"
            element={
              user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
            }
          />
          <Route
            path="/*"
            element={
              <ProtectedRoute user={user}>
                <AppLayout user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;
