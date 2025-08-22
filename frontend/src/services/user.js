import request from '../utils/request';

export const login = (credentials) => {
  return request({
    method: 'POST',
    url: '/auth/login',
    data: credentials
  });
};

export const getCurrentUser = () => {
  return request({
    method: 'GET',
    url: '/employees/me'
  });
};