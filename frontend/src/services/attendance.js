import request from '../utils/request';

export const getAttendanceRecords = (params) => {
  return request({
    method: 'GET',
    url: '/attendance',
    params
  });
};

export const createAttendanceRecord = (data) => {
  return request({
    method: 'POST',
    url: '/attendance',
    data
  });
};

export const updateAttendanceRecord = (recordId, data) => {
  return request({
    method: 'PUT',
    url: `/attendance/${recordId}`,
    data
  });
};

export const deleteAttendanceRecord = (recordId) => {
  return request({
    method: 'DELETE',
    url: `/attendance/${recordId}`
  });
};

export const importAttendanceRecords = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return request({
    method: 'POST',
    url: '/attendance/import',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const exportAttendanceRecords = (params) => {
  return request({
    method: 'GET',
    url: '/attendance/export',
    params,
    responseType: 'blob'
  });
};

export const getAttendanceStats = (params) => {
  return request({
    method: 'GET',
    url: '/attendance/stats',
    params
  });
};

export const processAttendanceStatus = (recordId, status) => {
  return request({
    method: 'PUT',
    url: `/attendance/${recordId}/process-status`,
    data: { status }
  });
};

export const getAttendanceRecord = (recordId) => {
  return request({
    method: 'GET',
    url: `/attendance/${recordId}`
  });
};