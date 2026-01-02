import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  UsersIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  StarIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import { getDashboardStats, getTodayTasks } from '../services/api';
import TaskCard from '../components/TaskCard';

function StatCard({ title, value, icon: Icon, color, subtext }) {
  const colorClasses = {
    green: 'bg-green-50 text-green-600 border-green-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
  };

  return (
    <div className={`rounded-2xl border-2 p-5 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
          {subtext && <p className="text-xs mt-1 opacity-70">{subtext}</p>}
        </div>
        <Icon className="w-12 h-12 opacity-50" />
      </div>
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, tasksRes] = await Promise.all([
        getDashboardStats(),
        getTodayTasks()
      ]);
      setStats(statsRes.data);
      setTasks(tasksRes.data.slice(0, 5));
    } catch (error) {
      console.error('Dashboard veri yükleme hatası:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskComplete = (taskId) => {
    setTasks(tasks.filter(t => t.id !== taskId));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Merhaba!</h1>
        <p className="text-gray-500">Bugünün özeti</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Bugünün Görevleri"
          value={stats?.today_tasks || 0}
          icon={ClipboardDocumentCheckIcon}
          color="blue"
          subtext={`${stats?.completed_tasks_today || 0} tamamlandı`}
        />
        <StatCard
          title="Toplam Müşteri"
          value={stats?.total_customers || 0}
          icon={UsersIcon}
          color="green"
          subtext={`${stats?.vip_customers || 0} VIP`}
        />
        <StatCard
          title="Risk Altında"
          value={stats?.at_risk_customers || 0}
          icon={ExclamationTriangleIcon}
          color="yellow"
          subtext="Kayıp riski yüksek"
        />
        <StatCard
          title="Bugün Kazanılan XP"
          value={stats?.total_points_today || 0}
          icon={StarIcon}
          color="purple"
          subtext="Harika gidiyorsun!"
        />
      </div>

      {/* Today's Tasks */}
      <div className="bg-white rounded-2xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Bugünün Görevleri</h2>
          <Link
            to="/tasks"
            className="flex items-center text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Tümünü Gör
            <ArrowRightIcon className="w-4 h-4 ml-1" />
          </Link>
        </div>

        {tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <ClipboardDocumentCheckIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Harika! Tüm görevler tamamlandı.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onComplete={handleTaskComplete}
              />
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          to="/customers?segment=LOST"
          className="bg-red-50 border-2 border-red-200 rounded-2xl p-4 hover:shadow-md transition-shadow"
        >
          <h3 className="font-bold text-red-700">Kayıp Müşteriler</h3>
          <p className="text-sm text-red-600 mt-1">{stats?.lost_customers || 0} müşteri</p>
        </Link>
        <Link
          to="/products?low_stock=true"
          className="bg-orange-50 border-2 border-orange-200 rounded-2xl p-4 hover:shadow-md transition-shadow"
        >
          <h3 className="font-bold text-orange-700">Düşük Stok</h3>
          <p className="text-sm text-orange-600 mt-1">{stats?.low_stock_products || 0} ürün</p>
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;
