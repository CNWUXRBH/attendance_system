import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, DatePicker, TimePicker, Select, Button, message } from 'antd';
import moment from 'moment';
import { updateAttendanceRecord, addAttendanceRecord } from '../../services/attendance';
import { getEmployees } from '../../services/employee';

const { Option } = Select;

const AttendanceEditModal = ({ visible, onCancel, onSuccess, record, isEdit = true }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    if (visible) {
      fetchEmployees();
      if (isEdit && record) {
        form.setFieldsValue({
          employee_id: record.employee_id,
          date: record.date ? moment(record.date, 'YYYY-MM-DD') : null,
          clock_in_time: record.checkIn ? moment(record.checkIn, 'HH:mm:ss') : null,
          clock_out_time: record.checkOut ? moment(record.checkOut, 'HH:mm:ss') : null,
          clock_type: record.clock_type,
          device_id: record.device_id,
          location: record.location,
          status: record.status
        });
      } else {
        form.resetFields();
      }
    }
  }, [visible, record, isEdit, form]);

  const fetchEmployees = async () => {
    try {
      const result = await getEmployees();
      setEmployees(result || []);
    } catch (error) {
      message.error('获取员工列表失败');
    }
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const submitData = {
        employee_id: values.employee_id,
        date: values.date ? values.date.format('YYYY-MM-DD') : null,
        clock_in_time: values.date && values.clock_in_time ? 
          moment(values.date.format('YYYY-MM-DD') + ' ' + values.clock_in_time.format('HH:mm:ss')).toISOString() : null,
        clock_out_time: values.date && values.clock_out_time ? 
          moment(values.date.format('YYYY-MM-DD') + ' ' + values.clock_out_time.format('HH:mm:ss')).toISOString() : null,
        clock_type: values.clock_type,
        device_id: values.device_id,
        location: values.location,
        status: values.status
      };

      if (isEdit && record) {
        await updateAttendanceRecord(record.record_id, submitData);
        message.success('考勤记录修改成功');
      } else {
        await addAttendanceRecord(submitData);
        message.success('考勤记录添加成功');
      }
      
      onSuccess();
      onCancel();
    } catch (error) {
      message.error(isEdit ? '修改失败' : '添加失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={isEdit ? '修正考勤记录' : '手动补录考勤'}
      visible={visible}
      onCancel={onCancel}
      footer={null}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="employee_id"
          label="员工"
          rules={[{ required: true, message: '请选择员工' }]}
        >
          <Select
            placeholder="选择员工"
            showSearch
            filterOption={(input, option) =>
              option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
            }
          >
            {employees.map(emp => (
              <Option key={emp.employee_id} value={emp.employee_id}>
                {emp.name} ({emp.employee_number})
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="date"
          label="日期"
          rules={[{ required: true, message: '请选择日期' }]}
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="clock_in_time"
          label="上班时间"
        >
          <TimePicker style={{ width: '100%' }} format="HH:mm:ss" />
        </Form.Item>

        <Form.Item
          name="clock_out_time"
          label="下班时间"
        >
          <TimePicker style={{ width: '100%' }} format="HH:mm:ss" />
        </Form.Item>

        <Form.Item
          name="clock_type"
          label="打卡类型"
        >
          <Select placeholder="选择打卡类型">
            <Option value="上班">上班</Option>
            <Option value="下班">下班</Option>
            <Option value="加班">加班</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="device_id"
          label="设备ID"
        >
          <Input placeholder="输入设备ID" />
        </Form.Item>

        <Form.Item
          name="location"
          label="打卡地点"
        >
          <Input placeholder="输入打卡地点" />
        </Form.Item>

        <Form.Item
          name="status"
          label="考勤状态"
          rules={[{ required: true, message: '请选择考勤状态' }]}
        >
          <Select placeholder="选择考勤状态">
            <Option value="正常">正常</Option>
            <Option value="迟到">迟到</Option>
            <Option value="早退">早退</Option>
            <Option value="缺勤">缺勤</Option>
            <Option value="异常">异常</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <div className="flex justify-end space-x-2">
            <Button onClick={onCancel}>取消</Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              {isEdit ? '保存修改' : '添加记录'}
            </Button>
          </div>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default AttendanceEditModal;