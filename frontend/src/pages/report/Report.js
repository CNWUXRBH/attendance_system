import React, { useState, useEffect } from 'react';
import { Table, DatePicker, Select, Button, Space, message } from 'antd';
import { getReports, generateReport } from '../../services/report';
import request from '../../utils/request';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Report = () => {
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({});

  const fetchReports = async () => {
    const result = await getReports();
    // 后端返回的数据结构是 {reports: [...]}
    setData(result.reports || []);
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters({
      ...filters,
      [key]: value,
    });
  };

  const handleGenerateReport = async () => {
    try {
      // 转换前端filters格式为后端期望的格式
      const reportData = {
        report_type: filters.type || 'monthly',
        start_date: filters.dates && filters.dates[0] ? filters.dates[0].format('YYYY-MM-DD') : '2025-01-01',
        end_date: filters.dates && filters.dates[1] ? filters.dates[1].format('YYYY-MM-DD') : '2025-12-31'
      };
      await generateReport(reportData);
      fetchReports();
      message.success('报表生成成功');
    } catch (error) {
      message.error('报表生成失败');
    }
  };

  const handleDownload = async (record) => {
    try {
      const response = await request.get(`/api/reports/download/${record.id || 'default'}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `报表_${record.name || 'default'}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('下载成功');
    } catch (error) {
      message.error('下载失败');
    }
  };

  const handleView = async (record) => {
    try {
      const result = await request.get(`/api/reports/view/${record.id || 'default'}`);
      if (result.success) {
        message.success('报表详情获取成功');
        // 这里可以打开一个模态框显示详情
      } else {
        message.error('获取报表详情失败');
      }
    } catch (error) {
      message.error('获取报表详情失败');
    }
  };

  const handleExport = async () => {
    try {
      const startDate = filters.dates && filters.dates[0] ? filters.dates[0].format('YYYY-MM-DD') : '2025-01-01';
      const endDate = filters.dates && filters.dates[1] ? filters.dates[1].format('YYYY-MM-DD') : '2025-12-31';
      const response = await request.get('/api/reports/export_detailed', {
        params: { start_date: startDate, end_date: endDate },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `详细报表_${startDate}_${endDate}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const columns = [
    {
      title: '报表名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '生成日期',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => {
        if (!text) return '-';
        return new Date(text).toLocaleString('zh-CN');
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (text, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleDownload(record)}>下载</Button>
          <Button type="link" onClick={() => handleView(record)}>查看</Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">报表统计</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between mb-4">
          <Space>
            <RangePicker onChange={(dates) => handleFilterChange('dates', dates)} />
            <Select placeholder="选择报表类型" style={{ width: 200 }} onChange={(value) => handleFilterChange('type', value)} allowClear>
              <Option value="monthly">月度报表</Option>
              <Option value="exception">异常报表</Option>
              <Option value="attendance_rate">出勤率报表</Option>
            </Select>
            <Button type="primary" onClick={handleGenerateReport}>生成报表</Button>
          </Space>
          <Button onClick={handleExport}>导出</Button>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" />
      </div>
    </div>
  );
};

export default Report;