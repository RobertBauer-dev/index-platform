import React, { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';
import Sidebar from './Sidebar.tsx';
import Header from './Header.tsx';

const Layout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    console.log('Layout: isAuthenticated =', isAuthenticated, 'isLoading =', isLoading);
    if (!isLoading && !isAuthenticated) {
      console.log('Layout: Redirecting to /login');
      navigate('/login', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading) {
    console.log('Layout: Showing loading spinner');
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mb-4"></div>
          <p className="text-secondary-600 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('Layout: Not authenticated, showing nothing while redirecting');
    return null;
  }

  console.log('Layout: Rendering main layout');
  return (
    <div className="flex h-screen overflow-hidden bg-secondary-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-6 py-8 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
