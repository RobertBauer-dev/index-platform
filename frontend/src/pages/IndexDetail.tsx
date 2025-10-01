import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api.ts';
import { 
  ArrowLeftIcon, 
  ChartBarIcon, 
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon 
} from '@heroicons/react/24/outline';

const IndexDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: response, isLoading, error } = useQuery({
    queryKey: ['index', id],
    queryFn: async () => {
      const res = await api.indices.get(Number(id));
      console.log('Index Detail Response:', res.data);
      return res.data;
    },
    enabled: !!id,
  });

  const index = response;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mb-4"></div>
          <p className="text-secondary-600 text-sm">Loading index details...</p>
        </div>
      </div>
    );
  }

  if (error || !index) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-danger-100 rounded-2xl mb-4">
            <XCircleIcon className="h-8 w-8 text-danger-600" />
          </div>
          <h3 className="text-lg font-semibold text-secondary-900 mb-2">Index not found</h3>
          <p className="text-sm text-secondary-600 mb-6">
            The index you're looking for doesn't exist or has been deleted.
          </p>
          <button
            onClick={() => navigate('/indices')}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-soft"
          >
            Back to Indices
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/indices')}
            className="p-2 text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 rounded-xl transition-all duration-200"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-secondary-900">{index.name}</h1>
              {index.is_active ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-success-50 text-success-700 border border-success-200">
                  <CheckCircleIcon className="w-4 h-4 mr-1" />
                  Active
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-danger-50 text-danger-700 border border-danger-200">
                  <XCircleIcon className="w-4 h-4 mr-1" />
                  Inactive
                </span>
              )}
            </div>
            {index.description && (
              <p className="mt-2 text-sm text-secondary-600">{index.description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 text-sm font-medium text-secondary-700 bg-white border border-secondary-300 rounded-xl hover:bg-secondary-50 transition-all duration-200">
            Edit Index
          </button>
          <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-soft">
            Calculate Value
          </button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-secondary-100 shadow-soft">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-primary-50 rounded-xl border border-primary-100">
              <ChartBarIcon className="h-6 w-6 text-primary-600" />
            </div>
            <h3 className="text-sm font-medium text-secondary-600">Weighting Method</h3>
          </div>
          <p className="text-2xl font-bold text-secondary-900 capitalize">
            {index.weighting_method ? index.weighting_method.replace(/_/g, ' ') : 'N/A'}
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-secondary-100 shadow-soft">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-success-50 rounded-xl border border-success-100">
              <CalendarIcon className="h-6 w-6 text-success-600" />
            </div>
            <h3 className="text-sm font-medium text-secondary-600">Created</h3>
          </div>
          <p className="text-2xl font-bold text-secondary-900">
            {index.created_at ? new Date(index.created_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            }) : 'N/A'}
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-secondary-100 shadow-soft">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-warning-50 rounded-xl border border-warning-100">
              <ChartBarIcon className="h-6 w-6 text-warning-600" />
            </div>
            <h3 className="text-sm font-medium text-secondary-600">Base Value</h3>
          </div>
          <p className="text-2xl font-bold text-secondary-900">
            {index.base_value ? index.base_value.toLocaleString() : 'N/A'}
          </p>
        </div>
      </div>

      {/* Additional Details */}
      <div className="bg-white rounded-2xl border border-secondary-100 shadow-soft overflow-hidden">
        <div className="px-6 py-5 border-b border-secondary-100">
          <h3 className="text-lg font-semibold text-secondary-900">Index Details</h3>
        </div>
        <div className="p-6">
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <dt className="text-sm font-medium text-secondary-600 mb-1">Index ID</dt>
              <dd className="text-sm text-secondary-900">{index.id}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-secondary-600 mb-1">Symbol</dt>
              <dd className="text-sm text-secondary-900 font-mono">{index.symbol || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-secondary-600 mb-1">Base Date</dt>
              <dd className="text-sm text-secondary-900">
                {index.base_date ? new Date(index.base_date).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                }) : 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-secondary-600 mb-1">Last Updated</dt>
              <dd className="text-sm text-secondary-900">
                {index.updated_at ? new Date(index.updated_at).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                }) : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Placeholder for constituents */}
      <div className="bg-white rounded-2xl border border-secondary-100 shadow-soft overflow-hidden">
        <div className="px-6 py-5 border-b border-secondary-100">
          <h3 className="text-lg font-semibold text-secondary-900">Index Constituents</h3>
          <p className="mt-1 text-sm text-secondary-600">Securities included in this index</p>
        </div>
        <div className="p-16 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary-100 rounded-2xl mb-4">
            <ChartBarIcon className="h-8 w-8 text-secondary-400" />
          </div>
          <h3 className="text-base font-medium text-secondary-900 mb-1">Coming Soon</h3>
          <p className="text-sm text-secondary-600">
            Index constituents and weightings will be displayed here.
          </p>
        </div>
      </div>
    </div>
  );
};

export default IndexDetail;
