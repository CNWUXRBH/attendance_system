import axios from 'axios';
import { message } from 'antd';

// 错误码映射
const ERROR_MESSAGES = {
  400: '请求参数错误',
  401: '未授权，请重新登录',
  403: '拒绝访问',
  404: '请求的资源不存在',
  408: '请求超时',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务不可用',
  504: '网关超时'
};

const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001',
  timeout: 300000,
});

// 请求拦截器 - 添加认证token
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => {
    // 开发环境下显示API响应日志
    if (process.env.NODE_ENV === 'development') {
      console.log('API响应:', response.data);
    }
    return response.data;
  },
  error => {
    console.error('API错误:', error);
    
    // 网络错误处理
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        message.error('请求超时，请稍后重试');
      } else {
        message.error('网络连接失败，请检查网络设置');
      }
      return Promise.reject(error);
    }

    // HTTP状态码错误处理
    const { status, data } = error.response;
    const errorMessage = data?.message || ERROR_MESSAGES[status] || '请求失败';
    
    // 特殊状态码处理
    switch (status) {
      case 401:
        const url = error.config?.url || '';
        // 只有非登录相关接口返回401时才清除token
        if (!url.includes('/auth/login') && !url.includes('/auth/token')) {
          localStorage.removeItem('token');
          localStorage.removeItem('userInfo');
          window.location.href = '/login';
        }
        message.error(errorMessage);
        break;
      case 403:
        message.error('权限不足，无法访问该资源');
        break;
      default:
        message.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

export default instance;