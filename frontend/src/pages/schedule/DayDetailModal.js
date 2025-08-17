import { Modal, List, Badge, Button, Popconfirm, Tooltip, Typography } from 'antd';
import { EditOutlined, DeleteOutlined, CopyOutlined, UserOutlined, ClockCircleOutlined } from '@ant-design/icons';
import moment from 'moment';
import './DayDetailModal.css';

const { Text } = Typography;

const DayDetailModal = ({ 
  open, 
  onCancel, 
  selectedDate, 
  schedules, 
  onEdit, 
  onDelete, 
  onCopy 
}) => {
  if (!selectedDate) return null;

  const dateStr = selectedDate.format('YYYY-MM-DD');
  const daySchedules = schedules[dateStr] || [];
  const isToday = selectedDate.isSame(moment(), 'day');
  const isWeekend = selectedDate.day() === 0 || selectedDate.day() === 6;

  const shiftTypes = {
    1: { color: 'success', text: '早班', bgColor: '#f6ffed', borderColor: '#b7eb8f' },
    2: { color: 'warning', text: '中班', bgColor: '#fffbe6', borderColor: '#ffe58f' },
    3: { color: 'error', text: '晚班', bgColor: '#fff2f0', borderColor: '#ffb3b3' }
  };

  const getShiftInfo = (shiftTypeId) => {
    return shiftTypes[shiftTypeId] || { color: 'default', text: '排班', bgColor: '#f5f5f5', borderColor: '#d9d9d9' };
  };

  const groupedSchedules = daySchedules.reduce((acc, schedule) => {
    const shiftType = schedule.shift_type_id;
    if (!acc[shiftType]) {
      acc[shiftType] = [];
    }
    acc[shiftType].push(schedule);
    return acc;
  }, {});

  return (
    <Modal
      title={
        <div className="flex items-center space-x-2">
          <ClockCircleOutlined className="text-blue-500" />
          <span>
            {selectedDate.format('YYYY年MM月DD日')} 
            ({selectedDate.format('dddd')})
            {isToday && <Badge status="processing" text="今天" className="ml-2" />}
            {isWeekend && <Badge color="orange" text="周末" className="ml-2" />}
          </span>
        </div>
      }
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="close" onClick={onCancel}>
          关闭
        </Button>
      ]}
      width={800}
      className="day-detail-modal"
    >
      <div className="space-y-4">
        {/* 统计信息 */}
        <div className="stats-card">
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">{daySchedules.length}</div>
              <div className="stat-label">总排班数</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">
                {new Set(daySchedules.map(s => s.employee_id)).size}
              </div>
              <div className="stat-label">参与员工</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">
                {Object.keys(groupedSchedules).length}
              </div>
              <div className="stat-label">班次类型</div>
            </div>
          </div>
        </div>

        {/* 排班详情 */}
        {daySchedules.length === 0 ? (
          <div className="empty-state">
            <UserOutlined />
            <div>该日期暂无排班安排</div>
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(groupedSchedules).map(([shiftTypeId, scheduleList]) => {
              const shiftInfo = getShiftInfo(parseInt(shiftTypeId));
              return (
                <div key={shiftTypeId} className="shift-group">
                  <div 
                    className="shift-header"
                    style={{ 
                      backgroundColor: shiftInfo.bgColor, 
                      borderBottom: `1px solid ${shiftInfo.borderColor}` 
                    }}
                  >
                    <Badge status={shiftInfo.color} />
                    <span>{shiftInfo.text}</span>
                    <span style={{ marginLeft: '8px', fontSize: '14px', opacity: 0.8 }}>({scheduleList.length}人)</span>
                  </div>
                  <List
                    dataSource={scheduleList}
                    renderItem={(item) => (
                      <List.Item
                        className="px-4"
                        actions={[
                          <Tooltip title="复制排班" key="copy">
                            <Button 
                              type="text" 
                              size="small" 
                              icon={<CopyOutlined />}
                              onClick={() => onCopy(item)}
                            />
                          </Tooltip>,
                          <Tooltip title="编辑排班" key="edit">
                            <Button 
                              type="text" 
                              size="small" 
                              icon={<EditOutlined />}
                              onClick={() => onEdit(item)}
                            />
                          </Tooltip>,
                          <Popconfirm
                            key="delete"
                            title="确定删除此排班吗？"
                            onConfirm={() => onDelete(item.id)}
                            okText="确定"
                            cancelText="取消"
                          >
                            <Tooltip title="删除排班">
                              <Button 
                                type="text" 
                                size="small" 
                                danger
                                icon={<DeleteOutlined />}
                              />
                            </Tooltip>
                          </Popconfirm>
                        ]}
                      >
                        <List.Item.Meta
                          avatar={
                            <div className="employee-avatar" style={{ backgroundColor: '#e6f7ff', color: '#1890ff' }}>
                              <UserOutlined />
                            </div>
                          }
                          title={
                            <div className="flex items-center space-x-2">
                              <Text strong>{item.employee_name || '员工'}</Text>
                              <Badge 
                                status={item.status === 1 ? 'success' : 'default'} 
                                text={item.status === 1 ? '已安排' : '待确认'} 
                              />
                            </div>
                          }
                          description={
                            <div className="text-sm text-gray-600">
                              <div>员工ID: {item.employee_id}</div>
                              <div>排班时间: {item.start_date} 至 {item.end_date}</div>
                            </div>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Modal>
  );
};

export default DayDetailModal;