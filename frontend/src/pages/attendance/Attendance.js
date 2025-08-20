import React, { useState, useEffect } from 'react';
import { Table, DatePicker, Input, Button, Space, message, Upload } from 'antd';
import { PlusOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import { getAttendanceRecords, importAttendanceRecords, exportAttendanceRecords } from '../../services/attendance';
import AttendanceDetailModal from './AttendanceDetailModal';
import AttendanceEditModal from './AttendanceEditModal';

const { RangePicker } = DatePicker;

const Attendance = () => {
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({
    dates: [],
    name: ''
  });
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isEditMode, setIsEditMode] = useState(true);

  const fetchAttendances = async (params) => {
    try {
      console.log('fetchAttendances called with params:', params);
      const result = await getAttendanceRecords(params);
      console.log('API response result:', result);
      console.log('Result type:', typeof result);
      console.log('Result length:', Array.isArray(result) ? result.length : 'Not an array');
      setData(result);
    } catch (error) {
      console.error('Failed to fetch attendances:', error);
    }
  };



  useEffect(() => {
    fetchAttendances({});
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = () => {
    const params = {};
    
    // 只有当用户设置了日期过滤器时才添加日期参数
    if (filters.dates && filters.dates.length === 2) {
      params.startDate = filters.dates[0]?.format('YYYY-MM-DD');
      params.endDate = filters.dates[1]?.format('YYYY-MM-DD');
    }
    
    // 只有当用户输入了姓名时才添加姓名参数
    if (filters.name && filters.name.trim()) {
      params.name = filters.name.trim();
    }
    
    fetchAttendances(params);
  };

  const handleAdd = () => {
    setSelectedRecord(null);
    setIsEditMode(false);
    setIsEditModalVisible(true);
  };



  const handleImport = async (file) => {
    try {
      await importAttendanceRecords(file);
      message.success('导入成功');
      fetchAttendances();
      return false;
    } catch (error) {
      message.error('导入失败');
      return false;
    }
  };

  const handleExport = async () => {
    try {
      const response = await exportAttendanceRecords();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `考勤记录_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const handleModalSuccess = () => {
    fetchAttendances();
  };

  const columns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '上班时间',
      dataIndex: 'checkIn',
      key: 'checkIn',
    },
    {
      title: '下班时间',
      dataIndex: 'checkOut',
      key: 'checkOut',
    },
    {
      title: '考勤状态',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            onClick={() => {
              setSelectedRecord(record);
              setIsDetailModalVisible(true);
            }}
          >
            详情
          </Button>


        </Space>
      ),
    },
  ];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <div className="bg-white p-6 rounded-lg shadow">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2>考勤记录</h2>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              手动补录
            </Button>
            <Upload
              beforeUpload={handleImport}
              showUploadList={false}
              accept=".xlsx,.xls"
            >
              <Button icon={<UploadOutlined />}>
                导入考勤
              </Button>
            </Upload>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              导出考勤
            </Button>
          </Space>
        </div>
        <div className="flex justify-between mb-4">
          <Space>
            <RangePicker onChange={(dates) => handleFilterChange('dates', dates)} />
            <Input
              placeholder="搜索员工"
              style={{ width: 200 }}
              onChange={(e) => handleFilterChange('name', e.target.value)}
            />
            <Button type="primary" onClick={handleSearch}>查询</Button>
          </Space>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" />
      </div>
      

      
      <AttendanceDetailModal
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        record={selectedRecord}
      />
      <AttendanceEditModal
        open={isEditModalVisible}
        onCancel={() => setIsEditModalVisible(false)}
        onSuccess={handleModalSuccess}
        record={selectedRecord}
        isEdit={isEditMode}
      />
    </div>
  );
};

export default Attendance;