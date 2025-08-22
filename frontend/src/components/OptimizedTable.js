import React, { memo, useMemo, useCallback, useState } from 'react';
import { Table, Input, Select, Button, Space, Tag } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;

// 使用memo优化组件渲染
const OptimizedTable = memo(({ 
  dataSource, 
  columns, 
  loading, 
  pagination, 
  onTableChange,
  onSearch,
  onRefresh,
  searchConfig = {},
  extraActions = null
}) => {
  const [searchText, setSearchText] = useState('');
  const [searchColumn, setSearchColumn] = useState('all');

  // 使用useMemo优化搜索逻辑
  const filteredData = useMemo(() => {
    if (!searchText || searchColumn === 'all') {
      return dataSource;
    }

    return dataSource.filter(item => {
      const value = item[searchColumn];
      if (typeof value === 'string') {
        return value.toLowerCase().includes(searchText.toLowerCase());
      }
      if (typeof value === 'number') {
        return value.toString().includes(searchText);
      }
      return false;
    });
  }, [dataSource, searchText, searchColumn]);

  // 使用useCallback优化事件处理函数
  const handleSearch = useCallback((value) => {
    setSearchText(value);
    if (onSearch) {
      onSearch(value, searchColumn);
    }
  }, [onSearch, searchColumn]);

  const handleColumnChange = useCallback((value) => {
    setSearchColumn(value);
    setSearchText('');
  }, []);

  const handleRefresh = useCallback(() => {
    if (onRefresh) {
      onRefresh();
    }
  }, [onRefresh]);

  // 使用useMemo优化表格列配置
  const tableColumns = useMemo(() => {
    return columns.map(col => ({
      ...col,
      // 添加搜索高亮功能
      render: (text, record, index) => {
        if (col.render) {
          return col.render(text, record, index);
        }
        
        if (searchText && searchColumn === col.dataIndex && typeof text === 'string') {
          const parts = text.split(new RegExp(`(${searchText})`, 'gi'));
          return (
            <span>
              {parts.map((part, i) => 
                part.toLowerCase() === searchText.toLowerCase() ? 
                  <mark key={i} style={{ backgroundColor: '#ffd54f' }}>{part}</mark> : 
                  part
              )}
            </span>
          );
        }
        
        return text;
      }
    }));
  }, [columns, searchText, searchColumn]);

  // 使用useMemo优化分页配置
  const tablePagination = useMemo(() => ({
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
    ...pagination
  }), [pagination]);

  return (
    <div className="optimized-table">
      {/* 搜索和操作区域 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Search
            placeholder="搜索..."
            allowClear
            style={{ width: 200 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onSearch={handleSearch}
            prefix={<SearchOutlined />}
          />
          {searchConfig.columns && (
            <Select
              value={searchColumn}
              onChange={handleColumnChange}
              style={{ width: 120 }}
            >
              <Option value="all">全部字段</Option>
              {searchConfig.columns.map(col => (
                <Option key={col.key} value={col.key}>
                  {col.label}
                </Option>
              ))}
            </Select>
          )}
        </Space>
        
        <Space>
          {extraActions}
          <Button 
            icon={<ReloadOutlined />} 
            onClick={handleRefresh}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* 表格 */}
      <Table
        dataSource={filteredData}
        columns={tableColumns}
        loading={loading}
        pagination={tablePagination}
        onChange={onTableChange}
        rowKey={(record) => record.id || record.key || Math.random()}
        scroll={{ x: 'max-content' }}
        size="middle"
        bordered
      />
    </div>
  );
});

// 设置组件显示名称，便于调试
OptimizedTable.displayName = 'OptimizedTable';

export default OptimizedTable;
