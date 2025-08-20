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