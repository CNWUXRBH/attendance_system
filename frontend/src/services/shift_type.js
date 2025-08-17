import request from '../utils/request';

// ==================== 基础CRUD操作 ====================

// 获取所有班次类型
export async function getShiftTypes(options = {}) {
  const { name, available } = options;
  const params = {};
  if (name) params.name = name;
  if (available !== undefined) params.available = available;
  
  return request({
    url: '/api/shift_types',
    method: 'GET',
    params
  });
}

// 根据ID获取班次类型
export async function getShiftType(id) {
  return request({
    url: `/api/shift_types/${id}`,
    method: 'GET'
  });
}

// 根据名称获取班次类型
export async function getShiftTypeByName(name) {
  return request({
    url: `/api/shift_types/name/${name}`,
    method: 'GET'
  });
}

// 获取所有可用的班次类型
export async function getAvailableShiftTypes() {
  return request({
    url: '/api/shift_types/available',
    method: 'GET'
  });
}

// 创建班次类型
export async function createShiftType(data) {
  return request({
    url: '/api/shift_types',
    method: 'POST',
    data
  });
}

// 更新班次类型
export async function updateShiftType(id, data) {
  return request({
    url: `/api/shift_types/${id}`,
    method: 'PUT',
    data
  });
}

// 删除班次类型
export async function deleteShiftType(id) {
  return request({
    url: `/api/shift_types/${id}`,
    method: 'DELETE'
  });
}

// ==================== 批量操作 ====================

// 批量创建班次类型
export async function batchCreateShiftTypes(shiftTypes) {
  return request({
    url: '/api/shift_types/batch',
    method: 'POST',
    data: shiftTypes
  });
}

// ==================== 冲突检测 ====================

// 验证班次时间冲突
export async function validateShiftTimeConflict(data) {
  return request({
    url: '/api/shift_types/validate-conflict',
    method: 'POST',
    data
  });
}

// ==================== 查询和过滤 ====================

// 根据时间范围获取班次类型
export async function getShiftTypesByTimeRange(startTime, endTime) {
  return request({
    url: '/api/shift_types/time-range',
    method: 'GET',
    params: {
      start_time: startTime,
      end_time: endTime
    }
  });
}

// ==================== 统计信息 ====================

// 获取班次类型统计信息
export async function getShiftTypeStatistics() {
  return request({
    url: '/api/shift_types/statistics',
    method: 'GET'
  });
}

// ==================== 便捷方法 ====================

// 检查班次类型名称是否可用
export async function checkShiftTypeNameAvailable(name, excludeId = null) {
  try {
    await getShiftTypeByName(name);
    // 如果找到了同名的班次类型
    if (excludeId) {
      // 如果是更新操作，检查是否是同一个记录
      const existingShiftType = await getShiftTypeByName(name);
      return existingShiftType.shift_type_id === excludeId;
    }
    return false; // 名称已被使用
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return true; // 名称可用
    }
    throw error; // 其他错误
  }
}

// 获取夜班班次类型（跨天班次）
export async function getNightShiftTypes() {
  const allShiftTypes = await getShiftTypes();
  return allShiftTypes.filter(shiftType => {
    // 判断是否为跨天班次（结束时间小于开始时间）
    return shiftType.end_time < shiftType.start_time;
  });
}

// 获取白班班次类型（非跨天班次）
export async function getDayShiftTypes() {
  const allShiftTypes = await getShiftTypes();
  return allShiftTypes.filter(shiftType => {
    // 判断是否为白班班次（结束时间大于等于开始时间）
    return shiftType.end_time >= shiftType.start_time;
  });
}

// 根据工作时长筛选班次类型
export async function getShiftTypesByDuration(minHours, maxHours) {
  const allShiftTypes = await getShiftTypes();
  return allShiftTypes.filter(shiftType => {
    const duration = calculateShiftDuration(shiftType.start_time, shiftType.end_time);
    return duration >= minHours && duration <= maxHours;
  });
}

// 计算班次时长（小时）
function calculateShiftDuration(startTime, endTime) {
  const start = new Date(`2000-01-01 ${startTime}`);
  let end = new Date(`2000-01-01 ${endTime}`);
  
  // 如果结束时间小于开始时间，说明是跨天班次
  if (end < start) {
    end = new Date(`2000-01-02 ${endTime}`);
  }
  
  return (end - start) / (1000 * 60 * 60); // 转换为小时
}

export { calculateShiftDuration };