import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';
import { 
  UserIcon, 
  LockClosedIcon, 
  EyeIcon, 
  EyeSlashIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('📝 Login form submitted with:', { username, password: '***' });
    setError('');
    setIsLoading(true);

    try {
      console.log('🔄 Calling login function...');
      await login(username, password);
      console.log('✅ Login successful, navigating to dashboard...');
      navigate('/');
    } catch (err: any) {
      console.error('❌ Login form error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed';
      console.log('📝 Setting error message:', errorMessage);
      setError(errorMessage);
    } finally {
      console.log('🏁 Login process finished, setting loading to false');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 via-white to-primary-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl shadow-medium mb-4">
            <ChartBarIcon className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Index Platform
          </h1>
          <p className="text-secondary-600">
            Professional Index Management
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-strong border-0 p-8">
          <div className="text-center pb-6">
            <h2 className="text-2xl font-semibold text-secondary-900 mb-2">
              Welcome Back
            </h2>
            <p className="text-secondary-600">
              Sign in to access your dashboard
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-secondary-700 mb-2">
                  Username
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400">
                    <UserIcon className="w-5 h-5" />
                  </div>
                  <input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-secondary-300 rounded-xl bg-white text-sm placeholder:text-secondary-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-secondary-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400">
                    <LockClosedIcon className="w-5 h-5" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-12 py-3 border border-secondary-300 rounded-xl bg-white text-sm placeholder:text-secondary-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600 transition-colors"
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="w-5 h-5" />
                    ) : (
                      <EyeIcon className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <div className="rounded-xl bg-danger-50 border border-danger-200 p-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-danger-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-danger-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 px-6 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-soft hover:shadow-medium flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-secondary-600">
              Don't have an account?{' '}
              <button
                type="button"
                className="font-medium text-primary-600 hover:text-primary-700 transition-colors"
                onClick={() => navigate('/register')}
              >
                Create account
              </button>
            </p>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-secondary-50 rounded-xl border border-secondary-200">
          <h3 className="text-sm font-medium text-secondary-900 mb-2">Demo Credentials</h3>
          <div className="text-xs text-secondary-600 space-y-1">
            <p><strong>Username:</strong> admin</p>
            <p><strong>Password:</strong> admin123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
