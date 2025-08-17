import request from '../utils/request';

export async function getMyProfile() {
  return request('/api/my/profile');
}

export async function updateMyProfile(data) {
  return request('/api/my/profile', {
    method: 'PUT',
    data
  });
}

export async function changePassword(data) {
  return request('/api/my/change-password', {
    method: 'POST',
    data
  });
}