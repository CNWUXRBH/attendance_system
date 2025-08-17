import request from '../utils/request';

export async function getReports(params) {
  return request({
    url: '/api/reports',
    method: 'GET',
    params: params
  });
}

export async function generateReport(data) {
  return request({
    url: '/api/reports',
    method: 'POST',
    data: data
  });
}

export async function exportExceptionRecords(params) {
  return request({
    url: '/api/reports/export_detailed',
    method: 'GET',
    params: params,
    responseType: 'blob'
  });
}