import React, { useState, useEffect } from 'react';
import { Table, DatePicker, Input, Button, Space, message, Upload, Popconfirm } from 'antd';
import { PlusOutlined, UploadOutlined, DownloadOutlined, EditOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';
import { getAttendanceRecords, deleteAttendanceRecord, importAttendanceRecords, exportAttendanceRecords, syncExternalAttendance } from '../../services/attendance';
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
  const [apiStatus, setApiStatus] = useState('connected');
  const [lastSyncTime, setLastSyncTime] = useState(new Date());
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchAttendances = async (params) => {
    try {
      const result = await getAttendanceRecords(params);
      setData(result);
      setApiStatus('connected');
      setLastSyncTime(new Date());
    } catch (error) {
      setApiStatus('disconnected');
      console.error('Failed to fetch attendances:', error);
    }
  };

  const handleSyncFromExternal = async () => {
    setIsSyncing(true);
    try {
      const result = await syncExternalAttendance();
      
      // 检查同步状态
      if (result.status === 'failed') {
        message.error(`同步失败: ${result.message || '未知错误'}`);
        setApiStatus('disconnected');
      } else if (result.status === 'success') {
        message.success(`${result.message || '同步成功'}，处理了 ${result.records_count || 0} 条记录`);
        setApiStatus('connected');
        setLastSyncTime(new Date());
        await fetchAttendances();
      } else {
        message.warning(`同步状态未知: ${result.message || '请检查系统状态'}`);
      }
    } catch (error) {
      message.error('同步请求失败: ' + (error.message || '网络连接错误'));
      setApiStatus('disconnected');
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchAttendances();
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = () => {
    const params = {
      startDate: filters.dates?.[0]?.format('YYYY-MM-DD'),
      endDate: filters.dates?.[1]?.format('YYYY-MM-DD'),
      name: filters.name
    };
    fetchAttendances(params);
  };

  const handleAdd = () => {
    setSelectedRecord(null);
    setIsEditMode(false);
    setIsEditModalVisible(true);
  };

  const handleEdit = (record) => {
    setSelectedRecord(record);
    setIsEditMode(true);
    setIsEditModalVisible(true);
  };

  const handleDelete = async (recordId) => {
    try {
      await deleteAttendanceRecord(recordId);
      message.success('删除成功');
      fetchAttendances();
    } catch (error) {
      message.error('删除失败');
    }
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
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这条考勤记录吗？"
            onConfirm={() => handleDelete(record.record_id)}
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
      
      {/* API状态指示器 */}
      <div className="bg-white mt-4 p-4 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                apiStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                API 连接状态：{apiStatus === 'connected' ? '已连接' : '连接失败'}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              最后同步时间：{lastSyncTime.toLocaleString('zh-CN')}
            </div>
          </div>
          <Button 
            type="primary" 
            icon={<SyncOutlined spin={isSyncing} />}
            onClick={handleSyncFromExternal}
            loading={isSyncing}
          >
            同步数据
          </Button>
        </div>
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