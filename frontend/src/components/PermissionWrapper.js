import React from 'react';
import { Result } from 'antd';
import { usePermission } from '../hooks/usePermission';

/**
 * 权限包装组件
 * @param {Object} props
 * @param {string|string[]} props.permission - 需要的权限（单个权限或权限数组）
 * @param {string} props.mode - 权限检查模式：'any'（任一权限）或 'all'（所有权限），默认 'any'
 * @param {React.ReactNode} props.children - 子组件
 * @param {React.ReactNode} props.fallback - 无权限时显示的内容
 * @param {boolean} props.hideOnNoPermission - 无权限时是否隐藏（不显示fallback），默认false
 */
const PermissionWrapper = ({ 
  permission, 
  mode = 'any', 
  children, 
  fallback,
  hideOnNoPermission = false 
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, loading } = usePermission();

  // 加载中时显示子组件（避免闪烁）
  if (loading) {
    return children;
  }

  // 权限检查
  let hasAccess = false;
  
  if (typeof permission === 'string') {
    hasAccess = hasPermission(permission);
  } else if (Array.isArray(permission)) {
    hasAccess = mode === 'all' 
      ? hasAllPermissions(permission)
      : hasAnyPermission(permission);
  }

  // 有权限时显示子组件
  if (hasAccess) {
    return children;
  }

  // 无权限时的处理
  if (hideOnNoPermission) {
    return null;
  }

  // 显示自定义fallback或默认无权限提示
  if (fallback) {
    return fallback;
  }

  return (
    <Result
      status="403"
      title="权限不足"
      subTitle="抱歉，您没有访问此功能的权限。"
    />
  );
};

export default PermissionWrapper;