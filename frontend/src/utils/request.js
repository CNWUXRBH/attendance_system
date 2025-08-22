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

// 创建axios实例
const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001',
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 重试配置
const retryConfig = {
  retries: 2,
  retryDelay: 1000,
  retryCondition: (error) => {
    return axios.isAxiosError(error) && 
           (error.code === 'ECONNABORTED' || 
            error.response?.status >= 500);
  }
};

// 重试拦截器
const retryInterceptor = async (error) => {
  const { config } = error;
  
  if (!config || !retryConfig.retryCondition(error)) {
    return Promise.reject(error);
  }
  
  config.__retryCount = config.__retryCount || 0;
  
  if (config.__retryCount >= retryConfig.retries) {
    return Promise.reject(error);
  }
  
  config.__retryCount += 1;
  
  // 延迟重试
  await new Promise(resolve => setTimeout(resolve, retryConfig.retryDelay * config.__retryCount));
  
  return instance(config);
};

// 请求拦截器 - 添加认证token
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 如果是FormData，删除Content-Type让浏览器自动设置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    // 添加请求时间戳，用于调试
    if (process.env.NODE_ENV === 'development') {
      config.metadata = { startTime: new Date() };
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
      const duration = new Date() - response.config.metadata?.startTime;
      console.log(`API响应 [${response.config.method?.toUpperCase()}] ${response.config.url}:`, {
        data: response.config.responseType === 'blob' ? '[Blob Data]' : response.data,
        duration: `${duration}ms`
      });
    }
    // 对于blob类型的响应，返回完整的response对象，其他情况返回data
    return response.config.responseType === 'blob' ? response : response.data;
  },
  async error => {
    // 尝试重试
    try {
      return await retryInterceptor(error);
    } catch (retryError) {
      error = retryError;
    }
    
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
      case 429:
        message.error('请求过于频繁，请稍后重试');
        break;
      default:
        message.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

// 导出实例和工具函数
export default instance;

// 工具函数
export const createRequest = (config) => instance(config);
export const get = (url, config) => instance.get(url, config);
export const post = (url, data, config) => instance.post(url, data, config);
export const put = (url, data, config) => instance.put(url, data, config);
export const del = (url, config) => instance.delete(url, config);