import request from '../utils/request';

export const getDepartments = () => {
  return request('/api/departments', {
    method: 'GET',
  });
};