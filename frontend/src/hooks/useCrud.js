import { useState, useEffect } from 'react';
import { message, Modal } from 'antd';
import { useLoading } from '../contexts/LoadingContext';

/**
 * 通用CRUD操作Hook
 * @param {Object} config - 配置对象
 * @param {Function} config.fetchData - 获取数据的函数
 * @param {Function} config.addData - 添加数据的函数
 * @param {Function} config.editData - 编辑数据的函数
 * @param {Function} config.deleteData - 删除数据的函数
 * @param {string} config.entityName - 实体名称，用于提示信息
 */
export const useCrud = (config) => {
  const {
    fetchData,
    addData,
    editData,
    deleteData,
    entityName = '数据'
  } = config;

  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(false);
  const { showLoading, hideLoading } = useLoading();

  // 获取数据
  const handleFetch = async (showGlobalLoading = false) => {
    try {
      if (showGlobalLoading) {
        showLoading(`正在加载${entityName}...`);
      } else {
        setLoading(true);
      }
      const result = await fetchData();
      const dataList = Array.isArray(result) ? result : (result.data || result.list || []);
      setData(dataList);
      setFilteredData(dataList);
    } catch (error) {
      message.error(`获取${entityName}失败`);
    } finally {
      if (showGlobalLoading) {
        hideLoading();
      } else {
        setLoading(false);
      }
    }
  };

  // 添加数据
  const handleAdd = async (values) => {
    try {
      showLoading(`正在添加${entityName}...`);
      await addData(values);
      message.success(`添加${entityName}成功`);
      await handleFetch();
      return true;
    } catch (error) {
      message.error(`添加${entityName}失败`);
      return false;
    } finally {
      hideLoading();
    }
  };

  // 编辑数据
  const handleEdit = async (id, values) => {
    try {
      showLoading(`正在更新${entityName}...`);
      await editData(id, values);
      message.success(`更新${entityName}成功`);
      await handleFetch();
      return true;
    } catch (error) {
      message.error(`更新${entityName}失败`);
      return false;
    } finally {
      hideLoading();
    }
  };

  // 删除数据
  const handleDelete = (id, customMessage) => {
    Modal.confirm({
      title: `确定删除该${entityName}吗？`,
      content: customMessage || '删除后将无法恢复',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          showLoading(`正在删除${entityName}...`);
          await deleteData(id);
          message.success(`删除${entityName}成功`);
          await handleFetch();
        } catch (error) {
          message.error(`删除${entityName}失败`);
        } finally {
          hideLoading();
        }
      },
    });
  };

  // 搜索过滤
  const handleSearch = (value, searchFields = ['name']) => {
    if (!value) {
      setFilteredData(data);
    } else {
      const filtered = data.filter(item => 
        searchFields.some(field => 
          item[field]?.toString().toLowerCase().includes(value.toLowerCase())
        )
      );
      setFilteredData(filtered);
    }
  };

  // 初始化时获取数据
  useEffect(() => {
    if (fetchData) {
      handleFetch(true);
    }
  }, []);

  return {
    data,
    filteredData,
    loading,
    handleFetch,
    handleAdd,
    handleEdit,
    handleDelete,
    handleSearch,
    setData,
    setFilteredData
  };
};