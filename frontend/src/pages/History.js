import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Descriptions, message, Popconfirm, Space, Empty } from 'antd';
import { EyeOutlined, DownloadOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';

function History() {
  const [loading, setLoading] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentDetail, setCurrentDetail] = useState(null);

  // 加载历史记录
  useEffect(() => {
    loadHistory(1, 10);
  }, []);

  const loadHistory = async (page, pageSize) => {
    setLoading(true);
    try {
      const response = await axios.get('http://172.29.167.50:5000/api/history', {
        params: { page, per_page: pageSize },
      });

      if (response.data.ok) {
        setHistoryData(response.data.data.items);
        setPagination({
          current: page,
          pageSize: pageSize,
          total: response.data.data.total,
        });
      } else {
        message.error(response.data.err || '加载失败');
      }
    } catch (error) {
      message.error('加载失败，请检查后端服务');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 查看详情
  const handleViewDetail = async (id) => {
    try {
      const response = await axios.get(`http://172.29.167.50:5000/api/history/${id}`);
      if (response.data.ok) {
        setCurrentDetail(response.data.data);
        setDetailVisible(true);
      } else {
        message.error(response.data.err || '获取详情失败');
      }
    } catch (error) {
      message.error('获取详情失败');
      console.error(error);
    }
  };

  // 下载文件
  const handleDownload = (outputFile) => {
    window.open(`http://172.29.167.50:5000/api/download/${outputFile}`, '_blank');
  };

  // 删除记录
  const handleDelete = async (id) => {
    try {
      const response = await axios.delete(`http://172.29.167.50:5000/api/history/${id}`);
      if (response.data.ok) {
        message.success('删除成功');
        loadHistory(pagination.current, pagination.pageSize);
      } else {
        message.error(response.data.err || '删除失败');
      }
    } catch (error) {
      message.error('删除失败');
      console.error(error);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '软件名称',
      dataIndex: 'software_name',
      key: 'software_name',
      width: 250,
      ellipsis: true,
    },
    {
      title: '版本',
      dataIndex: 'software_version',
      key: 'software_version',
      width: 80,
    },
    {
      title: '著作权人',
      dataIndex: 'owners_count',
      key: 'owners_count',
      width: 100,
      render: (count) => <Tag color="blue">{count} 人</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.id)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record.output_file)}
          >
            下载
          </Button>
          <Popconfirm
            title="确定要删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="历史记录"
        extra={
          <Button icon={<ReloadOutlined />} onClick={() => loadHistory(1, 10)}>
            刷新
          </Button>
        }
        bordered={false}
      >
        {historyData.length === 0 && !loading ? (
          <Empty description="暂无历史记录" style={{ padding: '40px 0' }} />
        ) : (
          <Table
            columns={columns}
            dataSource={historyData}
            rowKey="id"
            loading={loading}
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条记录`,
              onChange: (page, pageSize) => loadHistory(page, pageSize),
            }}
          />
        )}
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="详细信息"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
          currentDetail && (
            <Button
              key="download"
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => {
                handleDownload(currentDetail.output_file);
                setDetailVisible(false);
              }}
            >
              下载协议
            </Button>
          ),
        ]}
        width={700}
      >
        {currentDetail && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="软件名称" span={2}>
              <strong>{currentDetail.software_name}</strong>
            </Descriptions.Item>
            <Descriptions.Item label="版本">{currentDetail.software_version}</Descriptions.Item>
            <Descriptions.Item label="著作权人">
              <Tag color="blue">{currentDetail.owners_count} 人</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="开发完成日期">
              {currentDetail.dev_date}
            </Descriptions.Item>
            <Descriptions.Item label="协议签署日期">
              {currentDetail.agreement_date}
            </Descriptions.Item>
            <Descriptions.Item label="输入文件" span={2}>
              {currentDetail.input_file}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间" span={2}>
              {currentDetail.created_at}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}

export default History;
