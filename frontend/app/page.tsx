'use client';

import { useSystemStatus, useDashboard, useApiConnection } from '@/lib/api/hooks';
import { StatusCard } from '@/components/ui/StatusCard';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { EvolutionControls } from '@/components/evolution/EvolutionControls';
import { Cpu, Brain, Zap, Activity, Clock, BarChart3 } from 'lucide-react';

export default function Home() {
  const { data: apiConnected } = useApiConnection();
  const { data: status, isLoading: statusLoading } = useSystemStatus();
  const { data: dashboard, isLoading: dashboardLoading } = useDashboard();

  const isLoading = statusLoading || dashboardLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Carregando dashboard evolutivo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Status da API */}
      <div className={`p-4 rounded-lg ${apiConnected ? 'bg-green-900/20 border border-green-800' : 'bg-red-900/20 border border-red-800'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`h-3 w-3 rounded-full ${apiConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <div>
              <p className="font-medium">
                {apiConnected ? '✅ API Evolution conectada' : '❌ API Evolution desconectada'}
              </p>
              <p className="text-sm text-gray-400">
                {apiConnected 
                  ? `Conectado a localhost:8000 • Uptime: ${status?.uptime_seconds ? Math.floor(status.uptime_seconds / 3600) : 0}h`
                  : 'Verifique se o servidor da API está rodando na porta 8000'
                }
              </p>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            Atualização automática ativa
          </div>
        </div>
      </div>

      {/* Cards de Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatusCard
          title="Geração Atual"
          value={status?.generation || 0}
          subtitle="Evoluções realizadas"
          icon={<Cpu className="h-6 w-6" />}
          color="success"
          trend="up"
        />
        <StatusCard
          title="Mutações Totais"
          value={dashboard?.status.total_mutations || 0}
          subtitle="Alterações estruturais"
          icon={<Zap className="h-6 w-6" />}
          color="warning"
          trend="up"
        />
        <StatusCard
          title="Evoluções Totais"
          value={dashboard?.status.total_evolutions || 0}
          subtitle="Evoluções cerebrais"
          icon={<Brain className="h-6 w-6" />}
          color="default"
          trend="neutral"
        />
        <StatusCard
          title="Taxa de Sucesso"
          value={`${dashboard?.statistics.success_rate ? (dashboard.statistics.success_rate * 100).toFixed(1) : 0}%`}
          subtitle="Evoluções bem-sucedidas"
          icon={<BarChart3 className="h-6 w-6" />}
          color="success"
          trend="up"
        />
      </div>

      {/* Grid Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Coluna 1: Controles e Status */}
        <div className="lg:col-span-1 space-y-6">
          <EvolutionControls />
          
          {/* Status dos Componentes */}
          <div className="glass-dark rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-6">🔧 Componentes do Sistema</h3>
            <div className="space-y-4">
              {status?.components && Object.entries(status.components).map(([name, compStatus]) => (
                <div key={name} className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50">
                  <div className="flex items-center gap-3">
                    <div className={`h-2 w-2 rounded-full ${
                      compStatus === 'available' || compStatus === 'active' 
                        ? 'bg-green-500 animate-pulse' 
                        : 'bg-red-500'
                    }`}></div>
                    <span className="font-medium">{name}</span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    compStatus === 'available' || compStatus === 'active'
                      ? 'bg-green-900/50 text-green-400'
                      : 'bg-red-900/50 text-red-400'
                  }`}>
                    {compStatus}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Coluna 2: Dashboard e Atividade */}
        <div className="lg:col-span-2 space-y-6">
          <ActivityFeed
            mutations={dashboard?.recent_activity.mutations}
            evolutions={dashboard?.recent_activity.evolutions}
            alerts={dashboard?.recent_activity.alerts}
          />

          {/* Estatísticas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tipos de Mutação */}
            <div className="glass-dark rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-6">📊 Tipos de Mutação</h3>
              <div className="space-y-3">
                {dashboard?.statistics.mutation_types && Object.entries(dashboard.statistics.mutation_types).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-gray-400">{type.replace('_', ' ')}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${(count as number / Math.max(1, dashboard.status.total_mutations)) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-medium w-8 text-right">{count as number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tipos de Evolução */}
            <div className="glass-dark rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-6">🧠 Tipos de Evolução</h3>
              <div className="space-y-3">
                {dashboard?.statistics.evolution_types && Object.entries(dashboard.statistics.evolution_types).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-gray-400">{type.replace('_', ' ')}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-purple-500 rounded-full"
                          style={{ width: `${(count as number / Math.max(1, dashboard.status.total_evolutions)) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-medium w-8 text-right">{count as number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Rodapé Informativo */}
      <div className="glass-dark rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-semibold mb-2">🚀 Sistema Biomimético</h4>
            <p className="text-gray-400 text-sm">
              Sistema evolutivo que imita processos biológicos para otimização contínua de agentes IA.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">⚡ Funcionalidades</h4>
            <ul className="text-gray-400 text-sm space-y-1">
              <li>• Mutação estrutural do genoma</li>
              <li>• Evolução cerebral de modelos</li>
              <li>• Monitoramento em tempo real</li>
              <li>• Aprendizado evolutivo contínuo</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">🔗 Endpoints da API</h4>
            <ul className="text-gray-400 text-sm space-y-1 font-mono">
              <li>• GET /health</li>
              <li>• GET /status</li>
              <li>• POST /evolve/structure</li>
              <li>• POST /evolve/brain</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}