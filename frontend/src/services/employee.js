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

export const importEmployees = (formData) => {
  return request({
    method: 'POST',
    url: '/employees/import',
    data: formData
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