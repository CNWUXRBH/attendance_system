import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, TimePicker, Select, message } from 'antd';
import { createShiftTemplate, updateShiftTemplate } from '../../services/schedule';
import moment from 'moment';

const { Option } = Select;

const TemplateModal = ({ visible, onCancel, onOk, template = null }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const isEdit = !!template;

  useEffect(() => {
    if (visible && template) {
      form.setFieldsValue({
        name: template.name,
        description: template.description,
        shift_type_id: template.shift_type_id,
        start_time: template.start_time ? moment(template.start_time, 'HH:mm:ss') : null,
        end_time: template.end_time ? moment(template.end_time, 'HH:mm:ss') : null,
      });
    } else if (visible) {
      form.resetFields();
    }
  }, [visible, template, form]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      const templateData = {
        name: values.name,
        description: values.description,
        shift_type_id: values.shift_type_id,
        start_time: values.start_time.format('HH:mm:ss'),
        end_time: values.end_time.format('HH:mm:ss'),
      };
      
      if (isEdit) {
        await updateShiftTemplate(template.id, templateData);
        message.success('模板更新成功');
      } else {
        await createShiftTemplate(templateData);
        message.success('模板创建成功');
      }
      
      form.resetFields();
      onOk();
    } catch (error) {
      message.error(isEdit ? '模板更新失败' : '模板创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title={isEdit ? '编辑排班模板' : '新建排班模板'}
      visible={visible}
      onOk={handleOk}
      onCancel={handleCancel}
      okText="保存"
      cancelText="取消"
      confirmLoading={loading}
    >
      <Form form={form} layout="vertical" name="template_form">
        <Form.Item
          name="name"
          label="模板名称"
          rules={[{ required: true, message: '请输入模板名称' }]}
        >
          <Input placeholder="请输入模板名称" />
        </Form.Item>
        
        <Form.Item
          name="description"
          label="模板描述"
        >
          <Input.TextArea placeholder="请输入模板描述" rows={3} />
        </Form.Item>
        
        <Form.Item
          name="shift_type_id"
          label="班次类型"
          rules={[{ required: true, message: '请选择班次类型' }]}
        >
          <Select placeholder="请选择班次类型">
            <Option value={1}>早班</Option>
            <Option value={2}>中班</Option>
            <Option value={3}>晚班</Option>
          </Select>
        </Form.Item>
        
        <Form.Item
          name="start_time"
          label="开始时间"
          rules={[{ required: true, message: '请选择开始时间' }]}
        >
          <TimePicker format="HH:mm" placeholder="请选择开始时间" />
        </Form.Item>
        
        <Form.Item
          name="end_time"
          label="结束时间"
          rules={[{ required: true, message: '请选择结束时间' }]}
        >
          <TimePicker format="HH:mm" placeholder="请选择结束时间" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default TemplateModal;