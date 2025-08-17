import { useEffect, useState, useCallback } from 'react';
import { Card, Row, Col, Statistic, message, DatePicker, Table, Button, Tag } from 'antd';
import * as echarts from 'echarts';
import { 
  getDashboardStats, 
  getExceptionStats, 
  getExceptionRecords 
} from '../services/dashboard';
import { exportExceptionRecords } from '../services/report';

import moment from 'moment';
import { Icon } from '@iconify/react';
import ExceptionDetailModal from '../components/ExceptionDetailModal';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [exceptionStats, setExceptionStats] = useState([]);
  const [exceptionRecords, setExceptionRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(moment().format('YYYY-MM-DD'));
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedRecordId, setSelectedRecordId] = useState(null);

  const getExceptionChartOption = useCallback(() => {
    const chartData = exceptionStats.map(item => ({
      value: item.value,
      name: item.name
    }));

    return {
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
      legend: { 
        orient: 'vertical', 
        left: 'right', 
        top: 'center',
        textStyle: { color: '#666' }
      },
      series: [{
        name: '异常类型',
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false, position: 'center' },
        emphasis: { 
          label: { 
            show: true, 
            fontSize: '20', 
            fontWeight: 'bold' 
          }
        },
        labelLine: { show: false },
        data: chartData
      }]
    };
  }, [exceptionStats]);

  const initCharts = useCallback(() => {
    // 初始化异常类型分布图表
    const exceptionChartDom = document.getElementById('exceptionChart');
    if (exceptionChartDom) {
      const exceptionChart = echarts.init(exceptionChartDom);
      exceptionChart.setOption(getExceptionChartOption());
      
      // 窗口大小变化时重绘图表
      const resizeHandler = () => exceptionChart.resize();
      window.addEventListener('resize', resizeHandler);

      return () => {
        window.removeEventListener('resize', resizeHandler);
        exceptionChart.dispose();
      }
    }
  }, [getExceptionChartOption]);

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        date: selectedDate
      };
      
      const [statsRes, exceptionStatsRes, exceptionRecordsRes] = await Promise.all([
        getDashboardStats(params),
        getExceptionStats(params),
        getExceptionRecords(params)
      ]);
      
      setStats(statsRes);
      setExceptionStats(exceptionStatsRes || []);
      setExceptionRecords(exceptionRecordsRes || []);
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  useEffect(() => {
    if (exceptionStats.length > 0) {
      const cleanup = initCharts();
      return cleanup;
    }
  }, [exceptionStats, initCharts]);

  // 异常记录表格列配置
  const getExceptionColumns = () => [
    {
      title: '姓名',
      dataIndex: 'employee_name',
      key: 'employee_name',
    },
    {
      title: '工号',
      dataIndex: 'employee_no',
      key: 'employee_no',
    },
    {
      title: '异常类型',
      dataIndex: 'exception_type',
      key: 'exception_type',
      render: (text) => (
        <Tag color={getExceptionTagColor(text)}>
          {text}
        </Tag>
      ),
    },
    {
      title: '时间',
      dataIndex: 'time',
      key: 'time',
      render: (text) => text,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusConfig = {
          'unprocessed': { color: 'red', text: '未处理' },
          'processing': { color: 'orange', text: '处理中' },
          'processed': { color: 'green', text: '已处理' }
        };
        const config = statusConfig[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button 
          type="link" 
          style={{ color: '#2C5EFF' }}
          onClick={() => handleExceptionAction(record)}
        >
          {record.status === 'unprocessed' ? '标记处理' : '查看详情'}
        </Button>
      ),
    },
  ];

  // 获取异常类型标签颜色
  const getExceptionTagColor = (type) => {
    const colorMap = {
      '迟到': 'orange',
      '早退': 'orange',
      '迟到早退': 'orange',
      '缺卡': 'red',
      '缺勤': 'red',
      '位置异常': 'volcano'
    };
    return colorMap[type] || 'default';
  };

  // 处理异常记录操作
  const handleExceptionAction = (record) => {
    setSelectedRecordId(record.record_id);
    setDetailModalVisible(true);
  };

  // 处理状态更新后的回调
  const handleStatusUpdate = () => {
    fetchAllData();
  };

  // 导出异常记录报表
  const handleExportReport = async () => {
    try {
      const params = {
        start_date: selectedDate,
        end_date: selectedDate
      };
      const response = await exportExceptionRecords(params);
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `异常记录报表_${selectedDate}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败');
    }
  };

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5' }}>
      <Card 
        style={{ 
          marginBottom: '24px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.09)' 
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>今日考勤概览</h2>
          <div style={{ display: 'flex', gap: '12px' }}>
            <DatePicker
              value={moment(selectedDate)}
              onChange={(date) => setSelectedDate(date ? date.format('YYYY-MM-DD') : moment().format('YYYY-MM-DD'))}
              style={{ borderRadius: '5px' }}
            />
          </div>
        </div>
        
        {/* KPI卡片区域 */}
        <Row gutter={20} style={{ marginBottom: '32px' }}>
          <Col span={6}>
            <Card 
              style={{ 
                borderTop: '3px solid #4CAF50',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                borderRadius: '8px'
              }}
            >
              <Statistic
                title="今日出勤率"
                value={stats?.attendance_rate || 0}
                suffix="%"
                valueStyle={{ color: '#4CAF50', fontSize: '24px', fontWeight: 'bold' }}
                prefix={<Icon icon="ant-design:trending-up-outlined" style={{ color: '#4CAF50' }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card 
              style={{ 
                borderTop: '3px solid #FF6B6B',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                borderRadius: '8px'
              }}
            >
              <Statistic
                title="异常预警"
                value={stats?.abnormal_attendance || 0}
                suffix="例"
                valueStyle={{ color: '#FF6B6B', fontSize: '24px', fontWeight: 'bold' }}
                prefix={<Icon icon="ant-design:alert-outlined" style={{ color: '#FF6B6B' }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card 
              style={{ 
                borderTop: '3px solid #2C5EFF',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                borderRadius: '8px'
              }}
            >
              <Statistic
                title="在岗人数"
                value={stats?.present_today || 0}
                valueStyle={{ color: '#2C5EFF', fontSize: '24px', fontWeight: 'bold' }}
                prefix={<Icon icon="ant-design:team-outlined" style={{ color: '#2C5EFF' }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card 
              style={{ 
                borderTop: '3px solid #FFC107',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                borderRadius: '8px'
              }}
            >
              <Statistic
                title="迟到早退"
                value={stats?.abnormal_attendance || 0}
                suffix="例"
                valueStyle={{ color: '#FFC107', fontSize: '24px', fontWeight: 'bold' }}
                prefix={<Icon icon="ant-design:clock-circle-outlined" style={{ color: '#FFC107' }} />}
              />
            </Card>
          </Col>
        </Row>
        
        {/* 图表区域 */}
        <Row gutter={20} style={{ marginBottom: '32px' }}>
          <Col span={24}>
            <Card title="异常类型分布" style={{ height: '400px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.09)' }}>
               <div 
                 id="exceptionChart" 
                 style={{ height: '320px', width: '100%' }}
               ></div>
             </Card>
          </Col>
        </Row>
        
        {/* 异常记录表格 */}
        <Card 
          title="今日异常记录"
          extra={
            <Button 
              type="primary" 
              style={{ backgroundColor: '#2C5EFF', borderRadius: '5px' }}
              onClick={handleExportReport}
            >
              导出报表
            </Button>
          }
          style={{ borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.09)' }}
        >
          <Table
            dataSource={exceptionRecords}
            columns={getExceptionColumns()}
            pagination={{ pageSize: 10 }}
            loading={loading}
            rowKey="record_id"
          />
        </Card>
      </Card>
      
      <ExceptionDetailModal
        visible={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        recordId={selectedRecordId}
        onStatusUpdate={handleStatusUpdate}
      />
    </div>
  );
};

export default Dashboard;