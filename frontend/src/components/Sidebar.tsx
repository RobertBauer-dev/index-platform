import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeIcon,
  ChartBarIcon,
  BuildingLibraryIcon,
  PlusIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Indices', href: '/indices', icon: ChartBarIcon },
  { name: 'Securities', href: '/securities', icon: BuildingLibraryIcon },
  { name: 'Index Builder', href: '/builder', icon: PlusIcon },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="hidden lg:flex lg:flex-shrink-0 h-full">
      <div className="flex flex-col w-72 h-full">
        <div className="flex flex-col flex-1 bg-gradient-to-b from-secondary-900 to-secondary-950 border-r border-secondary-800">
          <div className="flex-1 flex flex-col pt-6 pb-4 overflow-y-auto">
            {/* Logo */}
            <div className="flex items-center flex-shrink-0 px-6 mb-8">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-xl shadow-medium">
                  <ChartBarIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Index Platform</h1>
                  <p className="text-xs text-secondary-400">Dr. Robert Bauer</p>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-2">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                      isActive
                        ? 'bg-primary-600 text-white shadow-medium'
                        : 'text-secondary-300 hover:bg-secondary-800 hover:text-white'
                    }`}
                  >
                    <item.icon
                      className={`mr-3 flex-shrink-0 h-5 w-5 ${
                        isActive ? 'text-white' : 'text-secondary-400 group-hover:text-white'
                      }`}
                      aria-hidden="true"
                    />
                    {item.name}
                    {isActive && (
                      <div className="ml-auto">
                        <div className="w-1.5 h-1.5 rounded-full bg-white"></div>
                      </div>
                    )}
                  </Link>
                );
              })}
            </nav>

            {/* Quick Actions */}
            <div className="px-4 mt-6">
              <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl p-4 shadow-strong">
                <div className="flex items-center mb-3">
                  <SparklesIcon className="h-5 w-5 text-white" />
                  <span className="ml-2 text-sm font-semibold text-white">Quick Create</span>
                </div>
                <p className="text-xs text-primary-100 mb-4">
                  Start building your index in seconds
                </p>
                <button 
                  onClick={() => navigate('/builder')}
                  className="w-full px-3 py-2 text-sm font-medium text-primary-600 bg-white rounded-lg hover:bg-primary-50 transition-colors duration-200"
                >
                  New Index
                </button>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex-shrink-0 border-t border-secondary-800 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-xl bg-primary-600/20 flex items-center justify-center border border-primary-600/30">
                  <span className="text-sm font-bold text-primary-400">IP</span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-white">Index Platform</p>
                <p className="text-xs text-secondary-400">Version 1.0.0</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
