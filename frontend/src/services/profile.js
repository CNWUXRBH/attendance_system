import request from '../utils/request';

export async function getProfile() {
  return request({
    url: '/api/profile',
    method: 'GET'
  });
}

export async function updateProfile(data) {
  return request({
    url: '/api/profile',
    method: 'PUT',
    data: data
  });
}