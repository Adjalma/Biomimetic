# 🚀 Dashboard IA Autoevolutiva V2

## 📋 **Visão Geral**

Dashboard web completo para testar e monitorar a IA Autoevolutiva V2 com Sistemas V2 integrados ao FAISS. Permite fazer perguntas, testar sistemas, monitorar evolução e controlar populações em tempo real.

## ✨ **Funcionalidades Principais**

### 🔍 **Chat com IA V2**
- **Perguntas e respostas** em tempo real
- **Interface conversacional** intuitiva
- **Processamento** baseado em 16M vetores FAISS
- **Integração** com Sistemas V2

### ⚙️ **Teste dos Sistemas V2**
- **Guardião do Conhecimento** - Detecção de contradições e obsolescência
- **Simulador Contrafactual** - Análise de cenários hipotéticos
- **Gerador de Procedimentos** - Otimização de processos
- **Academia de Agentes** - Treinamento e simulação

### 📊 **Monitoramento em Tempo Real**
- **Status das populações** evolutivas
- **Métricas de fitness** e performance
- **Contador de vetores** FAISS (16M+)
- **Gráficos** de evolução interativos

### 🧬 **Controle de Evolução**
- **Iniciar/parar** processo evolutivo
- **Configurar** número de gerações
- **Monitorar** progresso em tempo real
- **Visualizar** histórico de evolução

## 🛠️ **Arquitetura Técnica**

### **Backend**
- **Flask** - Framework web Python
- **Socket.IO** - Comunicação em tempo real
- **Threading** - Execução assíncrona de evolução
- **REST API** - Endpoints para todas as funcionalidades

### **Frontend**
- **HTML5 + CSS3** - Interface responsiva
- **Bootstrap 5** - Design moderno e mobile-friendly
- **Chart.js** - Gráficos interativos
- **JavaScript ES6** - Lógica de interface

### **Integração**
- **MainAI** - Sistema principal da IA
- **Sistemas V2** - Módulos especializados
- **FAISS** - Base de conhecimento unificada
- **WebSocket** - Atualizações em tempo real

## 🚀 **Como Usar**

### **1. Instalação**
```bash
# Instalar dependências
pip install -r requirements_dashboard.txt

# Ou usar o script automático (Windows)
iniciar_dashboard.bat
```

### **2. Execução**
```bash
python dashboard_ia_v2.py
```

### **3. Acesso**
- **URL**: http://localhost:5000
- **Porta padrão**: 5000
- **Host**: 0.0.0.0 (acessível externamente)

## 📱 **Interface do Usuário**

### **Layout Responsivo**
- **Desktop**: Layout completo com todas as funcionalidades
- **Tablet**: Adaptação para telas médias
- **Mobile**: Interface otimizada para dispositivos móveis

### **Seções Principais**
1. **Header** - Título e informações do sistema
2. **Chat com IA** - Interface conversacional
3. **Teste Sistemas V2** - Botões para testar cada sistema
4. **Status do Sistema** - Métricas em tempo real
5. **Controle de Evolução** - Botões de controle
6. **Gráfico de Evolução** - Histórico visual

## 🔌 **APIs Disponíveis**

### **Status e Monitoramento**
- `GET /api/status` - Status completo do sistema
- `GET /api/faiss/status` - Status do FAISS unificado

### **Interação com IA**
- `POST /api/pergunta` - Fazer pergunta à IA
- `GET /api/sistemas_v2/teste` - Testar todos os Sistemas V2

### **Controle de Evolução**
- `POST /api/evolucao/iniciar` - Iniciar processo evolutivo
- `POST /api/evolucao/parar` - Parar processo evolutivo

## 📊 **Métricas Monitoradas**

### **Sistema Principal**
- **Tamanho da população**: Número de indivíduos ativos
- **Melhor fitness**: Performance do melhor indivíduo
- **Geração atual**: Número da geração em execução
- **Histórico**: Evolução ao longo do tempo

### **FAISS Unificado**
- **Total de vetores**: 16.954.043 vetores
- **Por agente**: Distribuição por especialista
- **Tipo de índice**: IVFFlat otimizado
- **Última atualização**: Timestamp da última modificação

### **Sistemas V2**
- **Status online/offline** de cada sistema
- **Performance** de cada módulo
- **Integração** com FAISS
- **Logs** de operação

## 🎯 **Casos de Uso**

### **Para Desenvolvedores**
- **Testar** funcionalidades dos Sistemas V2
- **Monitorar** performance da IA
- **Debuggar** problemas de evolução
- **Validar** integrações

### **Para Usuários Finais**
- **Fazer perguntas** sobre contratos
- **Analisar** cenários hipotéticos
- **Obter** procedimentos otimizados
- **Monitorar** evolução do sistema

### **Para Stakeholders**
- **Visualizar** capacidades da IA
- **Acompanhar** progresso evolutivo
- **Validar** investimentos em IA
- **Demonstrar** valor agregado

## 🔧 **Configuração Avançada**

### **Variáveis de Ambiente**
```bash
# Porta do servidor
export DASHBOARD_PORT=5000

# Host de acesso
export DASHBOARD_HOST=0.0.0.0

# Modo debug
export DASHBOARD_DEBUG=true
```

### **Personalização**
- **Cores**: Modificar variáveis CSS no template
- **Layout**: Ajustar Bootstrap classes
- **Funcionalidades**: Adicionar novos endpoints
- **Integrações**: Conectar com sistemas externos

## 🚨 **Troubleshooting**

### **Problemas Comuns**

#### **1. Erro de Importação**
```bash
# Solução: Instalar dependências
pip install -r requirements_dashboard.txt
```

#### **2. Porta em Uso**
```bash
# Solução: Mudar porta no código
dashboard.run(port=5001)
```

#### **3. IA não Inicializa**
```bash
# Verificar logs do sistema
# Confirmar que main.py está funcionando
```

#### **4. WebSocket não Conecta**
```bash
# Verificar firewall
# Confirmar que Socket.IO está funcionando
```

### **Logs e Debug**
- **Console**: Logs em tempo real
- **Arquivo**: Logs salvos automaticamente
- **WebSocket**: Debug de conexões
- **API**: Respostas de erro detalhadas

## 🔮 **Roadmap Futuro**

### **Versão 2.1**
- **Autenticação** de usuários
- **Múltiplas sessões** simultâneas
- **Exportação** de dados
- **Notificações** push

### **Versão 2.2**
- **Dashboard mobile** nativo
- **Integração** com banco de contratos
- **Análise** avançada de performance
- **Machine Learning** de interface

### **Versão 3.0**
- **IA conversacional** avançada
- **Visualização 3D** de evolução
- **Colaboração** em tempo real
- **APIs públicas** para integração

## 📞 **Suporte**

### **Documentação**
- **README**: Este arquivo
- **Código**: Comentários inline
- **Logs**: Sistema de logging integrado

### **Contato**
- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions
- **Wiki**: Documentação expandida

---

## 🎉 **Conclusão**

O Dashboard IA Autoevolutiva V2 representa um marco na democratização do acesso à IA avançada. Com interface intuitiva, funcionalidades poderosas e integração completa com os Sistemas V2, permite que usuários de todos os níveis técnicos interajam com uma das IAs mais avançadas do mundo.

**🚀 Prepare-se para testar o futuro da IA!**
