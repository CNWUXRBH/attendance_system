import React, { useState } from 'react';
import { Card, Form, Input, Button, message } from 'antd';
import { changePassword } from '../../services/my';

const Settings = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handlePasswordChange = async (values) => {
    if (values.newPassword !== values.confirmPassword) {
      message.error('新密码和确认密码不一致');
      return;
    }

    try {
      setLoading(true);
      await changePassword({
        current_password: values.currentPassword,
        new_password: values.newPassword
      });
      message.success('密码修改成功');
      form.resetFields();
    } catch (error) {
      console.error('密码修改失败:', error);
      message.error('密码修改失败，请检查当前密码是否正确');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">个人设置</h1>
      <Card>
        <h2 className="text-lg font-semibold mb-4">修改密码</h2>
        <Form form={form} layout="vertical" onFinish={handlePasswordChange}>
          <Form.Item 
            name="currentPassword"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item 
            name="newPassword"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少6位' }
            ]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item 
            name="confirmPassword"
            label="确认新密码"
            rules={[{ required: true, message: '请确认新密码' }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>更新密码</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings;