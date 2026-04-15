# Evolution Dashboard - Frontend

Dashboard interativo em TypeScript para monitoramento e controle do Sistema Evolutivo Biomimético.

## 🚀 Funcionalidades

- **📊 Dashboard em tempo real**: Monitoramento completo do sistema evolutivo
- **⚡ Controles de evolução**: Interface para executar mutações estruturais e evoluções cerebrais
- **📈 Visualização de métricas**: Gráficos e estatísticas evolutivas
- **🔔 Sistema de alertas**: Notificações em tempo real sobre atividades do sistema
- **🔄 Atualização automática**: Polling automático para dados em tempo real
- **🎨 Design responsivo**: Interface moderna com Tailwind CSS

## 🏗️ Arquitetura

### Stack Tecnológica
- **Next.js 14** (App Router)
- **React 18** com TypeScript
- **Tailwind CSS** para estilização
- **TanStack Query** para gerenciamento de estado e cache
- **Axios** para chamadas HTTP
- **Recharts** para visualização de dados
- **Lucide React** para ícones

### Estrutura de Pastas
```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página principal (Dashboard)
│   ├── globals.css        # Estilos globais
│   └── providers.tsx      # Providers (React Query)
├── components/            # Componentes React
│   ├── dashboard/         # Componentes do dashboard
│   ├── evolution/         # Controles de evolução
│   └── ui/               # Componentes de UI reutilizáveis
├── lib/api/              # Cliente API e tipos TypeScript
│   ├── types.ts          # Tipos TypeScript para a API
│   ├── client.ts         # Cliente HTTP com Axios
│   └── hooks.ts          # Hooks React Query customizados
└── public/               # Assets estáticos
```

## 🔧 Configuração Rápida

### Pré-requisitos
- Node.js 18+ e npm/yarn
- Sistema Evolution API rodando em `http://localhost:8000`

### Instalação

1. **Instalar dependências:**
```bash
npm install
# ou
yarn install
```

2. **Configurar variáveis de ambiente:**
Crie um arquivo `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Iniciar servidor de desenvolvimento:**
```bash
npm run dev
# ou
yarn dev
```

4. **Acessar o dashboard:**
Abrir `http://localhost:3000` no navegador

## 🔌 Integração com a API

O frontend consome os seguintes endpoints da API Evolution:

### Endpoints Principais
- `GET /health` - Health check do sistema
- `GET /status` - Status do sistema e componentes
- `GET /dashboard` - Dados completos do dashboard
- `GET /history` - Histórico de evoluções
- `POST /evolve/structure` - Executar mutação estrutural
- `POST /evolve/brain` - Executar evolução cerebral
- `POST /generation/increment` - Incrementar geração

### Configuração de CORS
O Next.js está configurado com rewrites e headers CORS para comunicação com a API local.

## 🎨 Componentes Principais

### 1. EvolutionDashboard (`app/page.tsx`)
Página principal com:
- Cards de status do sistema
- Grid de métricas evolutivas
- Atividade recente
- Controles de evolução

### 2. EvolutionControls (`components/evolution/EvolutionControls.tsx`)
Interface para:
- Selecionar tipo de mutação/evolução
- Ajustar intensidade (slider 0-1)
- Executar evoluções estruturais e cerebrais
- Incrementar geração manualmente

### 3. ActivityFeed (`components/dashboard/ActivityFeed.tsx`)
Feed de atividades com:
- Lista de mutações recentes
- Evoluções cerebrais executadas
- Alertas do sistema
- Filtros por tipo de atividade

### 4. StatusCard (`components/ui/StatusCard.tsx`)
Card reutilizável para métricas:
- Ícone personalizado
- Valor principal
- Subtítulo
- Indicador de tendência
- Cores por status

## 📡 Sistema de Atualização Automática

O dashboard utiliza **TanStack Query** para:
- **Polling automático**: Atualização periódica dos dados
- **Cache inteligente**: Evita requisições desnecessárias
- **Otimistic updates**: Atualização imediata da UI após mutações
- **Retry automático**: Reconexão em caso de falhas de rede

**Intervalos de atualização:**
- Status do sistema: 5 segundos
- Dashboard: 10 segundos
- Conexão API: 30 segundos

## 🛠️ Desenvolvimento

### Comandos Disponíveis
```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Executar build de produção
npm run start

# Lint do código
npm run lint

# TypeScript check
npx tsc --noEmit
```

### Adicionando Novos Componentes
1. Crie o componente em `components/`
2. Exporte tipos em `lib/api/types.ts` se necessário
3. Crie hooks customizados em `lib/api/hooks.ts`
4. Importe no `app/page.tsx`

## 🔒 Segurança

- **CORS configurado**: Apenas origens permitidas
- **Sanitização de dados**: Todos os inputs são validados
- **Error boundaries**: Tratamento de erros em componentes
- **Rate limiting**: Implementado no lado da API

## 📱 Responsividade

O dashboard é totalmente responsivo:
- **Mobile**: Layout de coluna única
- **Tablet**: Grid de 2 colunas
- **Desktop**: Grid de 3-4 colunas

## 🚀 Deploy

### Deploy na Vercel (Recomendado)
```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Deploy com Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -am 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 🔗 Links

- **Documentação da API**: `http://localhost:8000/docs`
- **Repositório do Sistema**: [AI-Biomimetica](https://github.com/Adjalma/AI-Biomimetica)
- **Dashboard Online**: (Configurar após deploy)

---

**🎉 Pronto para evolução!** O dashboard está configurado para monitorar e controlar o sistema evolutivo biomimético em tempo real.