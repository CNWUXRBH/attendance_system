import request from '../utils/request';

export async function getDashboardStats(params = {}) {
  const { date } = params;
  const queryParams = new URLSearchParams();
  
  if (date) queryParams.append('date', date);
  
  const url = `/api/dashboard/stats${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  
  return request(url, {
    method: 'GET',
  });
}

export async function getExceptionStats(params = {}) {
  const { date } = params;
  const queryParams = new URLSearchParams();

  if (date) queryParams.append('date', date);
  
  const url = `/api/dashboard/exception-stats${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  
  return request(url, {
    method: 'GET',
  });
}

export async function getExceptionRecords(params = {}) {
  const { date, limit = 10 } = params;
  const queryParams = new URLSearchParams();
  
  if (date) queryParams.append('date', date);
  if (limit) queryParams.append('limit', limit);
  
  const url = `/api/dashboard/exception-records${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  
  return request(url, {
    method: 'GET',
  });
}