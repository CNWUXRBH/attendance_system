import request from '../utils/request';

export const getReports = (params) => {
  return request({
    method: 'GET',
    url: '/reports',
    params
  });
};

export const createReport = (data) => {
  return request({
    method: 'POST',
    url: '/reports',
    data
  });
};

export const exportReport = (params) => {
  return request({
    method: 'GET',
    url: '/reports/export_detailed',
    params,
    responseType: 'blob'
  });
};