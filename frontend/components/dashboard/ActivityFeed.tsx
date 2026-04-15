'use client';

import { useState } from 'react';
import { AlertRecord, MutationRecord, EvolutionRecord } from '@/lib/api/types';
import { AlertTriangle, Brain, Cpu, Zap, Clock } from 'lucide-react';

interface ActivityFeedProps {
  mutations?: MutationRecord[];
  evolutions?: EvolutionRecord[];
  alerts?: AlertRecord[];
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'structural_change':
      return <Cpu className="h-4 w-4 text-blue-400" />;
    case 'brain_evolution':
      return <Brain className="h-4 w-4 text-purple-400" />;
    case 'performance_alert':
      return <Zap className="h-4 w-4 text-yellow-400" />;
    case 'component_alert':
      return <AlertTriangle className="h-4 w-4 text-red-400" />;
    default:
      return <Zap className="h-4 w-4 text-gray-400" />;
  }
};

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Agora mesmo';
  if (diffMins < 60) return `${diffMins} min atrás`;
  if (diffHours < 24) return `${diffHours} h atrás`;
  return `${diffDays} dias atrás`;
};

export function ActivityFeed({ mutations = [], evolutions = [], alerts = [] }: ActivityFeedProps) {
  const [activeTab, setActiveTab] = useState<'all' | 'mutations' | 'evolutions' | 'alerts'>('all');

  // Combinar todas as atividades
  const allActivities = [
    ...mutations.map(m => ({
      ...m,
      activityType: 'mutation' as const,
      icon: <Cpu className="h-4 w-4 text-blue-400" />,
    })),
    ...evolutions.map(e => ({
      ...e,
      activityType: 'evolution' as const,
      icon: <Brain className="h-4 w-4 text-purple-400" />,
    })),
    ...alerts.map(a => ({
      ...a,
      activityType: 'alert' as const,
      icon: getActivityIcon(a.type),
    })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  // Filtrar por tab ativa
  const filteredActivities = allActivities.filter(activity => {
    if (activeTab === 'all') return true;
    if (activeTab === 'mutations') return activity.activityType === 'mutation';
    if (activeTab === 'evolutions') return activity.activityType === 'evolution';
    if (activeTab === 'alerts') return activity.activityType === 'alert';
    return true;
  }).slice(0, 10); // Limitar a 10 itens

  return (
    <div className="glass-dark rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold">📈 Atividade Recente</h3>
        <div className="flex space-x-2">
          {['all', 'mutations', 'evolutions', 'alerts'].map(tab => (
            <button
              key={tab}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
              onClick={() => setActiveTab(tab as any)}
            >
              {tab === 'all' ? 'Todos' : 
               tab === 'mutations' ? 'Mutações' : 
               tab === 'evolutions' ? 'Evoluções' : 'Alertas'}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {filteredActivities.length > 0 ? (
          filteredActivities.map((activity, index) => (
            <div
              key={`${activity.activityType}-${activity.id || index}`}
              className="flex items-start gap-3 p-3 rounded-lg bg-gray-900/50 hover:bg-gray-800/50 transition-colors"
            >
              <div className="mt-1">{activity.icon}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium">
                    {activity.activityType === 'mutation' 
                      ? `Mutação: ${activity.type}`
                      : activity.activityType === 'evolution'
                      ? `Evolução: ${activity.type}`
                      : activity.type === 'alert' 
                      ? activity.message
                      : 'Atividade'}
                  </span>
                  <span className="text-gray-500 text-sm flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatTime(activity.timestamp)}
                  </span>
                </div>
                <p className="text-gray-400 text-sm mt-1">
                  {activity.activityType === 'mutation' 
                    ? `${activity.data?.changes?.[0] || 'Detalhes da mutação'}`
                    : activity.activityType === 'evolution'
                    ? `${activity.data?.changes?.[0] || 'Detalhes da evolução'}`
                    : activity.type === 'alert' 
                    ? `Nível: ${activity.level}`
                    : 'Detalhes'}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>Nenhuma atividade recente</p>
          </div>
        )}
      </div>
    </div>
  );
}