import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Layout, Menu, Typography, ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { FileTextOutlined, HistoryOutlined } from '@ant-design/icons';
import Home from './pages/Home';
import History from './pages/History';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

function AppLayout() {
  const navigate = useNavigate();

  const menuItems = [
    {
      key: '/',
      icon: <FileTextOutlined />,
      label: '生成协议',
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: '历史记录',
    },
  ];

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
      </Header>

      <Content style={{ padding: '24px 50px' }}>
        <div style={{ background: '#fff', padding: 24, minHeight: 380, borderRadius: 8 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </Content>

      <Footer style={{ textAlign: 'center', color: '#999' }}>
        软件著作权合作协议生成器 © 2026 | 免费、快速、高效
      </Footer>
    </Layout>
  );
}

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <AppLayout />
      </Router>
    </ConfigProvider>
  );
}

export default App;
