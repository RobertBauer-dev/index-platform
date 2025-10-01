import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useNavigate } from 'react-router-dom';
import { BellIcon, MagnifyingGlassIcon, Cog6ToothIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext.tsx';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="sticky top-0 z-40 bg-white border-b border-secondary-200 shadow-sm">
      <div className="flex h-16 items-center gap-x-6 px-6 lg:px-8">
        <div className="flex flex-1 gap-x-6">
          {/* Search */}
          <div className="flex flex-1 max-w-lg">
            <div className="relative w-full">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <MagnifyingGlassIcon className="h-5 w-5 text-secondary-400" />
              </div>
              <input
                type="search"
                placeholder="Search indices, securities..."
                className="block w-full rounded-xl border border-secondary-300 bg-white py-2 pl-10 pr-3 text-sm placeholder:text-secondary-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-x-4">
          {/* Notifications */}
          <button
            type="button"
            className="relative p-2 text-secondary-400 hover:text-secondary-600 hover:bg-secondary-50 rounded-xl transition-all duration-200"
          >
            <span className="sr-only">View notifications</span>
            <BellIcon className="h-6 w-6" />
            {/* Notification Badge */}
            <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-danger-500 ring-2 ring-white"></span>
          </button>

          {/* Separator */}
          <div className="hidden lg:block h-6 w-px bg-secondary-200" />

          {/* Profile dropdown */}
          <Menu as="div" className="relative">
            <Menu.Button className="flex items-center gap-x-3 hover:bg-secondary-50 rounded-xl px-3 py-2 transition-all duration-200">
              <div className="flex items-center gap-x-3">
                <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-soft">
                  <span className="text-sm font-semibold text-white">
                    {user?.username?.substring(0, 2).toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-medium text-secondary-900">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-xs text-secondary-600">
                    {user?.email || 'Admin'}
                  </p>
                </div>
              </div>
            </Menu.Button>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-xl bg-white shadow-strong ring-1 ring-secondary-900/5 focus:outline-none overflow-hidden">
                <div className="p-2">
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        className={`${
                          active ? 'bg-secondary-50' : ''
                        } group flex w-full items-center rounded-lg px-3 py-2 text-sm text-secondary-900 transition-colors duration-150`}
                        onClick={() => navigate('/profile')}
                      >
                        <Cog6ToothIcon className="mr-3 h-5 w-5 text-secondary-400 group-hover:text-secondary-600" />
                        Account Settings
                      </button>
                    )}
                  </Menu.Item>
                  <div className="my-1 h-px bg-secondary-200" />
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        className={`${
                          active ? 'bg-danger-50' : ''
                        } group flex w-full items-center rounded-lg px-3 py-2 text-sm text-danger-700 transition-colors duration-150`}
                        onClick={handleLogout}
                      >
                        <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5 text-danger-400 group-hover:text-danger-600" />
                        Sign Out
                      </button>
                    )}
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </div>
  );
};

export default Header;
