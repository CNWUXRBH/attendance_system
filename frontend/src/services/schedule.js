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
export async function batchCreateSchedules(schedules, options = {}) {
  const { ignoreConflicts = false, validateOnly = false } = options;
  return request({
    url: '/api/schedules/batch',
    method: 'POST',
    data: schedules,
    params: {
      ignore_conflicts: ignoreConflicts,
      validate_only: validateOnly
    }
  });
}

// 复制排班
export async function copySchedules({
  sourceScheduleId,
  targetDates,
  ignoreConflicts = false
}) {
  return request({
    url: '/api/schedules/copy',
    method: 'POST',
    data: {
      source_schedule_id: sourceScheduleId,
      target_dates: targetDates
    },
    params: {
      ignore_conflicts: ignoreConflicts
    }
  });
}

// 检查排班冲突
export async function checkScheduleConflicts({
  employeeId,
  startDate,
  endDate,
  scheduleId = null
}) {
  return request({
    url: '/api/schedules/conflicts',
    method: 'GET',
    params: {
      employee_id: employeeId,
      start_date: startDate,
      end_date: endDate,
      schedule_id: scheduleId
    }
  });
}

// 批量检查排班冲突（用于日历视图）
export async function batchCheckConflicts(schedules) {
  const conflictPromises = schedules.map(schedule => 
    checkScheduleConflicts({
      employeeId: schedule.employee_id,
      startDate: schedule.start_date,
      endDate: schedule.end_date,
      scheduleId: schedule.id
    }).catch(() => ({ data: { has_conflict: false } })) // 错误时默认无冲突
  );
  
  const results = await Promise.all(conflictPromises);
  return results.map((result, index) => ({
    ...schedules[index],
    conflict_info: result.data
  }));
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

// ==================== 状态管理相关API ====================

// 排班状态转换
export async function transitionScheduleStatus(scheduleId, transitionData) {
  return request({
    url: `/api/schedules/${scheduleId}/status`,
    method: 'PUT',
    data: transitionData
  });
}

// 批量状态操作
export async function batchStatusOperation(operationData) {
  return request({
    url: '/api/schedules/batch-status',
    method: 'POST',
    data: operationData
  });
}

// 根据状态获取排班列表
export async function getSchedulesByStatus(status, options = {}) {
  const { skip = 0, limit = 100 } = options;
  return request({
    url: `/api/schedules/status/${status}`,
    method: 'GET',
    params: { skip, limit }
  });
}

// 获取待审核的排班列表
export async function getPendingApprovals(options = {}) {
  const { skip = 0, limit = 100 } = options;
  return request({
    url: '/api/schedules/pending-approvals',
    method: 'GET',
    params: { skip, limit }
  });
}

// ==================== 统计相关API ====================

// 获取排班统计信息
export async function getScheduleStatistics(options = {}) {
  const { startDate, endDate, employeeId } = options;
  const params = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (employeeId) params.employee_id = employeeId;
  
  return request({
    url: '/api/schedules/statistics',
    method: 'GET',
    params
  });
}

// ==================== 排班审核相关API ====================

// 批准排班
export async function approveSchedule(scheduleId, approvedBy, notes = '') {
  return transitionScheduleStatus(scheduleId, {
    new_status: 'approved',
    approved_by: approvedBy,
    notes
  });
}

// 拒绝排班
export async function rejectSchedule(scheduleId, rejectedBy, rejectionReason) {
  return transitionScheduleStatus(scheduleId, {
    new_status: 'rejected',
    approved_by: rejectedBy,
    rejection_reason: rejectionReason
  });
}

// 取消排班
export async function cancelSchedule(scheduleId, cancelledBy, notes = '') {
  return transitionScheduleStatus(scheduleId, {
    new_status: 'cancelled',
    approved_by: cancelledBy,
    notes
  });
}

// 发布排班
export async function publishSchedule(scheduleId, publishedBy, notes = '') {
  return transitionScheduleStatus(scheduleId, {
    new_status: 'published',
    approved_by: publishedBy,
    notes
  });
}

// 批量审核操作
export async function batchApproveSchedules(scheduleIds, approvedBy, notes = '') {
  return batchStatusOperation({
    schedule_ids: scheduleIds,
    operation: 'approve',
    approved_by: approvedBy,
    notes
  });
}

export async function batchRejectSchedules(scheduleIds, rejectedBy, rejectionReason) {
  return batchStatusOperation({
    schedule_ids: scheduleIds,
    operation: 'reject',
    approved_by: rejectedBy,
    rejection_reason: rejectionReason
  });
}

export async function batchPublishSchedules(scheduleIds, publishedBy, notes = '') {
  return batchStatusOperation({
    schedule_ids: scheduleIds,
    operation: 'publish',
    approved_by: publishedBy,
    notes
  });
}