import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api.ts';
import { ChartBarIcon, BuildingLibraryIcon, ArrowTrendingUpIcon, CurrencyDollarIcon, ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  // Fetch dashboard data
  const { data: indices } = useQuery({
    queryKey: ['indices'],
    queryFn: () => api.indices.list({ limit: 10, is_active: true }),
  });

  const { data: securities } = useQuery({
    queryKey: ['securities'],
    queryFn: () => api.securities.list({ limit: 10, is_active: true }),
  });

  const stats = [
    {
      name: 'Total Indices',
      value: indices?.data?.length || 0,
      change: '+12.5%',
      trend: 'up',
      icon: ChartBarIcon,
      bgColor: 'bg-primary-50',
      iconColor: 'text-primary-600',
      borderColor: 'border-primary-100',
    },
    {
      name: 'Total Securities',
      value: securities?.data?.length || 0,
      change: '+8.2%',
      trend: 'up',
      icon: BuildingLibraryIcon,
      bgColor: 'bg-success-50',
      iconColor: 'text-success-600',
      borderColor: 'border-success-100',
    },
    {
      name: 'Active Indices',
      value: indices?.data?.filter((i: any) => i.is_active)?.length || 0,
      change: '+4.3%',
      trend: 'up',
      icon: ArrowTrendingUpIcon,
      bgColor: 'bg-chart-purple/10',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-100',
    },
    {
      name: 'Total Market Cap',
      value: '$2.4T',
      change: '-2.1%',
      trend: 'down',
      icon: CurrencyDollarIcon,
      bgColor: 'bg-warning-50',
      iconColor: 'text-warning-600',
      borderColor: 'border-warning-100',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
          <p className="mt-2 text-sm text-secondary-600">
            Welcome back! Here's an overview of your index platform performance
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => {
              // TODO: Implement export functionality
              alert('Export functionality will be implemented soon!');
            }}
            className="px-4 py-2 text-sm font-medium text-secondary-700 bg-white border border-secondary-300 rounded-xl hover:bg-secondary-50 transition-all duration-200"
          >
            Export Data
          </button>
          <button 
            onClick={() => navigate('/builder')}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-soft"
          >
            Create Index
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <div 
            key={stat.name} 
            className="bg-white rounded-2xl p-6 border border-secondary-100 shadow-soft hover:shadow-medium transition-all duration-200 animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.bgColor} ${stat.borderColor} border rounded-xl p-3`}>
                <stat.icon className={`h-6 w-6 ${stat.iconColor}`} />
              </div>
              <div className={`flex items-center space-x-1 text-sm font-medium ${
                stat.trend === 'up' ? 'text-success-600' : 'text-danger-600'
              }`}>
                {stat.trend === 'up' ? (
                  <ArrowUpIcon className="h-4 w-4" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4" />
                )}
                <span>{stat.change}</span>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-secondary-600 mb-1">
                {stat.name}
              </p>
              <p className="text-2xl font-bold text-secondary-900">
                {stat.value}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Indices */}
      <div className="bg-white rounded-2xl border border-secondary-100 shadow-soft overflow-hidden">
        <div className="px-6 py-5 border-b border-secondary-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-secondary-900">Recent Indices</h3>
              <p className="mt-1 text-sm text-secondary-600">Your most recently created indices</p>
            </div>
            <button 
              onClick={() => navigate('/indices')}
              className="text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
            >
              View All →
            </button>
          </div>
        </div>
        <div>
          {indices?.data?.length ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-secondary-200">
                <thead className="bg-secondary-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Weighting Method
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-secondary-100">
                  {indices.data.slice(0, 5).map((index: any) => (
                    <tr key={index.id} className="hover:bg-secondary-50 transition-colors duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-secondary-900">{index.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-secondary-600 capitalize">
                          {index.weighting_method.replace('_', ' ')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                          index.is_active 
                            ? 'bg-success-50 text-success-700 border border-success-200' 
                            : 'bg-danger-50 text-danger-700 border border-danger-200'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                            index.is_active ? 'bg-success-500' : 'bg-danger-500'
                          }`}></span>
                          {index.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-600">
                        {new Date(index.created_at).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric', 
                          year: 'numeric' 
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary-100 rounded-2xl mb-4">
                <ChartBarIcon className="h-8 w-8 text-secondary-400" />
              </div>
              <h3 className="text-base font-medium text-secondary-900 mb-1">No indices yet</h3>
              <p className="text-sm text-secondary-600 mb-6">
                Get started by creating your first index.
              </p>
              <button 
                onClick={() => navigate('/builder')}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-soft"
              >
                Create Index
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Recent Securities */}
      <div className="bg-white rounded-2xl border border-secondary-100 shadow-soft overflow-hidden">
        <div className="px-6 py-5 border-b border-secondary-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-secondary-900">Recent Securities</h3>
              <p className="mt-1 text-sm text-secondary-600">Latest securities in your portfolio</p>
            </div>
            <button 
              onClick={() => navigate('/securities')}
              className="text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
            >
              View All →
            </button>
          </div>
        </div>
        <div>
          {securities?.data?.length ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-secondary-200">
                <thead className="bg-secondary-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Sector
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-secondary-700 uppercase tracking-wider">
                      Country
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-secondary-100">
                  {securities.data.slice(0, 5).map((security: any) => (
                    <tr key={security.id} className="hover:bg-secondary-50 transition-colors duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-8 w-8 bg-primary-100 rounded-lg flex items-center justify-center">
                            <span className="text-xs font-bold text-primary-700">{security.symbol.substring(0, 2)}</span>
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-secondary-900">{security.symbol}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-secondary-900">{security.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2.5 py-1 text-xs font-medium text-secondary-700 bg-secondary-100 rounded-lg">
                          {security.sector || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-600">
                        {security.country || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary-100 rounded-2xl mb-4">
                <BuildingLibraryIcon className="h-8 w-8 text-secondary-400" />
              </div>
              <h3 className="text-base font-medium text-secondary-900 mb-1">No securities yet</h3>
              <p className="text-sm text-secondary-600 mb-6">
                Start by adding securities to your platform.
              </p>
              <button 
                onClick={() => navigate('/securities')}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-soft"
              >
                Add Securities
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
