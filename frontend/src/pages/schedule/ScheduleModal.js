import { useState, useEffect } from 'react';
import { Modal, Form, DatePicker, Select, message, Tabs, Checkbox, Space } from 'antd';
import { getShiftTemplates, applyShiftTemplate, batchCreateSchedules, checkScheduleConflicts } from '../../services/schedule';

const { Option } = Select;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

const ScheduleModal = ({ open, onCancel, onOk, employees = [] }) => {
  const [form] = Form.useForm();
  const [batchForm] = Form.useForm();
  const [templateForm] = Form.useForm();
  const [activeTab, setActiveTab] = useState('single');
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [indeterminate, setIndeterminate] = useState(false);
  const [checkAll, setCheckAll] = useState(false);

  useEffect(() => {
    if (open) {
      loadTemplates();
    }
  }, [open]);

  const loadTemplates = async () => {
    try {
      const response = await getShiftTemplates();
      setTemplates(response.data || []);
    } catch (error) {
      message.error('加载排班模板失败');
    }
  };

  const handleSingleSchedule = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      // 检查冲突
      const conflictResponse = await checkScheduleConflicts(
        values.employee_id,
        values.start_date.format('YYYY-MM-DD HH:mm:ss'),
        values.end_date.format('YYYY-MM-DD HH:mm:ss')
      );
      
      if (conflictResponse.data) {
        message.warning('⚠️ 检测到排班冲突，请检查时间安排');
        setLoading(false);
        return;
      }
      
      message.success('✅ 排班创建成功！请查看日历中的更新');
      form.resetFields();
      onOk(values, 'single');
    } catch (error) {
      // 表单验证失败
      message.error('❌ 表单验证失败，请检查输入信息');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchSchedule = async () => {
    try {
      const values = await batchForm.validateFields();
      setLoading(true);
      
      const schedules = selectedEmployees.map(employeeId => ({
        employee_id: employeeId,
        shift_type_id: values.shift_type_id,
        start_date: values.start_date.format('YYYY-MM-DD HH:mm:ss'),
        end_date: values.end_date.format('YYYY-MM-DD HH:mm:ss'),
        status: 'scheduled'
      }));
      
      const response = await batchCreateSchedules(schedules);
      message.success(`✅ 批量排班成功！共创建 ${response.data.length} 个排班`);
      
      batchForm.resetFields();
      setSelectedEmployees([]);
      onOk(response.data, 'batch');
    } catch (error) {
      message.error('❌ 批量创建排班失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateApply = async () => {
    try {
      const values = await templateForm.validateFields();
      setLoading(true);
      
      const response = await applyShiftTemplate(
        values.template_id,
        selectedEmployees,
        values.date_range[0].format('YYYY-MM-DD'),
        values.date_range[1].format('YYYY-MM-DD')
      );
      
      if (response.data.conflicts_count > 0) {
        message.warning(`⚠️ 模板应用完成，但检测到 ${response.data.conflicts_count} 个冲突，请检查排班安排`);
      } else {
        message.success(`✅ 模板应用成功！共创建 ${response.data.created_count} 个排班`);
      }
      
      templateForm.resetFields();
      setSelectedEmployees([]);
      onOk(response.data, 'template');
    } catch (error) {
      message.error('❌ 应用模板失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleOk = () => {
    switch (activeTab) {
      case 'single':
        handleSingleSchedule();
        break;
      case 'batch':
        handleBatchSchedule();
        break;
      case 'template':
        handleTemplateApply();
        break;
      default:
        break;
    }
  };

  const handleCancel = () => {
    form.resetFields();
    batchForm.resetFields();
    templateForm.resetFields();
    setSelectedEmployees([]);
    setIndeterminate(false);
    setCheckAll(false);
    setActiveTab('single');
    onCancel();
  };

  const onCheckAllChange = (e) => {
    const allEmployeeIds = employees.map(emp => emp.employee_id);
    setSelectedEmployees(e.target.checked ? allEmployeeIds : []);
    setIndeterminate(false);
    setCheckAll(e.target.checked);
  };

  const onEmployeeChange = (checkedList) => {
    setSelectedEmployees(checkedList);
    setIndeterminate(!!checkedList.length && checkedList.length < employees.length);
    setCheckAll(checkedList.length === employees.length);
  };

  return (
    <Modal
      title="排班管理"
      open={open}
      onOk={handleOk}
      onCancel={handleCancel}
      okText="提交"
      cancelText="取消"
      loading={loading}
      width={800}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="单个排班" key="single">
          <Form form={form} layout="vertical" name="single_schedule_form">
            <Form.Item
              name="employee_id"
              label="员工"
              rules={[{ required: true, message: '请选择员工' }]}
            >
              <Select placeholder="请选择员工">
                {employees.map(emp => (
                  <Option key={emp.employee_id} value={emp.employee_id}>{emp.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="shift_type_id"
              label="班次类型"
              rules={[{ required: true, message: '请选择班次类型' }]}
            >
              <Select placeholder="请选择班次类型">
                <Option value={1}>早班</Option>
                <Option value={2}>中班</Option>
                <Option value={3}>晚班</Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="start_date"
              label="开始时间"
              rules={[{ required: true, message: '请选择开始时间' }]}
            >
              <DatePicker showTime format="YYYY-MM-DD HH:mm" />
            </Form.Item>
            <Form.Item
              name="end_date"
              label="结束时间"
              rules={[{ required: true, message: '请选择结束时间' }]}
            >
              <DatePicker showTime format="YYYY-MM-DD HH:mm" />
            </Form.Item>
          </Form>
        </TabPane>
        
        <TabPane tab="批量排班" key="batch">
          <Form form={batchForm} layout="vertical" name="batch_schedule_form">
            <Form.Item label="选择员工">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Checkbox
                  indeterminate={indeterminate}
                  onChange={onCheckAllChange}
                  checked={checkAll}
                >
                  全选
                </Checkbox>
                <Checkbox.Group
                  value={selectedEmployees}
                  onChange={onEmployeeChange}
                  style={{ width: '100%' }}
                >
                  <Space wrap>
                    {employees.map(emp => (
                      <Checkbox key={emp.employee_id} value={emp.employee_id}>{emp.name}</Checkbox>
                    ))}
                  </Space>
                </Checkbox.Group>
              </Space>
            </Form.Item>
            <Form.Item
              name="shift_type_id"
              label="班次类型"
              rules={[{ required: true, message: '请选择班次类型' }]}
            >
              <Select placeholder="请选择班次类型">
                <Option value={1}>早班</Option>
                <Option value={2}>中班</Option>
                <Option value={3}>晚班</Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="start_date"
              label="开始时间"
              rules={[{ required: true, message: '请选择开始时间' }]}
            >
              <DatePicker showTime format="YYYY-MM-DD HH:mm" />
            </Form.Item>
            <Form.Item
              name="end_date"
              label="结束时间"
              rules={[{ required: true, message: '请选择结束时间' }]}
            >
              <DatePicker showTime format="YYYY-MM-DD HH:mm" />
            </Form.Item>
          </Form>
        </TabPane>
        
        <TabPane tab="模板应用" key="template">
          <Form form={templateForm} layout="vertical" name="template_schedule_form">
            <Form.Item label="选择员工">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Checkbox
                  indeterminate={indeterminate}
                  onChange={onCheckAllChange}
                  checked={checkAll}
                >
                  全选
                </Checkbox>
                <Checkbox.Group
                  value={selectedEmployees}
                  onChange={onEmployeeChange}
                  style={{ width: '100%' }}
                >
                  <Space wrap>
                    {employees.map(emp => (
                      <Checkbox key={emp.employee_id} value={emp.employee_id}>{emp.name}</Checkbox>
                    ))}
                  </Space>
                </Checkbox.Group>
              </Space>
            </Form.Item>
            <Form.Item
              name="template_id"
              label="排班模板"
              rules={[{ required: true, message: '请选择排班模板' }]}
            >
              <Select placeholder="请选择排班模板">
                {templates.map(template => (
                  <Option key={template.id} value={template.id}>
                    {template.name} ({template.start_time} - {template.end_time})
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="date_range"
              label="日期范围"
              rules={[{ required: true, message: '请选择日期范围' }]}
            >
              <RangePicker />
            </Form.Item>
          </Form>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default ScheduleModal;