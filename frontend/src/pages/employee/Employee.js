import { useState, useEffect } from 'react';
import { Table, Input, Button, Space, message, Modal, Upload } from 'antd';
import { Icon } from '@iconify/react';
import { getEmployees, deleteEmployee, importEmployees, exportEmployees } from '../../services/employee';
import AddEmployeeModal from './AddEmployeeModal';
import EditEmployeeModal from './EditEmployeeModal';

const { Search } = Input;

const Employee = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [isAddModalVisible, setIsAddModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);

  const fetchEmployees = async () => {
    const result = await getEmployees();
    setData(result);
    setFilteredData(result);
  };

  const handleSearch = (value) => {
    if (!value) {
      setFilteredData(data);
    } else {
      const filtered = data.filter(employee => 
        employee.name?.toLowerCase().includes(value.toLowerCase()) ||
        employee.employee_no?.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredData(filtered);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleAddSuccess = () => {
    setIsAddModalVisible(false);
    fetchEmployees();
  };

  const handleEditSuccess = () => {
    setIsEditModalVisible(false);
    setEditingEmployee(null);
    fetchEmployees();
  };

  const handleExport = async () => {
    try {
      const response = await exportEmployees();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `员工信息_${new Date().toISOString().split('T')[0]}.xlsx`);
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

  const handleImport = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      await importEmployees(formData);
      message.success('导入成功');
      fetchEmployees();
    } catch (error) {
      console.error('导入失败:', error);
      message.error('导入失败');
    }
    return false; // 阻止默认上传行为
  };

  const handleDeleteEmployee = (id) => {
    Modal.confirm({
      title: '确定删除该员工吗？',
      content: '删除后将无法恢复',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteEmployee(id);
          fetchEmployees();
          message.success('删除员工成功');
        } catch (error) {
          message.error('删除员工失败');
        }
      },
    });
  };

  const columns = [
    {
      title: '工号',
      dataIndex: 'employee_no',
      key: 'employee_no',
      width: 120,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 100,
    },
    {
      title: '性别',
      dataIndex: 'gender',
      key: 'gender',
      width: 80,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
      width: 130,
    },
    {
      title: '职位',
      dataIndex: 'position',
      key: 'position',
      width: 120,
    },
    {
      title: '入职日期',
      dataIndex: 'hire_date',
      key: 'hire_date',
      width: 120,
    },
    {
      title: '合同期限',
      dataIndex: 'contract_end_date',
      key: 'contract_end_date',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            onClick={() => {
              setEditingEmployee(record);
              setIsEditModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Button type="link" danger onClick={() => handleDeleteEmployee(record.employee_id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">人员管理</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between mb-4">
          <Search 
            placeholder="搜索员工姓名或工号" 
            style={{ width: 300 }} 
            onSearch={handleSearch}
            allowClear
          />
          <Space>
            <Upload
              accept=".xlsx,.xls"
              beforeUpload={handleImport}
              showUploadList={false}
            >
              <Button icon={<Icon icon="mdi:upload" />}>
                导入Excel
              </Button>
            </Upload>
            <Button
              icon={<Icon icon="mdi:download" />}
              onClick={handleExport}
            >
              导出Excel
            </Button>
            <Button
              type="primary"
              icon={<Icon icon="heroicons-outline:plus" />}
              onClick={() => setIsAddModalVisible(true)}
            >
              新增员工
            </Button>
          </Space>
        </div>
        <Table columns={columns} dataSource={filteredData} rowKey="employee_id" />
      </div>
      <AddEmployeeModal
        open={isAddModalVisible}
        onCancel={() => setIsAddModalVisible(false)}
        onSuccess={handleAddSuccess}
      />
      <EditEmployeeModal
        open={isEditModalVisible}
        onCancel={() => {
          setEditingEmployee(null);
          setIsEditModalVisible(false);
        }}
        onSuccess={handleEditSuccess}
        employee={editingEmployee}
      />
    </div>
  );
};

export default Employee;