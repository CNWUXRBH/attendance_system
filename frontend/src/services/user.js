import request from '../utils/request';

export async function login(data) {
  return request({
    url: '/api/auth/login',
    method: 'POST',
    data: data
  });
}

export async function getInfo() {
  return request({
    url: '/api/employees/me',
    method: 'GET'
  });
}