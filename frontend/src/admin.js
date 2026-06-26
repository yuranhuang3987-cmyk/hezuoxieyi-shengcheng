import React from 'react';
import { TeamOutlined } from '@ant-design/icons';
import UserManagement from './pages/UserManagement';

export const menuItems = [
  { key: '/users', icon: <TeamOutlined />, label: '用户管理' },
];

export const routes = [
  { path: '/users', element: <UserManagement /> },
];
