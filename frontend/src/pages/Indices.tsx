import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api.ts';
import { Link } from 'react-router-dom';
import { PlusIcon, ChartBarIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';

const Indices: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch indices
  const { data: indices, isLoading } = useQuery({
    queryKey: ['indices'],
    queryFn: () => api.indices.list({ limit: 100 }),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.indices.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['indices'] });
    },
  });

  const filteredIndices = indices?.data?.filter((index: any) =>
    index.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    index.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this index?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Indices</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your index definitions and configurations.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setIsCreateModalOpen(true)}
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Index
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="max-w-lg">
        <input
          type="text"
          placeholder="Search indices..."
          className="input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Indices list */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredIndices.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredIndices.map((index: any) => (
            <div key={index.id} className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ChartBarIcon className="h-8 w-8 text-primary-600" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">{index.name}</h3>
                      <p className="text-sm text-gray-500">
                        {index.weighting_method.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      className="text-gray-400 hover:text-gray-600"
                      onClick={() => {/* Edit logic */}}
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      className="text-gray-400 hover:text-red-600"
                      onClick={() => handleDelete(index.id)}
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {index.description && (
                  <p className="mt-3 text-sm text-gray-600">{index.description}</p>
                )}
                
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Max: {index.max_constituents || '∞'}</span>
                    <span>Rebalance: {index.rebalance_frequency}</span>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    index.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {index.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="mt-4 flex space-x-2">
                  <Link
                    to={`/indices/${index.id}`}
                    className="flex-1 btn btn-outline text-center"
                  >
                    View Details
                  </Link>
                  <Link
                    to={`/indices/${index.id}/backtest`}
                    className="flex-1 btn btn-primary text-center"
                  >
                    Backtest
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No indices found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search terms.' : 'Get started by creating a new index.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setIsCreateModalOpen(true)}
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Create Index
              </button>
            </div>
          )}
        </div>
      )}

      {/* Create Index Modal */}
      {isCreateModalOpen && (
        <CreateIndexModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
        />
      )}
    </div>
  );
};

// Create Index Modal Component
const CreateIndexModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    weighting_method: 'equal_weight',
    rebalance_frequency: 'monthly',
    max_constituents: '',
    min_market_cap: '',
    max_market_cap: '',
  });

  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: any) => api.indices.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['indices'] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Index</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                required
                className="input mt-1"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                className="input mt-1"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Weighting Method</label>
              <select
                className="input mt-1"
                value={formData.weighting_method}
                onChange={(e) => setFormData({ ...formData, weighting_method: e.target.value })}
              >
                <option value="equal_weight">Equal Weight</option>
                <option value="market_cap_weight">Market Cap Weight</option>
                <option value="price_weight">Price Weight</option>
                <option value="revenue_weight">Revenue Weight</option>
                <option value="esg_weight">ESG Weight</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Rebalance Frequency</label>
              <select
                className="input mt-1"
                value={formData.rebalance_frequency}
                onChange={(e) => setFormData({ ...formData, rebalance_frequency: e.target.value })}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Max Constituents</label>
              <input
                type="number"
                className="input mt-1"
                value={formData.max_constituents}
                onChange={(e) => setFormData({ ...formData, max_constituents: e.target.value })}
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
                {createMutation.isPending ? 'Creating...' : 'Create Index'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Indices;
