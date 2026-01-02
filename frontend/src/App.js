import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  ClipboardDocumentListIcon,
  UsersIcon,
  CubeIcon,
  TrophyIcon,
  ArrowUpTrayIcon,
  TagIcon,
} from '@heroicons/react/24/outline';

import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Customers from './pages/Customers';
import Products from './pages/Products';
import Brands from './pages/Brands';
import Leaderboard from './pages/Leaderboard';
import Upload from './pages/Upload';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Görevler', href: '/tasks', icon: ClipboardDocumentListIcon },
  { name: 'Müşteriler', href: '/customers', icon: UsersIcon },
  { name: 'Ürünler', href: '/products', icon: CubeIcon },
  { name: 'Markalar', href: '/brands', icon: TagIcon },
  { name: 'Liderlik', href: '/leaderboard', icon: TrophyIcon },
  { name: 'Veri Yükle', href: '/upload', icon: ArrowUpTrayIcon },
];

function NavLink({ item }) {
  const location = useLocation();
  const isActive = location.pathname === item.href;

  return (
    <Link
      to={item.href}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
        isActive
          ? 'bg-primary-600 text-white shadow-lg'
          : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <item.icon className="w-6 h-6" />
      <span className="font-medium">{item.name}</span>
    </Link>
  );
}

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white shadow-sm p-4">
        <h1 className="text-xl font-bold text-primary-600">SmartPharmacy</h1>
      </div>

      <div className="flex">
        {/* Sidebar - Desktop */}
        <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-white shadow-lg">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-primary-600">SmartPharmacy</h1>
            <p className="text-sm text-gray-500 mt-1">Eczane CRM</p>
          </div>
          <nav className="flex-1 px-4 space-y-2">
            {navigation.map((item) => (
              <NavLink key={item.name} item={item} />
            ))}
          </nav>
          <div className="p-4 border-t">
            <p className="text-xs text-gray-400 text-center">v1.0.0</p>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 lg:ml-64">
          <div className="p-4 lg:p-8">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg">
        <div className="flex justify-around py-2">
          {navigation.slice(0, 5).map((item) => {
            const location = useLocation();
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex flex-col items-center p-2 ${
                  isActive ? 'text-primary-600' : 'text-gray-400'
                }`}
              >
                <item.icon className="w-6 h-6" />
                <span className="text-xs mt-1">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/products" element={<Products />} />
          <Route path="/brands" element={<Brands />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/upload" element={<Upload />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
