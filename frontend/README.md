# 考勤系统前端

基于 React.js 开发的现代化员工考勤管理系统前端应用，提供直观易用的用户界面和丰富的交互功能。

## 项目概述

本项目是一个功能完整的考勤管理系统前端，采用现代化的 React 技术栈，提供响应式设计和优秀的用户体验。系统支持员工管理、考勤记录、排班计划、报表统计等核心功能。

### 技术栈

- **React 18**: 现代化的前端框架
- **Ant Design**: 企业级 UI 设计语言和组件库
- **React Router**: 单页应用路由管理
- **Axios**: HTTP 客户端库
- **Day.js**: 轻量级日期处理库
- **Recharts**: 数据可视化图表库
- **Create React App**: 项目脚手架

### 核心功能

- **用户认证**: 登录/登出，JWT 令牌管理
- **员工管理**: 员工信息的增删改查，批量导入导出
- **考勤记录**: 考勤数据展示，今日异常提醒
- **排班管理**: 排班计划制定，模板管理，班次类型配置
- **报表统计**: 多维度数据分析，图表展示，数据导出
- **响应式设计**: 适配桌面端和移动端

## 快速开始

### 环境要求

- Node.js 16.x+
- npm 8.x+ 或 yarn 1.x+

### 安装和启动

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **环境配置**
   
   创建环境变量文件：
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件：
   ```env
   # API 服务地址
   REACT_APP_API_URL=http://localhost:8000
   
   # 应用标题
   REACT_APP_TITLE=考勤管理系统
   ```

3. **启动开发服务器**
   ```bash
   npm start
   ```
   
   应用将在 http://localhost:3000 启动

4. **构建生产版本**
   ```bash
   npm run build
   ```

## 项目结构

```
frontend/
├── public/                 # 静态资源
│   ├── index.html         # HTML 模板
│   └── manifest.json      # PWA 配置
├── src/                   # 源代码
│   ├── components/        # 通用组件
│   ├── pages/            # 页面组件
│   │   ├── Login.js      # 登录页面
│   │   ├── employee/     # 员工管理
│   │   ├── attendance/   # 考勤记录
│   │   ├── schedule/     # 排班管理
│   │   │   ├── Schedule.js        # 排班主页面
│   │   │   ├── TemplateManagement.js # 模板管理
│   │   │   ├── ScheduleModal.js   # 排班弹窗
│   │   │   └── DayDetailModal.js  # 日程详情
│   │   └── report/       # 报表统计
│   │       └── Report.js # 报表页面
│   ├── layout/           # 布局组件
│   │   └── index.js      # 主布局
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义
│   ├── utils/            # 工具函数
│   │   └── request.js    # HTTP 请求封装
│   ├── App.js            # 根组件
│   └── index.js          # 应用入口
├── nginx.conf            # Nginx 配置
├── Dockerfile            # Docker 构建文件
├── package.json          # 项目依赖
└── README.md             # 项目文档
```

## 页面功能

### 登录页面 (`/login`)
- 用户身份验证
- JWT 令牌获取和存储
- 登录状态管理

### 员工管理 (`/employees`)
- 员工列表展示
- 员工信息的增删改查
- 批量导入导出功能
- 搜索和筛选

### 考勤记录 (`/attendance`)
- 考勤数据列表
- 今日异常考勤提醒
- 考勤记录的查询和管理
- 数据导出功能

### 排班管理 (`/schedule`)
- **排班计划**: 日历视图展示排班安排
- **模板管理**: 排班模板的创建和管理
- **班次类型**: 班次类型的配置和管理
- **批量操作**: 支持批量排班和模板应用

### 报表统计 (`/reports`)
- 多维度数据分析
- 图表可视化展示
- 数据导出功能
- 自定义时间范围查询

## 路由配置

```javascript
const routes = [
  { path: '/login', component: Login },
  { 
    path: '/', 
    component: Layout,
    children: [
      { path: '/employees', component: Employees },
      { path: '/attendance', component: Attendance },
      { path: '/schedule', component: Schedule },
      { path: '/reports', component: Reports }
    ]
  }
];
```

## 组件设计

### 布局组件
- **Header**: 顶部导航栏，用户信息，登出功能
- **Sidebar**: 侧边导航菜单
- **Content**: 主内容区域
- **Footer**: 页脚信息

### 业务组件
- **ScheduleModal**: 排班编辑弹窗
- **DayDetailModal**: 日程详情弹窗
- **TemplateManagement**: 模板管理组件
- **DataTable**: 通用数据表格组件
- **SearchForm**: 搜索表单组件

## API 集成

### HTTP 客户端配置
```javascript
// utils/request.js
import axios from 'axios';

const request = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000
});

// 请求拦截器 - 添加认证头
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### API 接口调用
- 统一的错误处理
- 自动添加认证头
- 响应数据格式化
- 超时处理

## 样式和主题

### Ant Design 定制
- 自定义主题色彩
- 响应式断点配置
- 组件样式覆盖

### CSS 模块化
- 组件级样式隔离
- 全局样式变量
- 响应式设计

## 部署方式

### 开发环境
```bash
npm start
```

### 生产构建
```bash
npm run build
```

### Docker 部署
```bash
# 构建镜像
docker build -t attendance-frontend .

# 运行容器
docker run -p 3000:80 attendance-frontend
```

### Nginx 配置
- 静态文件服务
- API 代理配置
- 单页应用路由支持
- Gzip 压缩

## 开发指南

### 代码规范
- 使用 ESLint 进行代码检查
- 遵循 React Hooks 最佳实践
- 组件命名采用 PascalCase
- 文件命名采用 camelCase

### 组件开发
- 优先使用函数组件和 Hooks
- 合理拆分组件粒度
- 使用 PropTypes 进行类型检查
- 编写清晰的组件文档

### 状态管理
- 使用 React Context 进行全局状态管理
- 本地状态使用 useState
- 副作用使用 useEffect

### 性能优化
- 使用 React.memo 优化组件渲染
- 合理使用 useMemo 和 useCallback
- 代码分割和懒加载
- 图片资源优化

## 可用脚本

### `npm start`
启动开发服务器，支持热重载

### `npm test`
运行测试套件

### `npm run build`
构建生产版本到 `build` 文件夹

### `npm run eject`
弹出 Create React App 配置（不可逆操作）

## 浏览器支持

- Chrome >= 60
- Firefox >= 60
- Safari >= 12
- Edge >= 79

## 常见问题

### 开发环境问题
1. **端口冲突**: 修改 `.env` 文件中的 `PORT` 变量
2. **API 连接失败**: 检查后端服务是否启动，确认 API 地址配置
3. **依赖安装失败**: 清除 node_modules 和 package-lock.json 重新安装

### 构建问题
1. **内存不足**: 增加 Node.js 内存限制
2. **路径问题**: 检查相对路径和绝对路径配置
3. **环境变量**: 确认生产环境变量配置正确

## 贡献指南

欢迎对本项目进行贡献！请遵循以下步骤：

1. Fork 本项目仓库
2. 创建功能分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。
