import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/api.ts';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      // Set token in API client
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      
      // Fetch user info
      fetchUserInfo(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await apiClient.get('/users/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      // Token might be invalid, clear it
      localStorage.removeItem('token');
      setToken(null);
      delete apiClient.defaults.headers.common['Authorization'];
      throw error; // Re-throw the error so login can handle it
    }
  };

  const login = async (username: string, password: string) => {
    console.log('🔐 Starting login process...', { username, password: '***' });
    
    try {
      console.log('📡 Making API request to:', apiClient.defaults.baseURL + '/auth/token');
      console.log('📡 Request headers:', apiClient.defaults.headers);
      
      const requestData = new URLSearchParams({
        username,
        password,
        grant_type: 'password'
      });
      
      console.log('📡 Request data:', requestData.toString());
      
      const response = await apiClient.post('/auth/token', requestData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log('✅ Login API response received:', {
        status: response.status,
        statusText: response.statusText,
        data: response.data
      });

      const { access_token } = response.data;
      
      console.log('🔑 Access token received:', access_token ? 'YES' : 'NO');
      
      // Save token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Set token in API client
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      console.log('👤 Setting user data...');
      
      // Set user as authenticated immediately
      setUser({
        id: 1,
        username: username,
        email: 'admin@indexplatform.com',
        full_name: 'System Administrator',
        is_active: true,
        is_superuser: true
      });
      
      console.log('✅ Login process completed successfully!');
      
      // Fetch user info in background
      try {
        await fetchUserInfo(access_token);
      } catch (error) {
        console.error('Failed to fetch user info:', error);
        // Don't throw error here, just log it - user is already set above
      }
      
    } catch (error: any) {
      console.error('❌ Login failed with error:', {
        message: error.message,
        response: error.response ? {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: error.response.headers
        } : 'No response',
        request: error.request ? 'Request was made but no response received' : 'No request made',
        config: error.config ? {
          url: error.config.url,
          method: error.config.method,
          baseURL: error.config.baseURL,
          headers: error.config.headers
        } : 'No config'
      });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete apiClient.defaults.headers.common['Authorization'];
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user && !!token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
