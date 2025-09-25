import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api.ts';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { PlusIcon, PlayIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

const IndexBuilder: React.FC = () => {
  const [step, setStep] = useState(1);
  const [indexConfig, setIndexConfig] = useState({
    name: '',
    description: '',
    filters: {
      sectors: [] as string[],
      countries: [] as string[],
      min_market_cap: '',
      max_market_cap: '',
      max_constituents: '',
    },
    weighting_method: 'equal_weight',
    start_date: '',
    end_date: '',
  });
  const [backtestResults, setBacktestResults] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);

  // Fetch available sectors and countries
  const { data: sectors } = useQuery({
    queryKey: ['sectors'],
    queryFn: () => api.securities.getSectors(),
  });

  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: () => api.securities.getCountries(),
  });

  // Backtest mutation
  const backtestMutation = useMutation({
    mutationFn: (data: any) => api.indices.createCustom(data),
    onSuccess: (result) => {
      setBacktestResults(result.data);
      setStep(4);
    },
    onError: (error) => {
      console.error('Backtest failed:', error);
    },
  });

  const handleRunBacktest = async () => {
    setIsRunning(true);
    try {
      await backtestMutation.mutateAsync(indexConfig);
    } finally {
      setIsRunning(false);
    }
  };

  const handleFilterChange = (filterType: string, value: any) => {
    setIndexConfig(prev => ({
      ...prev,
      filters: {
        ...prev.filters,
        [filterType]: value
      }
    }));
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Index Name</label>
            <input
              type="text"
              required
              className="input mt-1"
              value={indexConfig.name}
              onChange={(e) => setIndexConfig(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Tech Growth Index"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="input mt-1"
              rows={3}
              value={indexConfig.description}
              onChange={(e) => setIndexConfig(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe your index strategy..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Weighting Method</label>
            <select
              className="input mt-1"
              value={indexConfig.weighting_method}
              onChange={(e) => setIndexConfig(prev => ({ ...prev, weighting_method: e.target.value }))}
            >
              <option value="equal_weight">Equal Weight</option>
              <option value="market_cap_weight">Market Cap Weight</option>
              <option value="price_weight">Price Weight</option>
              <option value="revenue_weight">Revenue Weight</option>
              <option value="esg_weight">ESG Weight</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setStep(2)}
          disabled={!indexConfig.name}
        >
          Next: Filters
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Index Filters</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Sectors</label>
            <div className="mt-2 grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
              {sectors?.data?.map((sector: string) => (
                <label key={sector} className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    checked={indexConfig.filters.sectors.includes(sector)}
                    onChange={(e) => {
                      const newSectors = e.target.checked
                        ? [...indexConfig.filters.sectors, sector]
                        : indexConfig.filters.sectors.filter(s => s !== sector);
                      handleFilterChange('sectors', newSectors);
                    }}
                  />
                  <span className="ml-2 text-sm text-gray-700">{sector}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Countries</label>
            <div className="mt-2 grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
              {countries?.data?.map((country: string) => (
                <label key={country} className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    checked={indexConfig.filters.countries.includes(country)}
                    onChange={(e) => {
                      const newCountries = e.target.checked
                        ? [...indexConfig.filters.countries, country]
                        : indexConfig.filters.countries.filter(c => c !== country);
                      handleFilterChange('countries', newCountries);
                    }}
                  />
                  <span className="ml-2 text-sm text-gray-700">{country}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Min Market Cap (USD)</label>
              <input
                type="number"
                className="input mt-1"
                value={indexConfig.filters.min_market_cap}
                onChange={(e) => handleFilterChange('min_market_cap', e.target.value)}
                placeholder="e.g., 1000000000"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Max Market Cap (USD)</label>
              <input
                type="number"
                className="input mt-1"
                value={indexConfig.filters.max_market_cap}
                onChange={(e) => handleFilterChange('max_market_cap', e.target.value)}
                placeholder="e.g., 1000000000000"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Max Constituents</label>
            <input
              type="number"
              className="input mt-1"
              value={indexConfig.filters.max_constituents}
              onChange={(e) => handleFilterChange('max_constituents', e.target.value)}
              placeholder="e.g., 50"
            />
          </div>
        </div>
      </div>
      
      <div className="flex justify-between">
        <button
          type="button"
          className="btn btn-outline"
          onClick={() => setStep(1)}
        >
          Back
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setStep(3)}
        >
          Next: Time Range
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Backtest Configuration</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Start Date</label>
            <input
              type="date"
              required
              className="input mt-1"
              value={indexConfig.start_date}
              onChange={(e) => setIndexConfig(prev => ({ ...prev, start_date: e.target.value }))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">End Date</label>
            <input
              type="date"
              className="input mt-1"
              value={indexConfig.end_date}
              onChange={(e) => setIndexConfig(prev => ({ ...prev, end_date: e.target.value }))}
            />
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h4 className="text-sm font-medium text-blue-800 mb-2">Index Summary</h4>
            <div className="text-sm text-blue-700 space-y-1">
              <p><strong>Name:</strong> {indexConfig.name}</p>
              <p><strong>Weighting:</strong> {indexConfig.weighting_method.replace('_', ' ')}</p>
              <p><strong>Sectors:</strong> {indexConfig.filters.sectors.length > 0 ? indexConfig.filters.sectors.join(', ') : 'All'}</p>
              <p><strong>Countries:</strong> {indexConfig.filters.countries.length > 0 ? indexConfig.filters.countries.join(', ') : 'All'}</p>
              <p><strong>Max Constituents:</strong> {indexConfig.filters.max_constituents || 'Unlimited'}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex justify-between">
        <button
          type="button"
          className="btn btn-outline"
          onClick={() => setStep(2)}
        >
          Back
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleRunBacktest}
          disabled={!indexConfig.start_date || isRunning}
        >
          {isRunning ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Running Backtest...
            </>
          ) : (
            <>
              <PlayIcon className="h-4 w-4 mr-2" />
              Run Backtest
            </>
          )}
        </button>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Backtest Results</h3>
        
        {backtestResults && (
          <div className="space-y-6">
            {/* Performance Chart */}
            <div className="card">
              <div className="card-header">
                <h4 className="text-lg font-medium text-gray-900">Performance Chart</h4>
              </div>
              <div className="card-body">
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={backtestResults.index_series}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(value) => new Date(value).toLocaleDateString()}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => new Date(value).toLocaleDateString()}
                        formatter={(value: any) => [value.toFixed(2), 'Index Value']}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="index_value" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
            
            {/* Performance Metrics */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="card">
                <div className="card-body">
                  <div className="text-2xl font-bold text-gray-900">
                    {(backtestResults.performance_metrics?.total_return * 100 || 0).toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-500">Total Return</div>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body">
                  <div className="text-2xl font-bold text-gray-900">
                    {(backtestResults.performance_metrics?.volatility * 100 || 0).toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-500">Volatility</div>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body">
                  <div className="text-2xl font-bold text-gray-900">
                    {backtestResults.performance_metrics?.sharpe_ratio?.toFixed(2) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">Sharpe Ratio</div>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body">
                  <div className="text-2xl font-bold text-gray-900">
                    {(backtestResults.performance_metrics?.max_drawdown * 100 || 0).toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-500">Max Drawdown</div>
                </div>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex justify-center space-x-4">
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => setStep(1)}
              >
                Create Another Index
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {/* Save index logic */}}
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Save Index
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {/* Export logic */}}
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                Export Results
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Custom Index Builder</h1>
        <p className="mt-2 text-sm text-gray-700">
          Create and backtest custom indices with your own criteria.
        </p>
      </div>

      {/* Progress indicator */}
      <div className="flex items-center justify-center">
        <div className="flex items-center space-x-4">
          {[1, 2, 3, 4].map((stepNumber) => (
            <div key={stepNumber} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                step >= stepNumber
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {stepNumber}
              </div>
              {stepNumber < 4 && (
                <div className={`w-16 h-1 mx-2 ${
                  step > stepNumber ? 'bg-primary-600' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step content */}
      <div className="max-w-4xl mx-auto">
        <div className="card">
          <div className="card-body">
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
            {step === 4 && renderStep4()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndexBuilder;
