import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Badge, Button, Space, message, Popconfirm, Tooltip, Upload } from 'antd';
import { CopyOutlined, DragOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getSchedules, addSchedule, updateSchedule, deleteSchedule, copySchedules, batchCheckConflicts } from '../../services/schedule';
import ScheduleModal from './ScheduleModal';
import EditScheduleModal from './EditScheduleModal';
import DayDetailModal from './DayDetailModal';
import request from '../../utils/request';

// 常量定义，避免重复创建
const SHIFT_TYPES = {
  1: { color: 'success', text: '早班' },
  2: { color: 'warning', text: '中班' },
  3: { color: 'error', text: '晚班' }
};

const SHIFT_TYPE_NAMES = {
  1: '早班',
  2: '中班',
  3: '晚班'
};

const Schedule = () => {
  const navigate = useNavigate();
  const [schedules, setSchedules] = useState({});
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [isDayDetailVisible, setIsDayDetailVisible] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [draggedSchedule, setDraggedSchedule] = useState(null);
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [importing, setImporting] = useState(false);

  const fetchSchedules = useCallback(async (year, month) => {
    try {
      const result = await getSchedules(year, month);
      const schedulesData = result.data || {};
      
      // 为每个日期的排班添加冲突检测
      const enhancedSchedules = {};
      for (const [date, daySchedules] of Object.entries(schedulesData)) {
        if (daySchedules && daySchedules.length > 0) {
          try {
            // 批量检查当日排班的冲突
            const schedulesWithConflicts = await batchCheckConflicts(daySchedules);
            enhancedSchedules[date] = schedulesWithConflicts;
          } catch (error) {
            console.warn(`检查日期 ${date} 的冲突失败:`, error);
            // 如果冲突检测失败，使用原始数据
            enhancedSchedules[date] = daySchedules.map(schedule => ({
              ...schedule,
              conflict_info: { has_conflict: false }
            }));
          }
        } else {
          enhancedSchedules[date] = daySchedules;
        }
      }
      
      setSchedules(enhancedSchedules);
    } catch (error) {
      console.error('获取排班数据失败:', error);
      message.error('获取排班数据失败，请检查网络连接');
    }
  }, []);

  const getListData = useCallback((value) => {
    const dateStr = value.format('YYYY-MM-DD');
    const data = schedules[dateStr] || [];
    return data;
  }, [schedules]);

  const handleCopySchedule = useCallback((schedule) => {
    setDraggedSchedule(schedule);
    message.info('已选择排班，点击目标日期进行复制');
  }, []);

  const handleDeleteSchedule = useCallback(async (id) => {
    try {
      await deleteSchedule(id);
      fetchSchedules(currentYear, currentMonth);
      message.success('排班删除成功');
    } catch (error) {
      message.error('排班删除失败');
    }
  }, [fetchSchedules, currentYear, currentMonth]);

  const showEditModal = useCallback((schedule) => {
    setSelectedSchedule(schedule);
    setIsEditModalVisible(true);
  }, []);

  const dateCellRender = useCallback((value) => {
    const listData = getListData(value);
    const isToday = value.isSame(new Date(), 'day');
    const isWeekend = value.day() === 0 || value.day() === 6;
    
    return (
      <div className={`h-full ${isToday ? 'bg-blue-50' : ''} ${isWeekend ? 'bg-gray-50' : ''}`}>
        <ul className="events space-y-1">
          {listData.length <= 2 ? (
            // 当排班数量较少时，显示详细信息
            listData.map((item) => {
              const shiftInfo = SHIFT_TYPES[item.shift_type_id] || { color: 'default', text: '排班' };
              const hasConflict = item.conflict_info?.has_conflict;
              const badgeColor = hasConflict ? 'error' : shiftInfo.color;
              const displayText = `${item.employee_name || '员工'} - ${shiftInfo.text}${hasConflict ? ' ⚠️' : ''}`;
              
              return (
                <li key={item.id} className="text-xs">
                  <div className="flex items-center justify-between">
                    <Badge 
                      status={badgeColor} 
                      text={displayText}
                      title={hasConflict ? `冲突: ${item.conflict_info?.conflict_details || '存在排班冲突'}` : ''}
                    />
                    <Space size={0}>
                      <Tooltip title="复制排班">
                         <Button 
                           type="link" 
                           size="small" 
                           icon={<CopyOutlined />}
                           onClick={(e) => {
                             e.stopPropagation();
                             handleCopySchedule(item);
                           }}
                           className="p-0 h-auto"
                         />
                       </Tooltip>
                       <Button 
                         type="link" 
                         size="small" 
                         onClick={(e) => {
                           e.stopPropagation();
                           showEditModal(item);
                         }}
                         className="p-0 h-auto"
                       >
                         编辑
                       </Button>
                      <Popconfirm
                        title="确定删除此排班吗？"
                        onConfirm={(e) => {
                          e.stopPropagation();
                          handleDeleteSchedule(item.id);
                        }}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button 
                          type="link" 
                          size="small" 
                          danger 
                          className="p-0 h-auto"
                          onClick={(e) => e.stopPropagation()}
                        >
                          删除
                        </Button>
                      </Popconfirm>
                    </Space>
                  </div>
                </li>
              );
            })
          ) : (
            // 当排班数量较多时，显示简化信息
            <>
              <div className="flex flex-wrap gap-1 mb-2">
                {Object.entries(
                  listData.reduce((acc, item) => {
                    const shiftType = SHIFT_TYPE_NAMES[item.shift_type_id] || '排班';
                    acc[shiftType] = (acc[shiftType] || 0) + 1;
                    return acc;
                  }, {})
                ).map(([shiftType, count]) => (
                  <Badge 
                    key={shiftType}
                    count={count} 
                    size="small"
                    style={{ fontSize: '10px' }}
                  >
                    <span className="text-xs px-1 py-0.5 bg-blue-100 text-blue-800 rounded">
                      {shiftType}
                    </span>
                  </Badge>
                ))}
                {/* 冲突提示 */}
                {(() => {
                  const conflictCount = listData.filter(item => item.conflict_info?.has_conflict).length;
                  return conflictCount > 0 ? (
                    <Badge 
                      count={conflictCount}
                      size="small"
                      style={{ fontSize: '10px', backgroundColor: '#ff4d4f' }}
                    >
                      <span className="text-xs px-1 py-0.5 bg-red-100 text-red-800 rounded">
                        ⚠️冲突
                      </span>
                    </Badge>
                  ) : null;
                })()}
              </div>
              <div className="text-xs text-blue-600 text-center p-1 bg-blue-50 rounded border border-dashed border-blue-300 cursor-pointer">
                共 {listData.length} 个排班，点击查看详情
              </div>
            </>
          )}
        </ul>
      </div>
    );
  }, [getListData, handleCopySchedule, handleDeleteSchedule, showEditModal]);

  const handlePanelChange = useCallback((date) => {
    const year = date.year();
    const month = date.month() + 1;
    setCurrentYear(year);
    setCurrentMonth(month);
    fetchSchedules(year, month);
  }, [fetchSchedules]);

  const fetchEmployees = useCallback(async () => {
    try {
      const response = await request.get('/api/employees');
      setEmployees(response.data || []);
    } catch (error) {
      console.error('获取员工列表失败:', error);
    }
  }, []);

  const handleAddSchedule = useCallback(async (values, type) => {
    try {
      if (type === 'single') {
        await addSchedule(values);
        message.success('✅ 排班新增成功！请查看下方日历中的排班显示');
      } else if (type === 'batch') {
        message.success(`✅ 批量排班成功，共创建 ${values.length} 个排班！请查看日历中的更新`);
      } else if (type === 'template') {
        message.success(`✅ 模板应用成功，共创建 ${values.created_count} 个排班！请查看日历中的更新`);
        if (values.conflicts_count > 0) {
          message.warning(`⚠️ 检测到 ${values.conflicts_count} 个冲突，请检查日历中的排班安排`);
        }
      }
      
      setIsModalVisible(false);
      // 刷新当前视图的排班数据
      fetchSchedules(currentYear, currentMonth);
    } catch (error) {
      message.error('❌ 排班操作失败，请重试');
    }
  }, [fetchSchedules, currentYear, currentMonth]);

  const handleImportSchedule = useCallback(async (file) => {
    if (!file) {
      message.error('请选择要导入的文件');
      return false;
    }

    // 检查文件类型
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedTypes.includes(fileExtension)) {
      message.error('只支持 Excel (.xlsx, .xls) 和 CSV (.csv) 格式的文件');
      return false;
    }

    setImporting(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await request.post('/api/schedules/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data) {
        const { success_count, error_count, errors } = response.data;
        if (success_count > 0) {
          message.success(`✅ 导入成功！共导入 ${success_count} 条排班记录`);
          // 刷新当前视图的排班数据
          fetchSchedules(currentYear, currentMonth);
        }
        if (error_count > 0) {
          message.warning(`⚠️ ${error_count} 条记录导入失败，请检查数据格式`);
          if (errors && errors.length > 0) {
            console.error('导入错误详情:', errors);
          }
        }
      }
    } catch (error) {
      console.error('导入排班失败:', error);
      message.error('❌ 导入失败，请检查文件格式和数据内容');
    } finally {
      setImporting(false);
    }
    return false; // 阻止默认上传行为
  }, [fetchSchedules, currentYear, currentMonth]);

  const handleEditSchedule = useCallback(async (id, values) => {
    try {
      await updateSchedule(id, values);
      setIsEditModalVisible(false);
      fetchSchedules(currentYear, currentMonth);
      message.success('排班编辑成功');
    } catch (error) {
      message.error('排班编辑失败');
    }
  }, [fetchSchedules, currentYear, currentMonth]);



  const handleDateClick = useCallback(async (date) => {
    if (draggedSchedule) {
      try {
        const targetDate = date.format('YYYY-MM-DD');
        await copySchedules({
        sourceYear: new Date(draggedSchedule.date).getFullYear(),
        sourceMonth: new Date(draggedSchedule.date).getMonth() + 1,
        targetYear: new Date(targetDate).getFullYear(),
        targetMonth: new Date(targetDate).getMonth() + 1,
        employeeIds: [draggedSchedule.employee_id]
      });
        message.success('排班复制成功');
        setDraggedSchedule(null);
        
        fetchSchedules(currentYear, currentMonth);
      } catch (error) {
        message.error('排班复制失败');
      }
    } else {
      setSelectedDate(date);
      setIsDayDetailVisible(true);
    }
  }, [draggedSchedule, fetchSchedules, currentYear, currentMonth]);

  // 处理当日详情模态框关闭
  const handleDayDetailClose = useCallback(() => {
    setIsDayDetailVisible(false);
    setSelectedDate(null);
  }, []);

  useEffect(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;
    setCurrentYear(year);
    setCurrentMonth(month);
    fetchSchedules(year, month);
    fetchEmployees();
  }, [fetchSchedules, fetchEmployees]);



  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">排班管理</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-lg font-semibold">排班日历</h2>
            <p className="text-gray-600">📅 新增的排班将自动显示在下方日历中，每个日期格子内显示当日的排班安排</p>
            <p className="text-gray-500 text-sm">💡 提示：点击日期可复制排班，支持批量操作和模板应用</p>
          </div>
          <Space>
            <Button onClick={() => navigate('/schedule/templates')}>模板管理</Button>
            <Button type="primary" onClick={() => setIsModalVisible(true)}>新增排班</Button>
            <Upload
              beforeUpload={handleImportSchedule}
              showUploadList={false}
              accept=".xlsx,.xls,.csv"
            >
              <Button icon={<UploadOutlined />} loading={importing}>
                {importing ? '导入中...' : '导入排班'}
              </Button>
            </Upload>
          </Space>
        </div>
        <Calendar 
          cellRender={dateCellRender} 
          onPanelChange={handlePanelChange}
          onSelect={handleDateClick}
          className={draggedSchedule ? 'cursor-copy' : ''}
        />
        {draggedSchedule && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <div className="flex items-center justify-between">
              <span className="text-blue-700">
                <DragOutlined className="mr-2" />
                已选择排班：{draggedSchedule.employee_name} - {draggedSchedule.shift_type_name}，点击目标日期进行复制
              </span>
              <Button size="small" onClick={() => setDraggedSchedule(null)}>取消</Button>
            </div>
          </div>
        )}
      </div>
      <ScheduleModal
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={handleAddSchedule}
        employees={employees}
      />
    <EditScheduleModal
        open={isEditModalVisible}
        onCancel={() => setIsEditModalVisible(false)}
        onSubmit={handleEditSchedule}
        schedule={selectedSchedule}
        employees={employees}
      />
      
      <DayDetailModal
        open={isDayDetailVisible}
        onCancel={handleDayDetailClose}
        selectedDate={selectedDate}
        schedules={schedules}
        onEdit={showEditModal}
        onDelete={handleDeleteSchedule}
        onCopy={handleCopySchedule}
      />
    </div>
  );
};

export default Schedule;