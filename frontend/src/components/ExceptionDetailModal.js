import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Descriptions, Button, Select, message, Tag } from 'antd';
import { getAttendanceRecordDetail, updateAttendanceStatus } from '../services/attendance';

const { Option } = Select;

const ExceptionDetailModal = ({ open, onCancel, recordId, onStatusUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [record, setRecord] = useState(null);
  const [processing, setProcessing] = useState(false);

  const fetchRecordDetail = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getAttendanceRecordDetail(recordId);
      setRecord(result);
    } catch (error) {
      message.error('获取记录详情失败');
    } finally {
      setLoading(false);
    }
  }, [recordId]);

  useEffect(() => {
    if (open && recordId) {
      fetchRecordDetail();
    }
  }, [open, recordId, fetchRecordDetail]);

  const handleStatusChange = async (newStatus) => {
    setProcessing(true);
    try {
      // 状态映射：中文到英文
      const statusMap = {
        '未处理': 'unprocessed',
        '处理中': 'processing',
        '已处理': 'processed'
      };
      
      await updateAttendanceStatus(recordId, statusMap[newStatus] || newStatus);
      message.success('状态更新成功');
      setRecord({ ...record, process_status: newStatus });
      if (onStatusUpdate) {
        onStatusUpdate();
      }
    } catch (error) {
      message.error('状态更新失败');
    } finally {
      setProcessing(false);
    }
  };

  const getStatusColor = (status) => {
    const statusMap = {
      '迟到': 'orange',
      '早退': 'orange', 
      '缺勤': 'red',
      '缺卡': 'red',
      '位置异常': 'volcano',
      '正常': 'green'
    };
    return statusMap[status] || 'default';
  };

  const getProcessStatusColor = (status) => {
    const statusMap = {
      'unprocessed': 'red',
      'processing': 'orange',
      'processed': 'green'
    };
    return statusMap[status] || 'default';
  };

  const getProcessStatusText = (status) => {
    const statusMap = {
      'unprocessed': '未处理',
      'processing': '处理中', 
      'processed': '已处理'
    };
    return statusMap[status] || status;
  };

  return (
    <Modal
      title="异常详情"
      open={open}
      onCancel={onCancel}
      width={800}
      footer={[
        <Button key="close" onClick={onCancel}>
          关闭
        </Button>,
        record && record.status === 'pending' && (
          <Select
            key="status"
            style={{ width: 120, marginRight: 8 }}
            placeholder="处理状态"
            onChange={handleStatusChange}
            loading={processing}
          >
            <Option value="approved">通过</Option>
            <Option value="rejected">拒绝</Option>
          </Select>
        ),
      ]}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>加载中...</div>
      ) : record ? (
        <Descriptions column={2} bordered>
          <Descriptions.Item label="员工姓名" span={1}>
            {record.employee_name || '未知'}
          </Descriptions.Item>
          <Descriptions.Item label="员工工号" span={1}>
            {record.employee_no || '未知'}
          </Descriptions.Item>
          <Descriptions.Item label="考勤日期" span={2}>
            {record.date || '未知'}
          </Descriptions.Item>
          <Descriptions.Item label="上班时间" span={1}>
            {record.clock_in_time || '未打卡'}
          </Descriptions.Item>
          <Descriptions.Item label="下班时间" span={1}>
            {record.clock_out_time || '未打卡'}
          </Descriptions.Item>
          <Descriptions.Item label="异常类型" span={1}>
            <Tag color={getStatusColor(record.status)}>
              {record.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="处理状态" span={1}>
            <Tag color={getProcessStatusColor(record.process_status || 'unprocessed')}>
              {getProcessStatusText(record.process_status || 'unprocessed')}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="工作地点" span={2}>
            {record.location || '未知'}
          </Descriptions.Item>
          <Descriptions.Item label="备注" span={2}>
            {record.remarks || '无'}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间" span={2}>
            {record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '未知'}
          </Descriptions.Item>
        </Descriptions>
      ) : (
        <div style={{ textAlign: 'center', padding: '40px' }}>暂无数据</div>
      )}
    </Modal>
  );
};

export default ExceptionDetailModal;