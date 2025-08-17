import React, { useEffect } from 'react';
import { Modal, Form, Input, DatePicker, Select } from 'antd';
import moment from 'moment';

const { Option } = Select;

const EditScheduleModal = ({ open, onCancel, onSubmit, schedule, employees }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (schedule) {
      form.setFieldsValue({
        ...schedule,
        date: moment(schedule.date),
      });
    }
  }, [schedule, form]);

  const handleOk = () => {
    form
      .validateFields()
      .then((values) => {
        onSubmit(schedule.id, values);
        form.resetFields();
      })
      .catch((info) => {
        // 表单验证失败
      });
  };

  return (
    <Modal
      title="编辑排班"
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      okText="提交"
      cancelText="取消"
    >
      <Form form={form} layout="vertical" name="schedule_form">
        <Form.Item
          name="date"
          label="日期"
          rules={[{ required: true, message: '请选择日期' }]}
        >
          <DatePicker />
        </Form.Item>
        <Form.Item
          name="content"
          label="排班内容"
          rules={[{ required: true, message: '请输入排班内容' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="type"
          label="类型"
          rules={[{ required: true, message: '请选择类型' }]}
        >
          <Select placeholder="请选择类型">
            <Option value="success">正常</Option>
            <Option value="warning">警告</Option>
            <Option value="error">错误</Option>
          </Select>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditScheduleModal;