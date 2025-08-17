# 考勤系统后端 API 文档

## 项目概述

本项目是基于 FastAPI 开发的员工考勤管理系统后端服务，采用现代化的异步 Web 框架，提供高性能的 RESTful API 接口。系统支持员工信息管理、考勤记录、智能排班、报表统计、异常管理等核心功能。

### 技术特色
- **FastAPI**: 高性能异步 Web 框架，自动生成 OpenAPI 文档
- **SQLAlchemy**: 强大的 ORM 框架，支持多种数据库
- **Pydantic**: 数据验证和序列化
- **JWT**: 安全的身份认证机制
- **异步处理**: 支持高并发请求处理
- **自动文档**: Swagger UI 和 ReDoc 自动生成

### 核心功能
- **用户认证**: JWT 令牌认证，支持登录/登出
- **员工管理**: 员工信息的 CRUD 操作，支持批量导入导出
- **考勤记录**: 考勤数据的记录、查询和管理
- **排班管理**: 灵活的排班计划和模板管理
- **报表统计**: 多维度的考勤数据分析和报表生成
- **异常管理**: 异常规则设定和异常记录处理
- **数据看板**: 实时的考勤数据展示和统计

## 快速开始

### 环境要求
- Python 3.9+
- MySQL 8.x 或 SQL Server
- pip 包管理器

### 安装和启动

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **环境配置**
   
   复制并配置环境变量文件：
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件，配置以下变量：
   ```env
   # 数据库配置
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/attendance_db
   
   # JWT 配置
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # 邮件配置 (可选)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   
   # SQL Server 配置 (可选)
   MSSQL_SERVER=localhost
   MSSQL_DATABASE=attendance_db
   MSSQL_USERNAME=sa
   MSSQL_PASSWORD=your-password
   ```

3. **数据库初始化**
   ```bash
   # 创建数据库表
   python -c "from database.mysql_database import create_tables; create_tables()"
   ```

4. **启动服务**
   ```bash
   # 开发环境
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # 生产环境
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **访问服务**
   - API 服务: http://localhost:8000
   - API 文档 (Swagger): http://localhost:8000/docs
   - API 文档 (ReDoc): http://localhost:8000/redoc

## API 接口文档

### 认证相关 (Authentication)

| 方法   | 路径                | 描述                     |
| ------ | ------------------- | ------------------------ |
| `POST` | `/auth/login`       | 用户登录，获取访问令牌   |
| `POST` | `/auth/logout`      | 用户登出                 |
| `GET`  | `/auth/me`          | 获取当前用户信息         |

### 员工管理 (Employees)

| 方法     | 路径                        | 描述                                   |
| -------- | --------------------------- | -------------------------------------- |
| `POST`   | `/employees/`               | 创建新员工                             |
| `GET`    | `/employees/`               | 获取员工列表（支持分页和筛选）         |
| `GET`    | `/employees/{employee_id}`  | 获取指定员工的详细信息                 |
| `PUT`    | `/employees/{employee_id}`  | 更新员工信息                           |
| `DELETE` | `/employees/{employee_id}`  | 删除员工                               |
| `POST`   | `/employees/import`         | 从 Excel 文件批量导入员工              |
| `GET`    | `/employees/export`         | 将员工数据导出为 Excel 文件            |

### 考勤记录 (Attendance)

| 方法     | 路径                          | 描述                                     |
| -------- | ----------------------------- | ---------------------------------------- |
| `POST`   | `/attendance/`                | 创建新的考勤记录                         |
| `GET`    | `/attendance/`                | 获取考勤记录列表（支持分页和筛选）       |
| `GET`    | `/attendance/{record_id}`     | 获取指定考勤记录的详细信息               |
| `PUT`    | `/attendance/{record_id}`     | 更新考勤记录                             |
| `DELETE` | `/attendance/{record_id}`     | 删除考勤记录                             |
| `POST`   | `/attendance/import`          | 从 Excel 文件批量导入考勤记录            |
| `GET`    | `/attendance/export`          | 将考勤记录导出为 Excel 文件              |
| `GET`    | `/attendance/today-exceptions`| 获取今日异常考勤记录                     |

### 排班管理 (Schedules)

| 方法     | 路径                        | 描述                                   |
| -------- | --------------------------- | -------------------------------------- |
| `POST`   | `/schedules/`               | 创建新的排班计划                       |
| `GET`    | `/schedules/`               | 获取排班列表（支持分页和筛选）         |
| `GET`    | `/schedules/{schedule_id}`  | 获取指定排班的详细信息                 |
| `PUT`    | `/schedules/{schedule_id}`  | 更新排班信息                           |
| `DELETE` | `/schedules/{schedule_id}`  | 删除排班                               |
| `GET`    | `/schedules/templates`      | 获取排班模板列表                       |
| `POST`   | `/schedules/templates`      | 创建排班模板                           |
| `GET`    | `/schedules/shift-types`    | 获取班次类型列表                       |
| `POST`   | `/schedules/shift-types`    | 创建班次类型                           |

### 报表统计 (Reports)

| 方法   | 路径                        | 描述                                   |
| ------ | --------------------------- | -------------------------------------- |
| `GET`  | `/reports/attendance`       | 获取考勤报表                           |
| `GET`  | `/reports/work-hours`       | 获取工时统计报表                       |
| `GET`  | `/reports/overtime`         | 获取加班统计报表                       |
| `GET`  | `/reports/exception`        | 获取异常统计报表                       |
| `POST` | `/reports/export`           | 导出报表为 Excel 文件                  |

### 异常管理 (Exceptions)

| 方法     | 路径                        | 描述                               |
| -------- | --------------------------- | ---------------------------------- |
| `POST`   | `/exceptions/rules`         | 创建新的考勤异常规则               |
| `GET`    | `/exceptions/rules`         | 获取异常规则列表                   |
| `GET`    | `/exceptions/rules/{rule_id}` | 获取指定规则的详细信息             |
| `PUT`    | `/exceptions/rules/{rule_id}` | 更新异常规则                       |
| `DELETE` | `/exceptions/rules/{rule_id}` | 删除异常规则                       |
| `GET`    | `/exceptions/records`       | 获取异常记录列表                   |
| `POST`   | `/exceptions/process`       | 处理异常记录                       |

### 数据看板 (Dashboard)

| 方法   | 路径                        | 描述                               |
| ------ | --------------------------- | ---------------------------------- |
| `GET`  | `/dashboard/overview`       | 获取数据看板概览信息               |
| `GET`  | `/dashboard/attendance-stats` | 获取考勤统计数据                   |
| `GET`  | `/dashboard/exception-stats`  | 获取异常统计数据                   |
| `POST` | `/dashboard/export`         | 导出看板数据                       |

## 项目结构

```
backend/
├── api/                    # API 路由模块
│   ├── auth.py            # 认证相关 API
│   ├── employees.py       # 员工管理 API
│   ├── attendance.py      # 考勤记录 API
│   ├── schedules.py       # 排班管理 API
│   ├── reports.py         # 报表统计 API
│   ├── exceptions.py      # 异常管理 API
│   └── dashboard.py       # 数据看板 API
├── models/                # 数据模型
│   ├── employee.py        # 员工模型
│   ├── attendance.py      # 考勤模型
│   ├── schedule.py        # 排班模型
│   └── exception.py       # 异常模型
├── schemas/               # Pydantic 数据验证模式
├── database/              # 数据库连接
│   ├── mysql_database.py  # MySQL 数据库连接
│   └── mssql_database.py  # SQL Server 数据库连接
├── config/                # 配置文件
│   └── config.py          # 应用配置
├── utils/                 # 工具函数
├── main.py                # FastAPI 应用入口
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 构建文件
└── README.md              # 项目文档
```

## 数据库支持

### MySQL (主要数据库)
- 使用 PyMySQL 驱动连接
- 支持连接池和事务管理
- 自动创建表结构

### SQL Server (可选)
- 使用 pyodbc 驱动连接
- 支持 Windows 认证和 SQL Server 认证
- 可作为备用数据源

### 数据模型
- **Employee**: 员工信息模型
- **Attendance**: 考勤记录模型
- **Schedule**: 排班计划模型
- **ShiftType**: 班次类型模型
- **ExceptionRule**: 异常规则模型
- **Department**: 部门信息模型

## 技术特性

### 异步处理
- 基于 asyncio 的异步编程
- 支持高并发请求处理
- 异步数据库操作

### 数据验证
- 使用 Pydantic 进行请求/响应数据验证
- 自动类型转换和错误处理
- 详细的错误信息返回

### 安全特性
- JWT 令牌认证
- 密码 bcrypt 加密
- CORS 跨域支持
- SQL 注入防护

### API 文档
- 自动生成 OpenAPI 3.0 规范
- Swagger UI 交互式文档
- ReDoc 文档界面
- 完整的请求/响应示例

## 部署方式

### 开发环境
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境
```bash
# 使用 Gunicorn + Uvicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或直接使用 Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署
```bash
# 构建镜像
docker build -t attendance-backend .

# 运行容器
docker run -p 8000:8000 attendance-backend
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | MySQL 数据库连接字符串 | - |
| `SECRET_KEY` | JWT 密钥 | - |
| `ALGORITHM` | JWT 算法 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 令牌过期时间(分钟) | 30 |
| `SMTP_SERVER` | 邮件服务器地址 | - |
| `SMTP_PORT` | 邮件服务器端口 | 587 |
| `MSSQL_SERVER` | SQL Server 服务器地址 | - |

## 依赖项

主要依赖包括：
- `fastapi`: Web 框架
- `uvicorn`: ASGI 服务器
- `sqlalchemy`: ORM 框架
- `pymysql`: MySQL 驱动
- `pyodbc`: SQL Server 驱动
- `pydantic`: 数据验证
- `python-jose`: JWT 处理
- `bcrypt`: 密码加密
- `python-multipart`: 文件上传支持

完整依赖列表请查看 `requirements.txt` 文件。

## 开发指南

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用类型注解提高代码可读性
- 编写清晰的文档字符串
- 保持函数和类的单一职责

### 测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=.
```

### 调试
- 使用 FastAPI 内置的调试模式
- 查看详细的错误日志
- 利用 Swagger UI 进行 API 测试

## 常见问题

### 数据库连接问题
1. 检查数据库服务是否启动
2. 验证连接字符串格式
3. 确认数据库用户权限

### JWT 认证问题
1. 检查 SECRET_KEY 配置
2. 验证令牌是否过期
3. 确认请求头格式正确

### 性能优化
1. 使用数据库连接池
2. 实现适当的缓存策略
3. 优化数据库查询
4. 使用异步操作

## 贡献指南

欢迎对本项目进行贡献！请遵循以下步骤：

1. Fork 本项目仓库
2. 创建功能分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。