-- Active: 1720232938342@@127.0.0.1@3306@attendance_system
-- Create database if not exists
CREATE DATABASE IF NOT EXISTS attendance_system;

-- Use the database
USE attendance_system;

-- Create employees table
CREATE TABLE
    IF NOT EXISTS employees (
        employee_id INT AUTO_INCREMENT PRIMARY KEY,
        employee_no VARCHAR(20) NOT NULL UNIQUE,
        name VARCHAR(50) NOT NULL,
        gender VARCHAR(10) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        phone VARCHAR(255),
        position VARCHAR(50),
        hire_date DATE,
        contract_end_date DATE,
        status INT DEFAULT 1,
        is_active BOOLEAN DEFAULT TRUE,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

-- Create attendance_records table
CREATE TABLE
    IF NOT EXISTS attendance_records (
        record_id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT NOT NULL,
        clock_in_time DATETIME,
        clock_out_time DATETIME,
        clock_type VARCHAR(50),
        device_id VARCHAR(255),
        location VARCHAR(255),
        status VARCHAR(50),
        process_status VARCHAR(50) DEFAULT 'unprocessed',
        remarks VARCHAR(500),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
    );

-- Create sync_logs table
CREATE TABLE
    IF NOT EXISTS sync_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sync_type VARCHAR(50) NOT NULL COMMENT '同步类型，如：attendance_records',
        sync_source VARCHAR(100) NOT NULL COMMENT '同步数据源，如：MSSQL_AttendanceDB',
        sync_date VARCHAR(50) NOT NULL COMMENT '同步的数据日期，格式：YYYY-MM-DD 或日期范围',
        employee_no VARCHAR(50) COMMENT '员工工号，如果是按员工同步',
        sync_status VARCHAR(20) NOT NULL DEFAULT 'processing' COMMENT '同步状态：processing, success, failed',
        records_count INT DEFAULT 0 COMMENT '同步的记录数量',
        error_message TEXT COMMENT '错误信息',
        sync_start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '同步开始时间',
        sync_end_time DATETIME COMMENT '同步结束时间',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

-- Create sync_records table
CREATE TABLE
    IF NOT EXISTS sync_records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sync_log_id INT NOT NULL COMMENT '关联的同步日志ID',
        employee_no VARCHAR(50) NOT NULL COMMENT '员工工号',
        attendance_date VARCHAR(10) NOT NULL COMMENT '考勤日期，格式：YYYY-MM-DD',
        clock_in_time DATETIME COMMENT '上班打卡时间',
        clock_out_time DATETIME COMMENT '下班打卡时间',
        external_record_id VARCHAR(100) COMMENT '外部系统的记录ID',
        sync_hash VARCHAR(64) NOT NULL UNIQUE COMMENT '同步数据的哈希值，用于去重',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
