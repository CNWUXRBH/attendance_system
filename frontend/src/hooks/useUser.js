import { useState, useEffect } from 'react';
import { getMyProfile } from '../services/my';

const useUser = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await getMyProfile();
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user profile', error);
      }
    };

    fetchUser();
  }, []);

  return user;
};

export default useUser;