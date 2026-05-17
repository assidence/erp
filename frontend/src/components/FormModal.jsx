import React, { useEffect } from 'react'
import { Modal, Form, Input, Switch, InputNumber } from 'antd'

export default function FormModal({ open, onClose, onSubmit, title, loading, fields, initialValues, width = 500 }) {
  const [form] = Form.useForm()

  useEffect(() => {
    if (open && initialValues) {
      form.setFieldsValue(initialValues)
    }
  }, [open, initialValues])

  const handleOk = async () => {
    try {
      const values = await form.validateFields()
      onSubmit(values)
    } catch (err) {
      // validation failed
    }
  }

  const handleCancel = () => {
    form.resetFields()
    onClose()
  }

  const renderField = (field) => {
    switch (field.type) {
      case 'input':
        return <Input placeholder={field.placeholder || field.label} />
      case 'textarea':
        return <Input.TextArea rows={field.rows || 3} placeholder={field.placeholder || field.label} />
      case 'switch':
        return <Switch />
      case 'number':
        return <InputNumber style={{ width: '100%' }} placeholder={field.placeholder || field.label} />
      default:
        return <Input placeholder={field.label} />
    }
  }

  return (
    <Modal
      title={title}
      open={open}
      onOk={handleOk}
      onCancel={handleCancel}
      confirmLoading={loading}
      width={width}
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        {fields.map((field, i) => (
          <Form.Item
            key={i}
            name={field.name}
            label={field.label}
            rules={field.rules}
            valuePropName={field.type === 'switch' ? 'checked' : 'value'}
            initialValue={field.initialValue}
            style={field.span ? { display: 'inline-block', width: `calc(${field.span / 24 * 100}% - 8px)` } : undefined}
          >
            {renderField(field)}
          </Form.Item>
        ))}
      </Form>
    </Modal>
  )
}
