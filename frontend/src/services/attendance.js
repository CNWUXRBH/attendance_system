import request from '../utils/request';

export async function getAttendanceRecords(params) {
  return request({
    url: '/api/attendance',
    method: 'GET',
    params: params
  });
}

export async function addAttendanceRecord(data) {
  return request({
    url: '/api/attendance',
    method: 'POST',
    data: data
  });
}

export async function updateAttendanceRecord(recordId, data) {
  return request({
    url: `/api/attendance/${recordId}`,
    method: 'PUT',
    data: data
  });
}

export async function deleteAttendanceRecord(recordId) {
  return request({
    url: `/api/attendance/${recordId}`,
    method: 'DELETE'
  });
}

export async function importAttendanceRecords(file) {
  const formData = new FormData();
  formData.append('file', file);
  return request({
    url: '/api/attendance/import',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });
}

export async function exportAttendanceRecords(params) {
  return request({
    url: '/api/attendance/export',
    method: 'GET',
    params: params,
    responseType: 'blob'
  });
}

export async function syncExternalAttendance() {
  return request({
    url: '/api/attendance/sync-external',
    method: 'POST'
  });
}

// 更新考勤记录处理状态
export async function updateAttendanceStatus(recordId, processStatus, remarks) {
  return request({
    url: `/api/attendance/${recordId}/process-status`,
    method: 'PATCH',
    params: {
      process_status: processStatus,
      remarks: remarks
    }
  });
}

export async function getAttendanceRecordDetail(recordId) {
  return request({
    url: `/api/attendance/${recordId}`,
    method: 'GET'
  });
}