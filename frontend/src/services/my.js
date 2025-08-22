import request from '../utils/request';

export const getProfile = () => {
  return request('/my/profile');
};

export const updateProfile = (data) => {
  return request('/my/profile', {
    method: 'PUT',
    data
  });
};

export const changePassword = (data) => {
  return request('/my/change-password', {
    method: 'POST',
    data
  });
};