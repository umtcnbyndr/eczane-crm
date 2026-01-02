import React, { useState, useEffect } from 'react';
import {
  FunnelIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import { getTasks, getTodayTasks } from '../services/api';
import TaskCard from '../components/TaskCard';

const statusFilters = [
  { value: '', label: 'Tümü' },
  { value: 'PENDING', label: 'Bekliyor' },
  { value: 'IN_PROGRESS', label: 'Devam Ediyor' },
  { value: 'COMPLETED', label: 'Tamamlandı' },
];

const typeFilters = [
  { value: '', label: 'Tüm Tipler' },
  { value: 'REPLENISHMENT', label: 'Ürün Hatırlatma' },
  { value: 'CHURN_PREVENTION', label: 'Kayıp Önleme' },
  { value: 'VIP_FOLLOWUP', label: 'VIP Takip' },
  { value: 'DERMO_CONSULT', label: 'Dermo Danışmanlık' },
  { value: 'REMINDER_CALL', label: 'Hatırlatma Araması' },
];

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [typeFilter, setTypeFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadTasks();
  }, [statusFilter, typeFilter]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (typeFilter) params.type = typeFilter;

      const response = await getTasks(params);
      setTasks(response.data.results || response.data);
    } catch (error) {
      console.error('Görevler yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskComplete = (taskId) => {
    setTasks(tasks.filter(t => t.id !== taskId));
  };

  const pendingCount = tasks.filter(t => t.status === 'PENDING').length;
  const completedCount = tasks.filter(t => t.status === 'COMPLETED').length;

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Görevler</h1>
          <p className="text-gray-500">{pendingCount} bekleyen görev</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`p-2 rounded-lg ${showFilters ? 'bg-primary-100 text-primary-600' : 'bg-gray-100'}`}
        >
          <FunnelIcon className="w-6 h-6" />
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white rounded-xl p-4 shadow-sm border space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Durum</label>
            <div className="flex flex-wrap gap-2">
              {statusFilters.map((filter) => (
                <button
                  key={filter.value}
                  onClick={() => setStatusFilter(filter.value)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    statusFilter === filter.value
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Görev Tipi</label>
            <div className="flex flex-wrap gap-2">
              {typeFilters.map((filter) => (
                <button
                  key={filter.value}
                  onClick={() => setTypeFilter(filter.value)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    typeFilter === filter.value
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Task List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center shadow-sm border">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900">Görev bulunamadı</h3>
          <p className="text-gray-500 mt-1">Seçili filtrelere uygun görev yok.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={handleTaskComplete}
              showDetails
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Tasks;
