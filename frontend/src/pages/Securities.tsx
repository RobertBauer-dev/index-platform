import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api.ts';
import { PlusIcon, BuildingLibraryIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const Securities: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const queryClient = useQueryClient();

  // Fetch securities
  const { data: securities, isLoading } = useQuery({
    queryKey: ['securities', { search: searchTerm, sector: selectedSector, country: selectedCountry }],
    queryFn: () => api.securities.list({
      search: searchTerm,
      sector: selectedSector,
      country: selectedCountry,
      limit: 100
    }),
  });

  // Fetch sectors and countries for filters
  const { data: sectors } = useQuery({
    queryKey: ['sectors'],
    queryFn: () => api.securities.getSectors(),
  });

  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: () => api.securities.getCountries(),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.securities.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['securities'] });
    },
  });

  // Market cap update mutations
  const updateMarketCapMutation = useMutation({
    mutationFn: (id: number) => api.securities.updateMarketCap(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['securities'] });
    },
  });

  const batchUpdateMarketCapMutation = useMutation({
    mutationFn: (symbols: string[]) => api.securities.batchUpdateMarketCap(symbols),
    onSuccess: (data) => {
      console.log('Market cap batch update response:', data);
      queryClient.invalidateQueries({ queryKey: ['securities'] });
      setNotification({
        type: 'success',
        message: `Market caps updated successfully!`
      });
      setTimeout(() => setNotification(null), 5000);
    },
    onError: (error: any) => {
      console.error('Market cap batch update error:', error);
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to update market caps'
      });
      setTimeout(() => setNotification(null), 5000);
    },
  });

  const updateAllMarketCapMutation = useMutation({
    mutationFn: () => api.securities.updateAllMarketCaps(),
    onSuccess: (data) => {
      console.log('Market cap update all response:', data);
      queryClient.invalidateQueries({ queryKey: ['securities'] });
      setNotification({
        type: 'success',
        message: `All market caps updated successfully!`
      });
      setTimeout(() => setNotification(null), 5000);
    },
    onError: (error: any) => {
      console.error('Market cap update all error:', error);
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to update all market caps'
      });
      setTimeout(() => setNotification(null), 5000);
    },
  });

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this security?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleUpdateMarketCap = (id: number) => {
    updateMarketCapMutation.mutate(id);
  };

  const handleBatchUpdateMarketCap = () => {
    if (!securities?.data) return;
    const symbols = securities.data.map((s: any) => s.symbol);
    batchUpdateMarketCapMutation.mutate(symbols);
  };

  const handleUpdateAllMarketCap = () => {
    if (window.confirm('This will update market cap for all securities. Continue?')) {
      updateAllMarketCapMutation.mutate();
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 max-w-md rounded-xl p-4 shadow-strong border ${
          notification.type === 'success' 
            ? 'bg-success-50 border-success-200' 
            : 'bg-danger-50 border-danger-200'
        } animate-slide-down`}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {notification.type === 'success' ? (
                <svg className="h-5 w-5 text-success-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="h-5 w-5 text-danger-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div className="ml-3">
              <p className={`text-sm font-medium ${
                notification.type === 'success' ? 'text-success-800' : 'text-danger-800'
              }`}>
                {notification.message}
              </p>
            </div>
            <button
              onClick={() => setNotification(null)}
              className="ml-auto text-secondary-400 hover:text-secondary-600"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}
      
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Securities</h1>
          <p className="mt-2 text-sm text-secondary-600">
            Manage your securities database and market data
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-secondary-700 bg-white border border-secondary-300 rounded-xl hover:bg-secondary-50 transition-all duration-200 flex items-center disabled:opacity-50"
            onClick={handleBatchUpdateMarketCap}
            disabled={batchUpdateMarketCapMutation.isPending || updateAllMarketCapMutation.isPending}
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${batchUpdateMarketCapMutation.isPending ? 'animate-spin' : ''}`} />
            {batchUpdateMarketCapMutation.isPending ? 'Updating...' : 'Update Visible'}
          </button>
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-white bg-warning-600 rounded-xl hover:bg-warning-700 transition-all duration-200 shadow-soft flex items-center disabled:opacity-50"
            onClick={handleUpdateAllMarketCap}
            disabled={updateAllMarketCapMutation.isPending || batchUpdateMarketCapMutation.isPending}
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${updateAllMarketCapMutation.isPending ? 'animate-spin' : ''}`} />
            {updateAllMarketCapMutation.isPending ? 'Updating All...' : 'Update All'}
          </button>
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-soft flex items-center"
            onClick={() => setIsCreateModalOpen(true)}
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Security
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search securities..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        <div>
          <select
            className="input"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
          >
            <option value="">All Sectors</option>
            {sectors?.data?.map((sector: string) => (
              <option key={sector} value={sector}>{sector}</option>
            ))}
          </select>
        </div>
        
        <div>
          <select
            className="input"
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
          >
            <option value="">All Countries</option>
            {countries?.data?.map((country: string) => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>
        
        <div>
          <button
            type="button"
            className="btn btn-outline w-full"
            onClick={() => {
              setSearchTerm('');
              setSelectedSector('');
              setSelectedCountry('');
            }}
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Securities table */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : securities?.data?.length > 0 ? (
        <div className="card">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Exchange
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sector
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Country
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Market Cap
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {securities.data.map((security: any) => (
                  <tr key={security.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {security.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {security.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {security.exchange || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {security.sector || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {security.country || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {security.market_cap ? `$${(security.market_cap / 1e9).toFixed(1)}B` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        security.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {security.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          className="text-blue-600 hover:text-blue-900"
                          onClick={() => handleUpdateMarketCap(security.id)}
                          disabled={updateMarketCapMutation.isPending}
                          title="Update Market Cap"
                        >
                          <ArrowPathIcon className="h-4 w-4" />
                        </button>
                        <button
                          className="text-primary-600 hover:text-primary-900"
                          onClick={() => {/* Edit logic */}}
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button
                          className="text-red-600 hover:text-red-900"
                          onClick={() => handleDelete(security.id)}
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <BuildingLibraryIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No securities found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || selectedSector || selectedCountry 
              ? 'Try adjusting your search filters.' 
              : 'Get started by adding securities to your database.'
            }
          </p>
          {!searchTerm && !selectedSector && !selectedCountry && (
            <div className="mt-6">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setIsCreateModalOpen(true)}
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Security
              </button>
            </div>
          )}
        </div>
      )}

      {/* Create Security Modal */}
      {isCreateModalOpen && (
        <CreateSecurityModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
        />
      )}
    </div>
  );
};

// Create Security Modal Component
const CreateSecurityModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    symbol: '',
    name: '',
    exchange: '',
    currency: 'USD',
    sector: '',
    industry: '',
    country: '',
    market_cap: '',
  });

  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: any) => api.securities.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['securities'] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      market_cap: formData.market_cap ? parseFloat(formData.market_cap) : null,
    };
    createMutation.mutate(submitData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Security</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Symbol *</label>
              <input
                type="text"
                required
                className="input mt-1"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Name *</label>
              <input
                type="text"
                required
                className="input mt-1"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Exchange</label>
              <input
                type="text"
                className="input mt-1"
                value={formData.exchange}
                onChange={(e) => setFormData({ ...formData, exchange: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Currency</label>
              <select
                className="input mt-1"
                value={formData.currency}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="JPY">JPY</option>
                <option value="CHF">CHF</option>
                <option value="CAD">CAD</option>
                <option value="AUD">AUD</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Sector</label>
              <input
                type="text"
                className="input mt-1"
                value={formData.sector}
                onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Industry</label>
              <input
                type="text"
                className="input mt-1"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Country</label>
              <input
                type="text"
                className="input mt-1"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Market Cap</label>
              <input
                type="number"
                className="input mt-1"
                value={formData.market_cap}
                onChange={(e) => setFormData({ ...formData, market_cap: e.target.value })}
              />
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                className="btn btn-outline"
                onClick={onClose}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? 'Adding...' : 'Add Security'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Securities;
