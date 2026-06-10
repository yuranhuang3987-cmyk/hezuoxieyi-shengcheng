import React from 'react';
import { HistoryOutlined, TeamOutlined } from '@ant-design/icons';
import History from './pages/History';
import UserManagement from './pages/UserManagement';

export const menuItems = [
  { key: '/history', icon: <HistoryOutlined />, label: '历史记录' },
  { key: '/users', icon: <TeamOutlined />, label: '用户管理' },
];

export const routes = [
  { path: '/history', element: <History /> },
  { path: '/users', element: <UserManagement /> },
];
