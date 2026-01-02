import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  PhoneIcon,
  StarIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { getCustomers } from '../services/api';

const segmentColors = {
  VIP: 'bg-purple-100 text-purple-700 border-purple-200',
  DERMO_VIP: 'bg-pink-100 text-pink-700 border-pink-200',
  STANDARD: 'bg-gray-100 text-gray-700 border-gray-200',
  NEW: 'bg-blue-100 text-blue-700 border-blue-200',
  LOST: 'bg-red-100 text-red-700 border-red-200',
};

const segmentLabels = {
  VIP: 'VIP',
  DERMO_VIP: 'Dermo VIP',
  STANDARD: 'Standart',
  NEW: 'Yeni',
  LOST: 'Kayıp',
};

function CustomerCard({ customer }) {
  const riskColor = customer.churn_risk >= 75 ? 'text-red-500' :
                    customer.churn_risk >= 50 ? 'text-orange-500' :
                    customer.churn_risk >= 25 ? 'text-yellow-500' : 'text-green-500';

  return (
    <div className="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${segmentColors[customer.segment]}`}>
              {segmentLabels[customer.segment]}
            </span>
            {customer.churn_risk >= 50 && (
              <ExclamationTriangleIcon className={`w-4 h-4 ${riskColor}`} />
            )}
          </div>

          <h3 className="font-semibold text-gray-900">{customer.full_name}</h3>

          {customer.phone && (
            <a
              href={`tel:${customer.phone}`}
              className="flex items-center gap-1 text-sm text-primary-600 mt-1 hover:underline"
            >
              <PhoneIcon className="w-4 h-4" />
              {customer.phone}
            </a>
          )}
        </div>

        <div className="text-right">
          <div className="flex items-center justify-end gap-1 text-amber-500">
            <StarIcon className="w-5 h-5" />
            <span className="font-bold">{Math.round(customer.total_points).toLocaleString()}</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">Puan</p>
        </div>
      </div>

      {/* Risk Bar */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
          <span>Kayıp Riski</span>
          <span className={riskColor}>{customer.churn_risk}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              customer.churn_risk >= 75 ? 'bg-red-500' :
              customer.churn_risk >= 50 ? 'bg-orange-500' :
              customer.churn_risk >= 25 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${customer.churn_risk}%` }}
          />
        </div>
      </div>
    </div>
  );
}

function Customers() {
  const [searchParams] = useSearchParams();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [segment, setSegment] = useState(searchParams.get('segment') || '');

  useEffect(() => {
    loadCustomers();
  }, [segment]);

  const loadCustomers = async () => {
    setLoading(true);
    try {
      const params = {};
      if (segment) params.segment = segment;
      if (search) params.search = search;

      const response = await getCustomers(params);
      setCustomers(response.data.results || response.data);
    } catch (error) {
      console.error('Müşteriler yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadCustomers();
  };

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Müşteriler</h1>
        <p className="text-gray-500">{customers.length} müşteri listelendi</p>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="İsim veya telefon ara..."
          className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
        />
      </form>

      {/* Segment Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {['', 'VIP', 'DERMO_VIP', 'STANDARD', 'LOST'].map((seg) => (
          <button
            key={seg}
            onClick={() => setSegment(seg)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              segment === seg
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {seg ? segmentLabels[seg] : 'Tümü'}
          </button>
        ))}
      </div>

      {/* Customer List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : customers.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center shadow-sm border">
          <p className="text-gray-500">Müşteri bulunamadı</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {customers.map((customer) => (
            <CustomerCard key={customer.id} customer={customer} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Customers;
