import request from '../utils/request';

export async function getEmployees() {
  return request({
    url: '/api/employees',
    method: 'GET'
  });
}

export async function addEmployee(data) {
  return request({
    url: '/api/employees',
    method: 'POST',
    data: data
  });
}

export async function updateEmployee(id, data) {
  return request({
    url: `/api/employees/${id}`,
    method: 'PUT',
    data: data
  });
}

export async function deleteEmployee(id) {
  return request({
    url: `/api/employees/${id}`,
    method: 'DELETE'
  });
}

export async function importEmployees(formData) {
  return request({
    url: '/api/employees/import',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });
}

export async function exportEmployees() {
  return request({
    url: '/api/employees/export',
    method: 'GET',
    responseType: 'blob'
  });
}