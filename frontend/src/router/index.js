import { createBrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Employee from '../pages/employee/Employee';
import Attendance from '../pages/attendance/Attendance';
import Report from '../pages/report/Report';
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
        path: '/report',
        element: <Report />,
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