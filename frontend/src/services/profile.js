import request from '../utils/request';

export const getProfile = () => {
  return request({
    method: 'GET',
    url: '/profile'
  });
};

export const updateProfile = (data) => {
  return request({
    method: 'PUT',
    url: '/profile',
    data
  });
};