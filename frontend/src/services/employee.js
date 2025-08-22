import request from '../utils/request';

export const getEmployees = (params) => {
  return request({
    method: 'GET',
    url: '/employees',
    params
  });
};

export const createEmployee = (data) => {
  return request({
    method: 'POST',
    url: '/employees',
    data
  });
};

export const updateEmployee = (id, data) => {
  return request({
    method: 'PUT',
    url: `/employees/${id}`,
    data
  });
};

export const deleteEmployee = (id) => {
  return request({
    method: 'DELETE',
    url: `/employees/${id}`
  });
};

export const importEmployees = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return request({
    method: 'POST',
    url: '/employees/import',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const exportEmployees = (params) => {
  return request({
    method: 'GET',
    url: '/employees/export',
    params,
    responseType: 'blob'
  });
};