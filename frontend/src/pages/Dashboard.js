import { useEffect, useState, useCallback } from 'react';
import { Card, Row, Col, Statistic, message, DatePicker, Table, Tag } from 'antd';
import { getDashboardStats } from '../services/dashboard';
import { getAttendanceRecords } from '../services/attendance';
import dayjs from 'dayjs';
import { Icon } from '@iconify/react';

const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(dayjs().format('YYYY-MM-DD'));



  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        date: selectedDate
      };
      
      const statsRes = await getDashboardStats(params);
      setStats(statsRes);
      
      // 获取今日考勤记录
      const attendanceParams = {
        startDate: selectedDate,
        endDate: selectedDate,
        limit: 10 // 限制显示最近10条记录
      };
      const attendanceRes = await getAttendanceRecords(attendanceParams);
      setAttendanceRecords(Array.isArray(attendanceRes) ? attendanceRes : []);
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

  // 考勤记录表格列配置
  const getAttendanceColumns = () => [
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
      title: '上班时间',
      dataIndex: 'clock_in_time',
      key: 'clock_in_time',
      render: (text) => text ? dayjs(text).format('HH:mm') : '-',
    },
    {
      title: '下班时间',
      dataIndex: 'clock_out_time',
      key: 'clock_out_time',
      render: (text) => text ? dayjs(text).format('HH:mm') : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusConfig = {
          '正常': { color: 'green', text: '正常' },
          '迟到': { color: 'orange', text: '迟到' },
          '早退': { color: 'orange', text: '早退' },
          '缺勤': { color: 'red', text: '缺勤' }
        };
        const config = statusConfig[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
  ];



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
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>考勤概览</h2>
          <div style={{ display: 'flex', gap: '12px' }}>
            <DatePicker
              value={selectedDate ? dayjs(selectedDate) : dayjs()}
              onChange={(date) => {
                if (date) {
                  setSelectedDate(date.format('YYYY-MM-DD'));
                } else {
                  setSelectedDate(dayjs().format('YYYY-MM-DD'));
                }
              }}
              format="YYYY-MM-DD"
              allowClear={false}
              style={{ borderRadius: '5px' }}
            />
          </div>
        </div>
        
        {/* KPI卡片区域 */}
        <Row gutter={20} style={{ marginBottom: '32px' }}>
          <Col span={12}>
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
          <Col span={12}>
            <Card 
              style={{ 
                borderTop: '3px solid #FFC107',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                borderRadius: '8px'
              }}
            >
              <Statistic
                title="总员工数"
                value={stats?.total_employees || 0}
                valueStyle={{ color: '#FFC107', fontSize: '24px', fontWeight: 'bold' }}
                prefix={<Icon icon="ant-design:user-outlined" style={{ color: '#FFC107' }} />}
              />
            </Card>
          </Col>
        </Row>

        
        {/* 考勤记录表格 */}
        <Card 
          title="今日考勤记录"
          style={{ borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.09)' }}
        >
          <Table
            dataSource={attendanceRecords}
            columns={getAttendanceColumns()}
            pagination={{ pageSize: 10 }}
            loading={loading}
            rowKey="record_id"
          />
        </Card>
      </Card>

    </div>
  );
};

export default Dashboard;