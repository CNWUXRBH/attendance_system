import { useState, useEffect } from 'react';
import { Card, Avatar, Descriptions, Button, Spin, message } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { getProfile } from '../../services/my';
import EditProfileModal from '../../components/EditProfileModal';

const Profile = () => {
  const [profile, setProfile] = useState({});
  const [loading, setLoading] = useState(true);
  const [editModalVisible, setEditModalVisible] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await getProfile();
      setProfile(result.data || result);
    } catch (error) {
      console.error('获取个人信息失败:', error);
      message.error('获取个人信息失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSuccess = () => {
    setEditModalVisible(false);
    fetchData(); // 重新获取个人信息
  };

  const handleEditCancel = () => {
    setEditModalVisible(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="p-6 bg-gray-100 min-h-screen flex justify-center items-center">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">个人信息</h1>
      <Card>
        <div className="flex items-center mb-6">
          <Avatar size={64} icon={<UserOutlined />} />
          <div className="ml-4">
            <h2 className="text-xl font-bold">{profile.name}</h2>
            <p className="text-gray-500">{profile.department} - {profile.position}</p>
          </div>
        </div>
        <Descriptions title="基本信息" bordered>
          <Descriptions.Item label="员工ID">{profile.id}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{profile.email}</Descriptions.Item>
          <Descriptions.Item label="电话">{profile.phone}</Descriptions.Item>
          <Descriptions.Item label="入职日期">{profile.hireDate}</Descriptions.Item>
        </Descriptions>
        <div className="mt-6 text-right">
          <Button type="primary" onClick={() => setEditModalVisible(true)}>编辑信息</Button>
        </div>
      </Card>
      
      <EditProfileModal
        open={editModalVisible}
        onCancel={handleEditCancel}
        onSuccess={handleEditSuccess}
        initialData={profile}
      />
    </div>
  );
};

export default Profile;