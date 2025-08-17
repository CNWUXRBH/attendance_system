import React from 'react';
import { Modal, Form, Input, DatePicker, Select, message } from 'antd';
import { addEmployee } from '../../services/employee';

const { Option } = Select;

const AddEmployeeModal = ({ open, onCancel, onSuccess }) => {
  const [form] = Form.useForm();

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      // 格式化日期
      const formattedValues = {
        ...values,
        hire_date: values.hire_date?.format('YYYY-MM-DD'),
        contract_end_date: values.contract_end_date?.format('YYYY-MM-DD'),
      };
      await addEmployee(formattedValues);
      message.success('员工添加成功');
      form.resetFields();
      onSuccess();
    } catch (error) {
      console.error('添加员工失败:', error);
      message.error('添加员工失败');
    }
  };

  return (
    <Modal
      title="添加员工"
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      okText="确定"
      cancelText="取消"
      width={600}
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="employee_no"
          label="工号"
          rules={[{ required: true, message: '请输入工号' }]}
        >
          <Input placeholder="请输入员工工号" />
        </Form.Item>
        <Form.Item
          name="name"
          label="姓名"
          rules={[{ required: true, message: '请输入姓名' }]}
        >
          <Input placeholder="请输入员工姓名" />
        </Form.Item>
        <Form.Item
          name="gender"
          label="性别"
          rules={[{ required: true, message: '请选择性别' }]}
        >
          <Select placeholder="请选择性别">
            <Option value="男">男</Option>
            <Option value="女">女</Option>
          </Select>
        </Form.Item>
        <Form.Item
          name="email"
          label="邮箱"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]}
        >
          <Input placeholder="请输入邮箱地址" />
        </Form.Item>
        <Form.Item
          name="phone"
          label="电话"
          rules={[{ required: true, message: '请输入电话号码' }]}
        >
          <Input placeholder="请输入电话号码" />
        </Form.Item>
        <Form.Item
          name="password"
          label="密码"
          rules={[{ required: true, message: '请输入密码' }]}
        >
          <Input.Password placeholder="请输入登录密码" />
        </Form.Item>
        <Form.Item
          name="position"
          label="职位"
          rules={[{ required: true, message: '请输入职位' }]}
        >
          <Input placeholder="请输入职位" />
        </Form.Item>
        <Form.Item
          name="hire_date"
          label="入职日期"
          rules={[{ required: true, message: '请选择入职日期' }]}
        >
          <DatePicker style={{ width: '100%' }} placeholder="请选择入职日期" />
        </Form.Item>
        <Form.Item
          name="contract_end_date"
          label="合同期限"
        >
          <DatePicker style={{ width: '100%' }} placeholder="请选择合同到期日期" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default AddEmployeeModal;