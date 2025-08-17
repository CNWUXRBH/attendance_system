import request from '../utils/request';

export async function getSchedules(year, month) {
  return request({
    url: `/api/schedules?year=${year}&month=${month}`,
    method: 'GET'
  });
}

export async function addSchedule(data) {
  return request({
    url: '/api/schedules',
    method: 'POST',
    data: data
  });
}

export async function updateSchedule(id, data) {
  return request({
    url: `/api/schedules/${id}`,
    method: 'PUT',
    data: data
  });
}

export async function deleteSchedule(id) {
  return request({
    url: `/api/schedules/${id}`,
    method: 'DELETE'
  });
}

// 批量操作
export async function batchCreateSchedules(schedules) {
  return request({
    url: '/api/schedules/batch',
    method: 'POST',
    data: { schedules }
  });
}

// 复制排班
export async function copySchedules({
  sourceYear,
  sourceMonth,
  targetYear,
  targetMonth,
  employeeIds
}) {
  return request({
    url: '/api/schedules/copy',
    method: 'POST',
    data: {
      sourceYear,
      sourceMonth,
      targetYear,
      targetMonth,
      employeeIds
    }
  });
}

// 检查排班冲突
export async function checkScheduleConflicts(schedules) {
  return request({
    url: '/api/schedules/conflicts',
    method: 'GET',
    params: {
      schedules: JSON.stringify(schedules)
    }
  });
}

// 班次模板相关
export async function applyShiftTemplate({
  templateId,
  year,
  month,
  employeeIds,
  dates
}) {
  return request({
    url: '/api/shift_templates/apply',
    method: 'POST',
    data: {
      templateId,
      year,
      month,
      employeeIds,
      dates
    }
  });
}

// 获取班次模板
export async function getShiftTemplates() {
  return request({
    url: '/api/shift_templates',
    method: 'GET'
  });
}

// 创建班次模板
export async function createShiftTemplate(data) {
  return request({
    url: '/api/shift_templates',
    method: 'POST',
    data: data
  });
}

// 更新班次模板
export async function updateShiftTemplate(id, data) {
  return request({
    url: `/api/shift_templates/${id}`,
    method: 'PUT',
    data: data
  });
}

// 删除班次模板
export async function deleteShiftTemplate(id) {
  return request({
    url: `/api/shift_templates/${id}`,
    method: 'DELETE'
  });
}