import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Popconfirm, Card } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getShiftTemplates, deleteShiftTemplate } from '../../services/schedule';
import TemplateModal from './TemplateModal';

const TemplateManagement = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await getShiftTemplates();
      setTemplates(response.data || []);
    } catch (error) {
      message.error('获取模板列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteShiftTemplate(id);
      message.success('模板删除成功');
      fetchTemplates();
    } catch (error) {
      message.error('模板删除失败');
    }
  };

  const handleEdit = (template) => {
    setSelectedTemplate(template);
    setIsModalVisible(true);
  };

  const handleAdd = () => {
    setSelectedTemplate(null);
    setIsModalVisible(true);
  };

  const handleModalOk = () => {
    setIsModalVisible(false);
    setSelectedTemplate(null);
    fetchTemplates();
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    setSelectedTemplate(null);
  };

  const columns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '班次类型',
      dataIndex: 'shift_type_id',
      key: 'shift_type_id',
      render: (shiftTypeId) => {
        const shiftTypes = {
          1: '早班',
          2: '中班',
          3: '晚班'
        };
        return shiftTypes[shiftTypeId] || '未知';
      },
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此模板吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    fetchTemplates();
  }, []);

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center">
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/schedule')}
              className="mr-4"
            >
              返回
            </Button>
            <h1 className="text-2xl font-bold">排班模板管理</h1>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
          >
            新建模板
          </Button>
        </div>
        
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>
      
      <TemplateModal
        visible={isModalVisible}
        onCancel={handleModalCancel}
        onOk={handleModalOk}
        template={selectedTemplate}
      />
    </div>
  );
};

export default TemplateManagement;