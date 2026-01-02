import React, { useState } from 'react';
import {
  PhoneIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  StarIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import { completeTask } from '../services/api';

const priorityColors = {
  LOW: 'bg-gray-100 text-gray-600',
  MEDIUM: 'bg-blue-100 text-blue-600',
  HIGH: 'bg-orange-100 text-orange-600',
  URGENT: 'bg-red-100 text-red-600',
};

const typeIcons = {
  REPLENISHMENT: '💊',
  CHURN_PREVENTION: '⚠️',
  VIP_FOLLOWUP: '⭐',
  DERMO_CONSULT: '🧴',
  REMINDER_CALL: '📞',
  BIRTHDAY: '🎂',
  SPECIAL_DAY: '🎉',
};

function TaskCard({ task, onComplete, showDetails = false }) {
  const [completing, setCompleting] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleComplete = async (status = 'COMPLETED') => {
    setCompleting(true);
    try {
      await completeTask(task.id, { status });
      if (onComplete) onComplete(task.id);
    } catch (error) {
      console.error('Görev tamamlanamadı:', error);
      alert('Görev tamamlanırken hata oluştu');
    } finally {
      setCompleting(false);
    }
  };

  const isCompleted = task.status === 'COMPLETED';

  return (
    <div
      className={`bg-white rounded-xl border-2 p-4 transition-all ${
        isCompleted ? 'opacity-60 border-gray-200' : 'border-gray-100 hover:border-primary-200 hover:shadow-md'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Type Icon */}
        <div className="text-2xl flex-shrink-0">
          {typeIcons[task.task_type] || '📋'}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priorityColors[task.priority]}`}>
              {task.priority_display}
            </span>
            <span className="text-xs text-gray-400">{task.task_type_display}</span>
          </div>

          <h3 className={`font-semibold ${isCompleted ? 'line-through text-gray-400' : 'text-gray-900'}`}>
            {task.customer_name}
          </h3>

          <p className="text-sm text-gray-600 mt-1">{task.title}</p>

          {/* Phone */}
          {task.customer_phone && (
            <a
              href={`tel:${task.customer_phone}`}
              className="inline-flex items-center gap-1 text-sm text-primary-600 mt-2 hover:underline"
            >
              <PhoneIcon className="w-4 h-4" />
              {task.customer_phone}
            </a>
          )}

          {/* Expanded Details */}
          {showDetails && expanded && task.description && (
            <p className="text-sm text-gray-500 mt-2 bg-gray-50 p-2 rounded-lg">
              {task.description}
            </p>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-3 text-xs text-gray-400">
              {task.due_date && (
                <span className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  {new Date(task.due_date).toLocaleDateString('tr-TR')}
                </span>
              )}
              <span className="flex items-center gap-1">
                <StarIcon className="w-4 h-4" />
                {task.points_value} XP
              </span>
            </div>

            {showDetails && task.description && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-xs text-gray-500 hover:text-gray-700"
              >
                {expanded ? 'Gizle' : 'Detay'}
              </button>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        {!isCompleted && (
          <div className="flex flex-col gap-2 flex-shrink-0">
            <button
              onClick={() => handleComplete('COMPLETED')}
              disabled={completing}
              className="p-2 rounded-full bg-green-100 text-green-600 hover:bg-green-200 transition-colors disabled:opacity-50"
              title="Tamamlandı"
            >
              {completing ? (
                <div className="w-5 h-5 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
              ) : (
                <CheckCircleIcon className="w-5 h-5" />
              )}
            </button>
            <button
              onClick={() => handleComplete('UNREACHABLE')}
              disabled={completing}
              className="p-2 rounded-full bg-red-100 text-red-600 hover:bg-red-200 transition-colors disabled:opacity-50"
              title="Ulaşılamadı"
            >
              <XCircleIcon className="w-5 h-5" />
            </button>
          </div>
        )}

        {isCompleted && (
          <CheckCircleSolid className="w-8 h-8 text-green-500 flex-shrink-0" />
        )}
      </div>
    </div>
  );
}

export default TaskCard;
