import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, message, Modal } from 'antd';
import { getExceptionRules, addExceptionRule, updateExceptionRule, deleteExceptionRule } from '../../services/exception';
import ExceptionRuleModal from './ExceptionRuleModal';

const Exception = () => {
  const [data, setData] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState(null);

  const fetchExceptions = async () => {
    const result = await getExceptionRules();
    setData(result);
  };

  useEffect(() => {
    fetchExceptions();
  }, []);

  const handleAdd = async (values) => {
    try {
      await addExceptionRule(values);
      setIsModalVisible(false);
      fetchExceptions();
      message.success('新增规则成功');
    } catch (error) {
      message.error('新增规则失败');
    }
  };

  const handleEdit = async (values) => {
    try {
      await updateExceptionRule(values.rule_id, values);
      setIsModalVisible(false);
      setEditingRule(null);
      fetchExceptions();
      message.success('编辑规则成功');
    } catch (error) {
      message.error('编辑规则失败');
    }
  };

  const handleDelete = (id) => {
    Modal.confirm({
      title: '确定删除该规则吗？',
      content: '删除后将无法恢复',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteExceptionRule(id);
          fetchExceptions();
          message.success('删除规则成功');
        } catch (error) {
          message.error('删除规则失败');
        }
      },
    });
  };

  const columns = [
    {
      title: '规则名称',
      dataIndex: 'rule_name',
      key: 'rule_name',
    },
    {
      title: '规则类型',
      dataIndex: 'rule_type',
      key: 'rule_type',
      render: (type) => {
        const color = type === '迟到' ? 'orange' : type === '早退' ? 'red' : 'blue';
        return <Tag color={color}>{type}</Tag>;
      },
    },
    {
      title: '时间阈值 (分钟)',
      dataIndex: 'threshold',
      key: 'threshold',
    },
    {
      title: '处理方式',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '操作',
      key: 'operation',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            onClick={() => {
              setEditingRule(record);
              setIsModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Button type="link" danger onClick={() => handleDelete(record.rule_id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">异常设定</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between mb-4">
          <Space>
            <Button type="primary" onClick={() => setIsModalVisible(true)}>
              新增规则
            </Button>
          </Space>
        </div>
        <Table columns={columns} dataSource={data} rowKey="rule_id" />
      </div>
      <ExceptionRuleModal
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingRule(null);
        }}
        onOk={editingRule ? handleEdit : handleAdd}
        rule={editingRule}
      />
    </div>
  );
};

export default Exception;