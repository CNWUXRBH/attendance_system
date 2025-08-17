import request from '../utils/request';

export async function getExceptionRules() {
  return request({
    url: '/api/exception-rules',
    method: 'GET'
  });
}

export async function addExceptionRule(data) {
  return request({
    url: '/api/exception-rules',
    method: 'POST',
    data: data
  });
}

export async function updateExceptionRule(id, data) {
  return request({
    url: `/api/exception-rules/${id}`,
    method: 'PUT',
    data: data
  });
}

export async function deleteExceptionRule(id) {
  return request({
    url: `/api/exception-rules/${id}`,
    method: 'DELETE'
  });
}