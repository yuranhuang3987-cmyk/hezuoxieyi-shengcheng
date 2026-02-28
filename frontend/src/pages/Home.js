import React, { useState } from 'react';
import { Upload, Button, Card, message, Spin, Descriptions, Tag, Divider, Space, Modal } from 'antd';
import { UploadOutlined, FileTextOutlined, DownloadOutlined, ReloadOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Dragger } = Upload;

function Home() {
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [uploadPath, setUploadPath] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  // 上传配置
  const uploadProps = {
    name: 'file',
    multiple: true,
    accept: '.docx,.doc',
    showUploadList: false,
    beforeUpload: (file, fileList) => {
      // 处理多文件上传
      handleMultipleUpload(fileList);
      return false; // 阻止自动上传
    },
  };

  // 处理多文件上传
  const handleMultipleUpload = async (files) => {
    if (!files || files.length === 0) return;

    setLoading(true);
    setPreviewData(null);
    setDownloadUrl(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('http://172.29.167.50:5000/api/preview-batch', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.ok) {
        setPreviewData(response.data.data);
        setUploadPath(response.data.data.upload_paths);
        message.success(`成功解析 ${files.length} 个文件！`);
        
        // 检查是否有未成年人
        if (response.data.data.minors && response.data.data.minors.length > 0) {
          const minorNames = response.data.data.minors.map(m => `${m.name}（${m.age}岁）`).join('、');
          Modal.warning({
            title: '未成年人提醒',
            content: (
              <div>
                <p>以下著作权人为未成年人，需注意：</p>
                <p style={{ fontWeight: 'bold', color: '#faad14' }}>{minorNames}</p>
                <p style={{ marginTop: 16 }}>建议由监护人代为签署协议或出具监护人同意书。</p>
              </div>
            ),
          });
        }
      } else {
        message.error(response.data.err || '解析失败');
      }
    } catch (error) {
      message.error('上传失败，请检查后端服务是否启动');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 生成协议
  const handleGenerate = async () => {
    if (!previewData || !uploadPath) {
      message.warning('请先上传并预览文件');
      return;
    }

    setGenerating(true);

    try {
      const response = await axios.post('http://172.29.167.50:5000/api/generate', {
        ...previewData,
        upload_path: uploadPath,
      });

      if (response.data.ok) {
        setDownloadUrl(response.data.download_url);
        message.success('协议生成成功！');
      } else {
        message.error(response.data.err || '生成失败');
      }
    } catch (error) {
      message.error('生成失败，请稍后重试');
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  // 下载文件
  const handleDownload = () => {
    if (downloadUrl) {
      window.open(`http://172.29.167.50:5000${downloadUrl}`, '_blank');
    }
  };

  // 重置
  const handleReset = () => {
    setPreviewData(null);
    setUploadPath(null);
    setDownloadUrl(null);
  };

  return (
    <div>
      <div className="upload-section">
        <Card title="第一步：上传申请表" bordered={false}>
          <Dragger {...uploadProps} disabled={loading}>
            <p className="ant-upload-drag-icon">
              <FileTextOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">支持 .docx 和 .doc 格式的软件著作权申请表</p>
          </Dragger>
        </Card>
      </div>

      {loading && (
        <div className="loading-container">
          <Spin size="large" tip="正在解析文件..." />
        </div>
      )}

      {previewData && !loading && (
        <>
          <Card title="第二步：确认信息" bordered={false} style={{ marginBottom: 24 }}>
            {/* 显示软件数量 */}
            {previewData.software_count > 1 && (
              <div style={{ marginBottom: 16, padding: 12, background: '#e6f7ff', borderRadius: 4 }}>
                <strong>📋 检测到 {previewData.software_count} 个软件，将为每个软件生成独立的协议</strong>
              </div>
            )}

            {/* 软件列表 */}
            <Descriptions bordered column={2}>
              {previewData.software_list && previewData.software_list.length > 0 ? (
                <>
                  {previewData.software_count === 1 ? (
                    // 单软件：显示详细信息
                    <>
                      <Descriptions.Item label="软件名称" span={2}>
                        <strong>{previewData.software_list[0].software_name}</strong>
                      </Descriptions.Item>
                      <Descriptions.Item label="版本号">{previewData.software_list[0].software_version}</Descriptions.Item>
                      <Descriptions.Item label="著作权人数量">
                        <Tag color="blue">{previewData.owners_count} 人</Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="开发完成日期">{previewData.software_list[0].dev_date}</Descriptions.Item>
                      <Descriptions.Item label="协议签署日期">{previewData.software_list[0].agreement_date}</Descriptions.Item>
                    </>
                  ) : (
                    // 多软件：显示列表
                    <>
                      <Descriptions.Item label="软件数量" span={2}>
                        <Tag color="blue">{previewData.software_count} 个</Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="软件列表" span={2}>
                        <div>
                          {previewData.software_list.map((sw, index) => (
                            <div key={index} style={{ marginBottom: 8, padding: 8, background: '#fafafa', borderRadius: 4 }}>
                              <strong>{index + 1}. {sw.software_name}</strong>
                              <br />
                              <small style={{ color: '#666' }}>
                                版本: {sw.software_version} | 开发日期: {sw.dev_date} | 协议日期: {sw.agreement_date}
                              </small>
                            </div>
                          ))}
                        </div>
                      </Descriptions.Item>
                      <Descriptions.Item label="著作权人数量" span={2}>
                        <Tag color="blue">{previewData.owners_count} 人</Tag>
                      </Descriptions.Item>
                    </>
                  )}
                </>
              ) : (
                <Descriptions.Item label="提示" span={2}>
                  未检测到软件信息
                </Descriptions.Item>
              )}
            </Descriptions>

            <Divider>著作权人信息</Divider>

            <div className="owners-list">
              {previewData.owners.map((owner, index) => (
                <div key={index} className="owner-item">
                  <strong>
                    {index + 1}. {owner.name}
                  </strong>
                  <span className="owner-type">
                    {owner.is_person ? '(个人 - 签名留空)' : '(单位 - 显示名称)'}
                  </span>
                </div>
              ))}
            </div>

            <div className="action-buttons">
              <Space size="large">
                <Button icon={<ReloadOutlined />} onClick={handleReset}>
                  重新上传
                </Button>
                <Button
                  type="primary"
                  icon={<FileTextOutlined />}
                  onClick={handleGenerate}
                  loading={generating}
                  size="large"
                >
                  生成协议
                </Button>
              </Space>
            </div>
          </Card>

          {downloadUrl && (
            <Card title="第三步：下载协议" bordered={false}>
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={handleDownload}
                  size="large"
                >
                  下载合作协议
                </Button>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

export default Home;
