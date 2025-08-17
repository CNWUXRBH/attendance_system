import { createBrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Employee from '../pages/employee/Employee';
import Attendance from '../pages/attendance/Attendance';
import Schedule from '../pages/schedule/Schedule';
import TemplateManagement from '../pages/schedule/TemplateManagement';
import Report from '../pages/report/Report';
import Exception from '../pages/exception/Exception';
import Profile from '../pages/my/Profile';
import Settings from '../pages/my/Settings';
import Layout from '../layout';
import Login from '../pages/Login';
import PrivateRoute from '../components/PrivateRoute';

const router = createBrowserRouter([
  {
    path: '/',
    element: <PrivateRoute><Layout /></PrivateRoute>,
    children: [
      {
        path: '/',
        element: <Dashboard />,
      },
      {
        path: '/employee',
        element: <Employee />,
      },
      {
        path: '/attendance',
        element: <Attendance />,
      },
      {
        path: '/schedule',
        element: <Schedule />,
      },
      {
        path: '/schedule/templates',
        element: <TemplateManagement />,
      },
      {
        path: '/report',
        element: <Report />,
      },
      {
        path: '/exception',
        element: <Exception />,
      },

      {
        path: '/my/profile',
        element: <Profile />,
      },
      {
        path: '/my/settings',
        element: <Settings />,
      },
    ],
  },
  {
    path: '/login',
    element: <Login />,
  },
]);

export default router;