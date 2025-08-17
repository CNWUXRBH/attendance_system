import React, { createContext, useContext, useState } from 'react';
import { Spin } from 'antd';

const LoadingContext = createContext();

export const useLoading = () => {
  const context = useContext(LoadingContext);
  if (!context) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
};

export const LoadingProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('加载中...');

  const showLoading = (text = '加载中...') => {
    setLoadingText(text);
    setLoading(true);
  };

  const hideLoading = () => {
    setLoading(false);
  };

  const value = {
    loading,
    showLoading,
    hideLoading,
    loadingText
  };

  return (
    <LoadingContext.Provider value={value}>
      <Spin spinning={loading} tip={loadingText} size="large">
        {children}
      </Spin>
    </LoadingContext.Provider>
  );
};