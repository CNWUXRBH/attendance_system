import React, { useEffect } from 'react';
import { Modal, Form, Input, Select, InputNumber } from 'antd';

const { Option } = Select;

const ExceptionRuleModal = ({ visible, onCancel, onOk, rule }) => {
  const [form] = Form.useForm();
  const [ruleType, setRuleType] = React.useState('');

  useEffect(() => {
    if (rule) {
      // 将后端字段映射到前端字段
      const mappedRule = {
        name: rule.rule_name,
        type: rule.rule_type,
        threshold: rule.threshold,
        action: rule.description
      };
      form.setFieldsValue(mappedRule);
      setRuleType(rule.rule_type || '');
    } else {
      form.resetFields();
      setRuleType('');
    }
  }, [rule, form]);

  const handleOk = () => {
    form
      .validateFields()
      .then((values) => {
        // 将前端字段映射到后端字段
        const mappedValues = {
          rule_name: values.name,
          rule_type: values.type,
          threshold: values.threshold,
          description: values.action || values.description
        };
        onOk({ ...rule, ...mappedValues });
        form.resetFields();
      })
      .catch((info) => {
        // 表单验证失败
      });
  };

  return (
    <Modal
      title={rule ? '编辑规则' : '新增规则'}
      visible={visible}
      onOk={handleOk}
      onCancel={onCancel}
      okText="确定"
      cancelText="取消"
    >
      <Form form={form} layout="vertical" name="exception_rule_form">
        <Form.Item
          name="name"
          label="规则名称"
          rules={[{ required: true, message: '请输入规则名称' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="type"
          label="规则类型"
          rules={[{ required: true, message: '请选择规则类型' }]}
        >
          <Select 
            placeholder="请选择规则类型"
            onChange={(value) => setRuleType(value)}
          >
            <Option value="迟到">迟到</Option>
            <Option value="早退">早退</Option>
            <Option value="缺卡">缺卡</Option>
            <Option value="超期">超期</Option>
          </Select>
        </Form.Item>
        <Form.Item
          name="threshold"
          label={ruleType === '超期' ? '时间阈值 (天)' : '时间阈值 (分钟)'}
          rules={[{ required: true, message: '请输入时间阈值' }]}
        >
          <InputNumber 
            style={{ width: '100%' }} 
            min={1}
            placeholder={ruleType === '超期' ? '请输入天数' : '请输入分钟数'}
          />
        </Form.Item>
        <Form.Item
          name="action"
          label="处理方式"
          rules={[{ required: true, message: '请输入处理方式' }]}
        >
          <Input placeholder="发送提醒" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ExceptionRuleModal;