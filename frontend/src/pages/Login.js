import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { UserOutlined, LockOutlined, DashboardOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/user';

const { Title, Text } = Typography;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await login(values);
      localStorage.setItem('token', response.access_token);
      message.success('登录成功');
      navigate('/');
    } catch (error) {
      message.error('登录失败，请检查您的用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      {/* 左侧深色品牌区域 */}
      <div style={{
        flex: 1,
        background: 'linear-gradient(135deg, #001529 0%, #002140 50%, #003a5c 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        padding: '40px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <DashboardOutlined style={{ fontSize: '80px', marginBottom: '24px', color: 'white' }} />
          <Title level={1} style={{ color: 'white', marginBottom: '16px', fontSize: '36px' }}>
            考勤管理系统
          </Title>
          <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '18px', lineHeight: '1.6' }}>
            智能化员工考勤管理平台<br/>
            提供全面的考勤跟踪、排班管理和数据分析
          </Text>
        </div>
      </div>
      
      {/* 右侧登录表单区域 */}
      <div style={{
        flex: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px'
      }}>
        <Card 
          style={{
            width: '100%',
            maxWidth: '400px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            borderRadius: '12px',
            border: 'none'
          }}
          styles={{ body: { padding: '40px' } }}
        >
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <Title level={2} style={{ color: '#001529', marginBottom: '8px' }}>
              欢迎登录
            </Title>
            <Text type="secondary" style={{ fontSize: '14px' }}>
              请输入您的账号信息
            </Text>
          </div>
          
          <Form
            name="normal_login"
            onFinish={onFinish}
            size="large"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名!' }]}
            >
              <Input 
                prefix={<UserOutlined style={{ color: '#001529' }} />} 
                placeholder="用户名"
                style={{
                  borderRadius: '8px',
                  padding: '12px 16px',
                  fontSize: '14px'
                }}
              />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码!' }]}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: '#001529' }} />}
                placeholder="密码"
                style={{
                  borderRadius: '8px',
                  padding: '12px 16px',
                  fontSize: '14px'
                }}
              />
            </Form.Item>
            
            <Form.Item style={{ marginBottom: '16px' }}>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                block
                style={{
                  height: '48px',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '500',
                  background: 'linear-gradient(135deg, #001529 0%, #003a5c 100%)',
                  border: 'none',
                  boxShadow: '0 4px 12px rgba(0, 21, 41, 0.3)'
                }}
              >
                登录
              </Button>
            </Form.Item>
          </Form>
          
          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              © 2024 考勤管理系统. 保留所有权利.
            </Text>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;