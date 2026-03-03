import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Popconfirm, Space, Tag } from 'antd';
import { UserOutlined, PlusOutlined, ReloadOutlined, KeyOutlined } from '@ant-design/icons';
import axios from 'axios';

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [resetModalVisible, setResetModalVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [form] = Form.useForm();
  const [resetForm] = Form.useForm();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/users', { withCredentials: true });
      if (response.data.ok) {
        setUsers(response.data.data);
      }
    } catch (error) {
      message.error(error.response?.data?.err || '获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values) => {
    try {
      const response = await axios.post('http://localhost:5000/api/users', values, { withCredentials: true });
      if (response.data.ok) {
        message.success('创建成功');
        setModalVisible(false);
        form.resetFields();
        fetchUsers();
      }
    } catch (error) {
      message.error(error.response?.data?.err || '创建失败');
    }
  };

  const handleDelete = async (userId) => {
    try {
      const response = await axios.delete(`http://localhost:5000/api/users/${userId}`, { withCredentials: true });
      if (response.data.ok) {
        message.success('删除成功');
        fetchUsers();
      }
    } catch (error) {
      message.error(error.response?.data?.err || '删除失败');
    }
  };

  const handleResetPassword = async (values) => {
    try {
      const response = await axios.post(
        `http://localhost:5000/api/users/${selectedUser.id}/reset-password`,
        { password: values.password },
        { withCredentials: true }
      );
      if (response.data.ok) {
        message.success('密码已重置');
        setResetModalVisible(false);
        resetForm.resetFields();
        setSelectedUser(null);
      }
    } catch (error) {
      message.error(error.response?.data?.err || '重置失败');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '用户名',
      dataIndex: 'username',
    },
    {
      title: '角色',
      dataIndex: 'role',
      render: (role) => (
        <Tag color={role === 'admin' ? 'red' : 'blue'}>
          {role === 'admin' ? '管理员' : '普通用户'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
    },
    {
      title: '操作',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<KeyOutlined />}
            onClick={() => {
              setSelectedUser(record);
              setResetModalVisible(true);
            }}
          >
            重置密码
          </Button>
          <Popconfirm
            title="确定删除该用户？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button size="small" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          创建用户
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchUsers}>
          刷新
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      {/* 创建用户弹窗 */}
      <Modal
        title="创建用户"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="密码" />
          </Form.Item>
          <Form.Item
            name="role"
            label="角色"
            initialValue="user"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="user">普通用户</Select.Option>
              <Select.Option value="admin">管理员</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 重置密码弹窗 */}
      <Modal
        title={`重置密码 - ${selectedUser?.username}`}
        open={resetModalVisible}
        onCancel={() => {
          setResetModalVisible(false);
          setSelectedUser(null);
        }}
        footer={null}
      >
        <Form form={resetForm} onFinish={handleResetPassword} layout="vertical">
          <Form.Item
            name="password"
            label="新密码"
            rules={[{ required: true, message: '请输入新密码' }]}
          >
            <Input.Password placeholder="新密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              重置
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default UserManagement;
