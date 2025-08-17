import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { updateMyProfile } from '../services/my';


const EditProfileModal = ({ visible, onCancel, onSuccess, initialData }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);


  useEffect(() => {
    if (visible) {
      // 设置表单初始值
      if (initialData) {
        form.setFieldsValue({
          name: initialData.name,
          email: initialData.email,
          phone: initialData.phone,
          position: initialData.position,
        });
      }
    }
  }, [visible, initialData, form]);



  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await updateMyProfile(values);
      message.success('个人信息更新成功！');
      form.resetFields();
      onSuccess();
    } catch (error) {
      console.error('更新个人信息失败:', error);
      message.error('更新失败，请重试');
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
      title="编辑个人信息"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          label="姓名"
          name="name"
          rules={[
            { required: true, message: '请输入姓名' },
            { max: 50, message: '姓名不能超过50个字符' }
          ]}
        >
          <Input placeholder="请输入姓名" />
        </Form.Item>

        <Form.Item
          label="邮箱"
          name="email"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]}
        >
          <Input placeholder="请输入邮箱" />
        </Form.Item>

        <Form.Item
          label="手机号"
          name="phone"
          rules={[
            { required: true, message: '请输入手机号' },
            { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
          ]}
        >
          <Input placeholder="请输入手机号" />
        </Form.Item>

        <Form.Item
          label="职位"
          name="position"
          rules={[
            { required: true, message: '请输入职位' },
            { max: 50, message: '职位不能超过50个字符' }
          ]}
        >
          <Input placeholder="请输入职位" />
        </Form.Item>

        <Form.Item>
          <div style={{ textAlign: 'right' }}>
            <Button onClick={handleCancel} style={{ marginRight: 8 }}>
              取消
            </Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              保存
            </Button>
          </div>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditProfileModal;