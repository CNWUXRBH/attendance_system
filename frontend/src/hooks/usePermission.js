import { useState, useEffect } from 'react';

// 权限常量定义
export const PERMISSIONS = {
  // 员工管理权限
  EMPLOYEE_VIEW: 'employee:view',
  EMPLOYEE_CREATE: 'employee:create',
  EMPLOYEE_EDIT: 'employee:edit',
  EMPLOYEE_DELETE: 'employee:delete',
  EMPLOYEE_IMPORT: 'employee:import',
  EMPLOYEE_EXPORT: 'employee:export',
  
  // 排班管理权限
  SCHEDULE_VIEW: 'schedule:view',
  SCHEDULE_CREATE: 'schedule:create',
  SCHEDULE_EDIT: 'schedule:edit',
  SCHEDULE_DELETE: 'schedule:delete',
  
  // 异常规则权限
  EXCEPTION_VIEW: 'exception:view',
  EXCEPTION_CREATE: 'exception:create',
  EXCEPTION_EDIT: 'exception:edit',
  EXCEPTION_DELETE: 'exception:delete',
  
  // 报表权限
  REPORT_VIEW: 'report:view',
  REPORT_EXPORT: 'report:export',
  REPORT_DOWNLOAD: 'report:download',
  
  // 系统管理权限
  SYSTEM_ADMIN: 'system:admin'
};

// 角色权限映射
const ROLE_PERMISSIONS = {
  admin: Object.values(PERMISSIONS), // 管理员拥有所有权限
  manager: [
    PERMISSIONS.EMPLOYEE_VIEW,
    PERMISSIONS.EMPLOYEE_CREATE,
    PERMISSIONS.EMPLOYEE_EDIT,
    PERMISSIONS.EMPLOYEE_EXPORT,
    PERMISSIONS.SCHEDULE_VIEW,
    PERMISSIONS.SCHEDULE_CREATE,
    PERMISSIONS.SCHEDULE_EDIT,
    PERMISSIONS.SCHEDULE_DELETE,
    PERMISSIONS.EXCEPTION_VIEW,
    PERMISSIONS.EXCEPTION_CREATE,
    PERMISSIONS.EXCEPTION_EDIT,
    PERMISSIONS.EXCEPTION_DELETE,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.REPORT_EXPORT,
    PERMISSIONS.REPORT_DOWNLOAD
  ],
  employee: [
    PERMISSIONS.EMPLOYEE_VIEW,
    PERMISSIONS.SCHEDULE_VIEW,
    PERMISSIONS.EXCEPTION_VIEW,
    PERMISSIONS.REPORT_VIEW
  ]
};

/**
 * 权限管理Hook
 */
export const usePermission = () => {
  const [userPermissions, setUserPermissions] = useState([]);
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);

  // 初始化用户权限
  useEffect(() => {
    const initPermissions = () => {
      try {
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const role = userInfo.role || 'employee';
        const permissions = ROLE_PERMISSIONS[role] || ROLE_PERMISSIONS.employee;
        
        setUserRole(role);
        setUserPermissions(permissions);
      } catch (error) {
        console.error('初始化权限失败:', error);
        setUserRole('employee');
        setUserPermissions(ROLE_PERMISSIONS.employee);
      } finally {
        setLoading(false);
      }
    };

    initPermissions();
  }, []);

  // 检查是否有指定权限
  const hasPermission = (permission) => {
    if (loading) return false;
    return userPermissions.includes(permission);
  };

  // 检查是否有任一权限
  const hasAnyPermission = (permissions) => {
    if (loading) return false;
    return permissions.some(permission => userPermissions.includes(permission));
  };

  // 检查是否有所有权限
  const hasAllPermissions = (permissions) => {
    if (loading) return false;
    return permissions.every(permission => userPermissions.includes(permission));
  };

  // 检查是否是管理员
  const isAdmin = () => {
    return userRole === 'admin';
  };

  // 检查是否是经理
  const isManager = () => {
    return userRole === 'manager';
  };

  // 检查是否是普通员工
  const isEmployee = () => {
    return userRole === 'employee';
  };

  // 获取用户所有权限
  const getAllPermissions = () => {
    return userPermissions;
  };

  // 更新用户权限（当用户信息变更时）
  const updatePermissions = (newUserInfo) => {
    const role = newUserInfo.role || 'employee';
    const permissions = ROLE_PERMISSIONS[role] || ROLE_PERMISSIONS.employee;
    
    setUserRole(role);
    setUserPermissions(permissions);
  };

  return {
    userPermissions,
    userRole,
    loading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin,
    isManager,
    isEmployee,
    getAllPermissions,
    updatePermissions,
    PERMISSIONS
  };
};