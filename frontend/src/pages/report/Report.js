import React, { useState, useEffect } from 'react';
import { Table, DatePicker, Button, Space, message, Modal, Descriptions } from 'antd';
import { getReports, createReport } from '../../services/report';
import request from '../../utils/request';

const { RangePicker } = DatePicker;

const Report = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    dates: null
  });
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewData, setViewData] = useState(null);

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
      if (!filters.dates || !filters.dates[0] || !filters.dates[1]) {
        message.error('请选择时间范围');
        return;
      }
      
      // 生成月度考勤报表
      const monthlyReportData = {
        report_type: 'monthly',
        start_date: filters.dates[0].format('YYYY-MM-DD'),
        end_date: filters.dates[1].format('YYYY-MM-DD')
      };
      await createReport(monthlyReportData);
      
      // 生成异常考勤统计
      const exceptionReportData = {
        report_type: 'exception',
        start_date: filters.dates[0].format('YYYY-MM-DD'),
        end_date: filters.dates[1].format('YYYY-MM-DD')
      };
      await createReport(exceptionReportData);
      
      fetchReports();
      message.success('报表生成成功（包含月度考勤报表和异常考勤统计）');
    } catch (error) {
      message.error('报表生成失败');
    }
  };

  const handleDownload = async (record) => {
    try {
      const reportId = record.id || record.report_id || 'default';
      const response = await request.get(`/reports/download/${reportId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('报表下载成功');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败，请稍后重试');
    }
  };

  const handleView = async (record) => {
    try {
      const reportId = record.id || record.report_id || 'default';
      const result = await request.get(`/reports/view/${reportId}`);
      if (result.success) {
        setViewData({
          ...result,
          reportName: record.name,
          reportType: record.type
        });
        setViewModalVisible(true);
      } else {
        message.error('获取报表详情失败');
      }
    } catch (error) {
      console.error('查看失败:', error);
      message.error('获取报表详情失败');
    }
  };

  const handleExport = async () => {
    try {
      const startDate = filters.dates && filters.dates[0] ? filters.dates[0].format('YYYY-MM-DD') : '2025-01-01';
      const endDate = filters.dates && filters.dates[1] ? filters.dates[1].format('YYYY-MM-DD') : '2025-12-31';
      const response = await request.get('/reports/export_detailed', {
        params: { start_date: startDate, end_date: endDate },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `attendance_report_${startDate}_${endDate}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败，请稍后重试');
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
            <RangePicker onChange={(dates) => handleFilterChange('dates', dates)} placeholder={['开始日期', '结束日期']} />
            <Button type="primary" onClick={handleGenerateReport}>生成报表</Button>
          </Space>
          <Button onClick={handleExport}>导出详细报表</Button>
        </div>
        <Table 
          columns={columns} 
          dataSource={data} 
          rowKey={(record) => record.id || record.report_id || Math.random().toString(36).substr(2, 9)} 
        />
      </div>
      
      <Modal
        title="报表详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {viewData && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="报表名称">{viewData.reportName}</Descriptions.Item>
            <Descriptions.Item label="报表类型">{viewData.reportType === 'monthly' ? '月度考勤报表' : '异常考勤统计'}</Descriptions.Item>
            <Descriptions.Item label="报表ID">{viewData.report_id}</Descriptions.Item>
            <Descriptions.Item label="生成时间">{new Date(viewData.generated_at).toLocaleString('zh-CN')}</Descriptions.Item>
            <Descriptions.Item label="状态">{viewData.status === 'completed' ? '已完成' : viewData.status}</Descriptions.Item>
            <Descriptions.Item label="记录数量">{viewData.data?.records_count || 0} 条</Descriptions.Item>
            <Descriptions.Item label="日期范围">{viewData.data?.date_range || '未指定'}</Descriptions.Item>
            <Descriptions.Item label="摘要">{viewData.data?.summary || '无摘要'}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default Report;