#!/usr/bin/env python3
"""
IA Autoevolutiva Avançada com Metalearning
Sistema que aprende, evolui e busca conhecimento dinamicamente
"""

import sqlite3
import json
import os
import re
import threading
import time
from datetime import datetime
import requests
from urllib.parse import quote
import wikipedia
import asyncio
import aiohttp

class MetalearningAgent:
    """Agente com capacidade de metalearning e evolução"""
    
    def __init__(self, agent_name, specialization):
        self.name = agent_name
        self.specialization = specialization
        self.knowledge_base = []
        self.learning_patterns = []
        self.evolution_history = []
        self.collaboration_network = {}
        
    def learn_from_response(self, question, response, feedback=None):
        """Metalearning: aprende com suas próprias respostas"""
        learning_entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response,
            'feedback': feedback,
            'success_rate': 1.0 if feedback == 'positive' else 0.0
        }
        self.learning_patterns.append(learning_entry)
        
        # Evoluir baseado no feedback
        if feedback == 'negative':
            self.evolve_strategy(question, response)
    
    def evolve_strategy(self, question, response):
        """Evoluir estratégia de resposta baseada no feedback"""
        evolution_entry = {
            'timestamp': datetime.now().isoformat(),
            'trigger': 'negative_feedback',
            'question_type': self.analyze_question_type(question),
            'improvement_strategy': self.generate_improvement_strategy(question),
            'previous_response': response
        }
        self.evolution_history.append(evolution_entry)
    
    def analyze_question_type(self, question):
        """Analisar tipo de pergunta para melhorar respostas futuras"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['o que é', 'defina', 'explique']):
            return 'definition'
        elif any(word in question_lower for word in ['como', 'procedimento', 'passo']):
            return 'procedure'
        elif any(word in question_lower for word in ['quando', 'prazo', 'tempo']):
            return 'timing'
        elif any(word in question_lower for word in ['por que', 'motivo', 'causa']):
            return 'reasoning'
        else:
            return 'general'
    
    def generate_improvement_strategy(self, question):
        """Gerar estratégia de melhoria baseada no tipo de pergunta"""
        question_type = self.analyze_question_type(question)
        
        strategies = {
            'definition': 'Buscar definições mais precisas e exemplos práticos',
            'procedure': 'Incluir passos detalhados e considerações importantes',
            'timing': 'Especificar prazos e condições temporais',
            'reasoning': 'Explicar causas, consequências e contexto',
            'general': 'Estruturar resposta com introdução, desenvolvimento e conclusão'
        }
        
        return strategies.get(question_type, 'Melhorar clareza e precisão da resposta')

class InternetSearchAgent:
    """Agente especializado em busca de informações na internet"""
    
    def __init__(self):
        self.search_history = []
        self.trusted_sources = [
            'wikipedia.org',
            'gov.br',
            'stf.jus.br',
            'tst.jus.br',
            'senado.leg.br',
            'camara.leg.br'
        ]
    
    async def search_internet(self, query, max_results=3):
        """Buscar informações na internet de forma assíncrona"""
        try:
            # Busca no Google (simulada)
            search_results = await self.google_search(query)
            
            # Busca na Wikipedia
            wiki_results = await self.wikipedia_search(query)
            
            # Combinar resultados
            all_results = search_results + wiki_results
            
            # Filtrar por fontes confiáveis
            filtered_results = self.filter_trusted_sources(all_results)
            
            return filtered_results[:max_results]
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    async def google_search(self, query):
        """Simular busca no Google"""
        # Em produção, usar API do Google Search
        return [
            {
                'title': f'Resultado para: {query}',
                'snippet': f'Informações relevantes sobre {query}',
                'url': f'https://example.com/search?q={quote(query)}',
                'source': 'google'
            }
        ]
    
    async def wikipedia_search(self, query):
        """Buscar na Wikipedia"""
        try:
            # Buscar páginas relacionadas
            search_results = wikipedia.search(query, results=3)
            wiki_results = []
            
            for title in search_results:
                try:
                    page = wikipedia.page(title)
                    wiki_results.append({
                        'title': page.title,
                        'snippet': page.summary[:300] + '...',
                        'url': page.url,
                        'source': 'wikipedia'
                    })
                except:
                    continue
            
            return wiki_results
            
        except Exception as e:
            print(f"Erro na Wikipedia: {e}")
            return []
    
    def filter_trusted_sources(self, results):
        """Filtrar resultados por fontes confiáveis"""
        filtered = []
        for result in results:
            if any(source in result.get('url', '') for source in self.trusted_sources):
                filtered.append(result)
        return filtered

class CollaborativeAgentSystem:
    """Sistema de agentes colaborativos com metalearning"""
    
    def __init__(self):
        self.agents = {
            'maestro': MetalearningAgent('Maestro', 'Coordenação e Orquestração'),
            'legal': MetalearningAgent('Legal', 'Conformidade Legal'),
            'financial': MetalearningAgent('Financial', 'Análise Financeira'),
            'jurist': MetalearningAgent('Jurist', 'Interpretação Jurídica'),
            'contract': MetalearningAgent('Contract', 'Gestão de Contratos'),
            'reviewer': MetalearningAgent('Reviewer', 'Revisão e Validação'),
            'skeptic': MetalearningAgent('Skeptic', 'Validação Crítica')
        }
        
        self.internet_agent = InternetSearchAgent()
        self.collaboration_history = []
        
    async def process_question_advanced(self, question):
        """Processar pergunta usando metalearning e colaboração"""
        
        # 1. Análise inicial da pergunta
        question_analysis = self.analyze_question(question)
        
        # 2. Seleção do agente principal
        primary_agent = self.select_best_agent(question_analysis)
        
        # 3. Busca de conhecimento local
        local_knowledge = self.get_local_knowledge(primary_agent.name)
        
        # 4. Busca na internet (se necessário)
        internet_knowledge = []
        if self.needs_internet_search(question_analysis):
            internet_knowledge = await self.internet_agent.search_internet(question)
        
        # 5. Colaboração entre agentes
        collaborative_knowledge = self.collaborate_with_agents(question, primary_agent)
        
        # 6. Síntese da resposta
        response = self.synthesize_response(
            question, 
            local_knowledge, 
            internet_knowledge, 
            collaborative_knowledge,
            primary_agent
        )
        
        # 7. Metalearning - aprender com a resposta
        self.learn_from_interaction(question, response, primary_agent)
        
        return response
    
    def analyze_question(self, question):
        """Análise avançada da pergunta"""
        question_lower = question.lower()
        
        analysis = {
            'complexity': self.assess_complexity(question),
            'domain': self.identify_domain(question_lower),
            'requires_internet': self.needs_internet_search({'question': question}),
            'collaboration_needed': self.needs_collaboration(question_lower),
            'keywords': self.extract_keywords(question_lower)
        }
        
        return analysis
    
    def assess_complexity(self, question):
        """Avaliar complexidade da pergunta"""
        word_count = len(question.split())
        if word_count < 5:
            return 'simple'
        elif word_count < 15:
            return 'moderate'
        else:
            return 'complex'
    
    def identify_domain(self, question):
        """Identificar domínio da pergunta"""
        domains = {
            'legal': ['lei', 'legal', 'jurídico', 'direito', 'artigo', 'código'],
            'financial': ['financeiro', 'econômico', 'dinheiro', 'custo', 'orçamento'],
            'contract': ['contrato', 'cláusula', 'obrigação', 'vigência'],
            'technical': ['técnico', 'tecnologia', 'sistema', 'processo'],
            'general': []
        }
        
        for domain, keywords in domains.items():
            if any(keyword in question for keyword in keywords):
                return domain
        
        return 'general'
    
    def needs_internet_search(self, analysis):
        """Determinar se precisa buscar na internet"""
        question = analysis.get('question', '')
        question_lower = question.lower()
        
        # Buscar na internet se:
        # - Pergunta sobre fatos recentes
        # - Informações específicas não encontradas localmente
        # - Pergunta sobre legislação atualizada
        
        recent_keywords = ['recente', 'atual', 'hoje', '2024', '2025', 'novo', 'atualizado']
        if any(keyword in question_lower for keyword in recent_keywords):
            return True
        
        return False
    
    def needs_collaboration(self, question):
        """Determinar se precisa de colaboração entre agentes"""
        # Colaboração necessária para perguntas complexas ou multidisciplinares
        complex_keywords = ['relacionado', 'conexão', 'impacto', 'consequência', 'análise completa']
        return any(keyword in question for keyword in complex_keywords)
    
    def extract_keywords(self, question):
        """Extrair palavras-chave da pergunta"""
        # Remover palavras comuns
        stop_words = ['o', 'a', 'os', 'as', 'um', 'uma', 'e', 'ou', 'de', 'da', 'do', 'em', 'com', 'para', 'por', 'que', 'como', 'quando', 'onde', 'quem', 'qual', 'quais']
        
        words = question.split()
        keywords = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        return keywords
    
    def select_best_agent(self, analysis):
        """Selecionar melhor agente baseado na análise"""
        domain = analysis['domain']
        
        agent_mapping = {
            'legal': self.agents['legal'],
            'financial': self.agents['financial'],
            'contract': self.agents['contract'],
            'technical': self.agents['reviewer'],
            'general': self.agents['maestro']
        }
        
        return agent_mapping.get(domain, self.agents['maestro'])
    
    def get_local_knowledge(self, agent_name):
        """Obter conhecimento local do agente"""
        # Implementar busca no banco de dados local
        db_path = f"agents/{agent_name.lower()}/memory.db"
        knowledge = []
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if 'learned_facts' in tables:
                    cursor.execute("SELECT fact_content FROM learned_facts LIMIT 20")
                    facts = cursor.fetchall()
                    
                    for fact in facts:
                        if fact[0] and len(fact[0].strip()) > 20:
                            fact_text = fact[0].strip()
                            
                            # Processar dados em formato Python dict
                            if fact_text.startswith('{') and fact_text.endswith('}'):
                                try:
                                    dict_data = eval(fact_text)
                                    if 'content' in dict_data:
                                        content = dict_data['content']
                                        if isinstance(content, str) and len(content) > 20:
                                            knowledge.append(content)
                                except:
                                    pass
                
                conn.close()
                
            except Exception as e:
                print(f"Erro ao ler banco {agent_name}: {e}")
        
        return knowledge
    
    def collaborate_with_agents(self, question, primary_agent):
        """Colaboração entre agentes"""
        collaboration_results = []
        
        # Se a pergunta precisa de colaboração, consultar outros agentes
        if self.needs_collaboration(question.lower()):
            for agent_name, agent in self.agents.items():
                if agent != primary_agent:
                    # Obter conhecimento complementar
                    complementary_knowledge = self.get_local_knowledge(agent_name)
                    if complementary_knowledge:
                        collaboration_results.append({
                            'agent': agent_name,
                            'knowledge': complementary_knowledge[:2]  # Top 2 fatos
                        })
        
        return collaboration_results
    
    def synthesize_response(self, question, local_knowledge, internet_knowledge, collaborative_knowledge, primary_agent):
        """Sintetizar resposta final"""
        
        response = f"🤖 **Resposta do {primary_agent.name}:**\n\n"
        response += f"**Especialização:** {primary_agent.specialization}\n\n"
        response += f"**Pergunta:** {question}\n\n"
        
        # Conhecimento local
        if local_knowledge:
            response += "**Conhecimento Local:**\n\n"
            for i, knowledge in enumerate(local_knowledge[:2], 1):
                clean_knowledge = knowledge.strip()
                if len(clean_knowledge) > 200:
                    clean_knowledge = clean_knowledge[:200] + "..."
                response += f"{i}. {clean_knowledge}\n\n"
        
        # Conhecimento da internet
        if internet_knowledge:
            response += "**Informações da Internet:**\n\n"
            for i, result in enumerate(internet_knowledge, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet']}\n"
                response += f"   Fonte: {result['source']}\n\n"
        
        # Colaboração entre agentes
        if collaborative_knowledge:
            response += "**Colaboração entre Agentes:**\n\n"
            for collab in collaborative_knowledge:
                response += f"**{collab['agent'].title()}:**\n"
                for knowledge in collab['knowledge']:
                    clean_knowledge = knowledge.strip()
                    if len(clean_knowledge) > 150:
                        clean_knowledge = clean_knowledge[:150] + "..."
                    response += f"• {clean_knowledge}\n"
                response += "\n"
        
        # Metalearning info
        response += f"**Evolução do Sistema:**\n"
        response += f"• Agente principal: {primary_agent.name}\n"
        response += f"• Padrões aprendidos: {len(primary_agent.learning_patterns)}\n"
        response += f"• Evoluções: {len(primary_agent.evolution_history)}\n"
        response += f"• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return response
    
    def learn_from_interaction(self, question, response, agent):
        """Aprender com a interação"""
        # Registrar interação para metalearning
        agent.learn_from_response(question, response)
        
        # Registrar colaboração
        collaboration_entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'primary_agent': agent.name,
            'response_length': len(response),
            'complexity': self.assess_complexity(question)
        }
        self.collaboration_history.append(collaboration_entry)

# Sistema principal
class AdvancedAISystem:
    """Sistema de IA Autoevolutiva Avançada"""
    
    def __init__(self):
        self.collaborative_system = CollaborativeAgentSystem()
        self.evolution_counter = 0
        
    async def ask_question(self, question):
        """Fazer pergunta ao sistema avançado"""
        print(f"🧠 Processando pergunta: {question}")
        print("🔄 Usando metalearning e colaboração entre agentes...")
        
        try:
            response = await self.collaborative_system.process_question_advanced(question)
            self.evolution_counter += 1
            
            print(f"✅ Resposta gerada (evolução #{self.evolution_counter})")
            return response
            
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            return f"❌ Erro no processamento da pergunta: {str(e)}"

def main():
    """Função principal"""
    print("🚀 INICIANDO IA AUTOEVOLUTIVA AVANÇADA")
    print("=" * 60)
    print("🧠 Metalearning ativo")
    print("🌐 Busca na internet habilitada")
    print("🤝 Colaboração entre agentes")
    print("📈 Evolução contínua")
    print("=" * 60)
    
    # Criar sistema
    ai_system = AdvancedAISystem()
    
    # Exemplo de uso
    async def test_system():
        questions = [
            "O que é contrato de trabalho?",
            "Como funciona o fato superveniente em contratos?",
            "Quais são as principais mudanças na legislação trabalhista em 2024?"
        ]
        
        for question in questions:
            print(f"\n{'='*50}")
            print(f"❓ PERGUNTA: {question}")
            print(f"{'='*50}")
            
            response = await ai_system.ask_question(question)
            print(response)
            
            # Aguardar um pouco entre perguntas
            await asyncio.sleep(2)
    
    # Executar teste
    asyncio.run(test_system())

if __name__ == "__main__":
    main() 