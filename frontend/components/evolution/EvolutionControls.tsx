'use client';

import { useState } from 'react';
import { useEvolveStructure, useEvolveBrain, useIncrementGeneration } from '@/lib/api/hooks';
import { MUTATION_TYPES, EVOLUTION_TYPES } from '@/lib/api/types';
import { Zap, Brain, Cpu, Plus } from 'lucide-react';

export function EvolutionControls() {
  const [evolutionType, setEvolutionType] = useState<string>(MUTATION_TYPES[0]);
  const [intensity, setIntensity] = useState<number>(0.5);
  const [activeTab, setActiveTab] = useState<'structural' | 'brain'>('structural');

  const { mutate: evolveStructure, isPending: isEvolvingStructure } = useEvolveStructure();
  const { mutate: evolveBrain, isPending: isEvolvingBrain } = useEvolveBrain();
  const { mutate: incrementGeneration, isPending: isIncrementing } = useIncrementGeneration();

  const handleStructuralEvolution = () => {
    evolveStructure({
      evolution_type: evolutionType,
      intensity,
      component: 'genome_mutator',
    });
  };

  const handleBrainEvolution = () => {
    evolveBrain({
      evolution_type: evolutionType,
      intensity,
      component: 'brain_evolver',
    });
  };

  const handleIncrementGeneration = () => {
    incrementGeneration();
  };

  return (
    <div className="glass-dark rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold">⚡ Controles de Evolução</h3>
        <button
          onClick={handleIncrementGeneration}
          disabled={isIncrementing}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 rounded-lg font-medium flex items-center gap-2 transition-colors"
        >
          <Plus className="h-4 w-4" />
          {isIncrementing ? 'Incrementando...' : 'Incrementar Geração'}
        </button>
      </div>

      <div className="flex space-x-2 mb-6">
        <button
          className={`flex-1 py-3 rounded-lg flex items-center justify-center gap-2 font-medium transition-colors ${
            activeTab === 'structural'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
          onClick={() => setActiveTab('structural')}
        >
          <Cpu className="h-5 w-5" />
          Estrutural
        </button>
        <button
          className={`flex-1 py-3 rounded-lg flex items-center justify-center gap-2 font-medium transition-colors ${
            activeTab === 'brain'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
          onClick={() => setActiveTab('brain')}
        >
          <Brain className="h-5 w-5" />
          Cerebral
        </button>
      </div>

      {activeTab === 'structural' ? (
        <>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-400 mb-2">Tipo de Mutação</label>
              <select
                value={evolutionType}
                onChange={(e) => setEvolutionType(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {MUTATION_TYPES.map(type => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-gray-400">Intensidade</label>
                <span className="text-blue-400 font-medium">{intensity.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={intensity}
                onChange={(e) => setIntensity(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-500"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Baixa</span>
                <span>Média</span>
                <span>Alta</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleStructuralEvolution}
            disabled={isEvolvingStructure}
            className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
          >
            <Zap className="h-5 w-5" />
            {isEvolvingStructure ? 'Executando Mutação...' : 'Executar Mutação Estrutural'}
          </button>
        </>
      ) : (
        <>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-400 mb-2">Tipo de Evolução</label>
              <select
                value={evolutionType}
                onChange={(e) => setEvolutionType(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {EVOLUTION_TYPES.map(type => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-gray-400">Intensidade</label>
                <span className="text-purple-400 font-medium">{intensity.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={intensity}
                onChange={(e) => setIntensity(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-purple-500"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Baixa</span>
                <span>Média</span>
                <span>Alta</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleBrainEvolution}
            disabled={isEvolvingBrain}
            className="w-full mt-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
          >
            <Brain className="h-5 w-5" />
            {isEvolvingBrain ? 'Executando Evolução...' : 'Executar Evolução Cerebral'}
          </button>
        </>
      )}

      <div className="mt-6 pt-6 border-t border-gray-800">
        <p className="text-gray-400 text-sm">
          <strong>Nota:</strong> As evoluções são processadas em tempo real. 
          O sistema biomimético aprenderá com cada execução.
        </p>
      </div>
    </div>
  );
}