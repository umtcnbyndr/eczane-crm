import React, { useState, useEffect } from 'react';
import {
  TrophyIcon,
  StarIcon,
  FireIcon,
} from '@heroicons/react/24/solid';
import { getLeaderboard } from '../services/api';

const medalColors = {
  1: 'bg-yellow-100 text-yellow-600 border-yellow-300',
  2: 'bg-gray-100 text-gray-600 border-gray-300',
  3: 'bg-orange-100 text-orange-600 border-orange-300',
};

const medalIcons = {
  1: '🥇',
  2: '🥈',
  3: '🥉',
};

function LeaderboardCard({ staff, rank }) {
  const isTopThree = rank <= 3;

  return (
    <div
      className={`bg-white rounded-xl border-2 p-4 transition-all hover:shadow-md ${
        isTopThree ? medalColors[rank] : 'border-gray-100'
      }`}
    >
      <div className="flex items-center gap-4">
        {/* Rank */}
        <div className="flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-full bg-gray-100">
          {isTopThree ? (
            <span className="text-2xl">{medalIcons[rank]}</span>
          ) : (
            <span className="text-lg font-bold text-gray-500">{rank}</span>
          )}
        </div>

        {/* Info */}
        <div className="flex-1">
          <h3 className="font-bold text-gray-900">{staff.name}</h3>
          <p className="text-sm text-gray-500">{staff.tasks_completed} görev tamamlandı</p>
        </div>

        {/* Points */}
        <div className="text-right">
          <div className="flex items-center gap-1 text-primary-600">
            <StarIcon className="w-5 h-5" />
            <span className="text-xl font-bold">{staff.weekly_points}</span>
          </div>
          <p className="text-xs text-gray-400">XP</p>
        </div>
      </div>
    </div>
  );
}

function Leaderboard() {
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('weekly');

  useEffect(() => {
    loadLeaderboard();
  }, [period]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await getLeaderboard(period);
      setStaff(response.data);
    } catch (error) {
      console.error('Liderlik tablosu yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const topThree = staff.slice(0, 3);
  const rest = staff.slice(3);

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <TrophyIcon className="w-8 h-8 text-yellow-500" />
          Liderlik Tablosu
        </h1>
        <p className="text-gray-500 mt-1">En çok puan kazananlar</p>
      </div>

      {/* Period Selector */}
      <div className="flex justify-center gap-2">
        {[
          { value: 'weekly', label: 'Bu Hafta' },
          { value: 'monthly', label: 'Bu Ay' },
          { value: 'total', label: 'Tüm Zamanlar' },
        ].map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              period === p.value
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : staff.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center shadow-sm border">
          <TrophyIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">Henüz sıralama yok</p>
        </div>
      ) : (
        <>
          {/* Top 3 Podium */}
          {topThree.length > 0 && (
            <div className="flex justify-center items-end gap-4 py-4">
              {/* 2nd Place */}
              {topThree[1] && (
                <div className="text-center">
                  <div className="text-4xl mb-2">🥈</div>
                  <div className="bg-gray-100 rounded-xl p-4 w-28">
                    <p className="font-bold text-gray-900 text-sm truncate">{topThree[1].name}</p>
                    <p className="text-primary-600 font-bold mt-1">{topThree[1].weekly_points} XP</p>
                  </div>
                  <div className="h-16 bg-gray-200 rounded-b-xl" />
                </div>
              )}

              {/* 1st Place */}
              {topThree[0] && (
                <div className="text-center -mt-8">
                  <div className="text-5xl mb-2">🥇</div>
                  <div className="bg-yellow-100 rounded-xl p-4 w-32 border-2 border-yellow-300">
                    <p className="font-bold text-gray-900 truncate">{topThree[0].name}</p>
                    <p className="text-primary-600 font-bold text-lg mt-1">{topThree[0].weekly_points} XP</p>
                  </div>
                  <div className="h-24 bg-yellow-200 rounded-b-xl" />
                </div>
              )}

              {/* 3rd Place */}
              {topThree[2] && (
                <div className="text-center">
                  <div className="text-4xl mb-2">🥉</div>
                  <div className="bg-orange-100 rounded-xl p-4 w-28">
                    <p className="font-bold text-gray-900 text-sm truncate">{topThree[2].name}</p>
                    <p className="text-primary-600 font-bold mt-1">{topThree[2].weekly_points} XP</p>
                  </div>
                  <div className="h-12 bg-orange-200 rounded-b-xl" />
                </div>
              )}
            </div>
          )}

          {/* Rest of the List */}
          {rest.length > 0 && (
            <div className="space-y-3">
              {rest.map((s) => (
                <LeaderboardCard key={s.id} staff={s} rank={s.rank} />
              ))}
            </div>
          )}
        </>
      )}

      {/* Motivation */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 text-white text-center">
        <FireIcon className="w-12 h-12 mx-auto mb-3 opacity-80" />
        <h3 className="font-bold text-lg">Harika Gidiyorsun!</h3>
        <p className="text-sm opacity-90 mt-1">
          Her tamamlanan görev seni zirveye taşıyor
        </p>
      </div>
    </div>
  );
}

export default Leaderboard;
