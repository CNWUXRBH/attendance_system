import request from '../utils/request';

export const getDashboardStats = (params) => {
  const queryParams = new URLSearchParams();
  
  if (params.date) {
    queryParams.append('date', params.date);
  }
  
  const url = `/dashboard/stats${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  
  return request({
    method: 'GET',
    url
  });
};