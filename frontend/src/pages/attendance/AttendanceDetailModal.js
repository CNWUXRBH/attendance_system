import React from 'react';
import { Modal, Descriptions } from 'antd';

const AttendanceDetailModal = ({ open, onCancel, record }) => {
  return (
    <Modal
        title="考勤详情"
        open={open}
        onCancel={onCancel}
        footer={null}
        width={600}
    >
      <Descriptions bordered column={1}>
        <Descriptions.Item label="日期">{record?.date}</Descriptions.Item>
        <Descriptions.Item label="姓名">{record?.name}</Descriptions.Item>
        <Descriptions.Item label="上班时间">{record?.checkIn}</Descriptions.Item>
        <Descriptions.Item label="下班时间">{record?.checkOut}</Descriptions.Item>
        <Descriptions.Item label="考勤状态">{record?.status}</Descriptions.Item>
        <Descriptions.Item label="工作时长">{record?.workHours}</Descriptions.Item>
        <Descriptions.Item label="加班时长">{record?.overtimeHours}</Descriptions.Item>
        <Descriptions.Item label="备注">{record?.remarks}</Descriptions.Item>
      </Descriptions>
    </Modal>
  );
};

export default AttendanceDetailModal;