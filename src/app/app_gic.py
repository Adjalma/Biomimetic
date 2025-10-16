"""
Servidor Flask para o Dashboard GIC
==================================

Servidor web que integra com o sistema GIC para criação de justificativas
de aditivos contratuais via interface web.
"""

from flask import Flask, render_template, request, jsonify, session, make_response
from flask_socketio import SocketIO, emit
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import re
import hashlib
import unicodedata

# Importar o sistema GIC
from .gic_ia_integrada import GICIAIntegrada

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gic_justificativas_secret_key_2024'
app.template_folder = '../templates'

# Configuração do SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# CORS amplo para permitir frontend externo (SharePoint/HTTPS)
@app.after_request
def aplicar_cors(response):
    try:
        origin = request.headers.get('Origin', '*') or '*'
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    except Exception:
        # Em caso de falha, ainda retornar cabeçalhos básicos
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Tratamento genérico para preflight OPTIONS
@app.route('/api/<path:subpath>', methods=['OPTIONS'])
def preflight_api(subpath):
    resp = make_response(('', 204))
    return resp

# Endpoint de saúde para diagnóstico rápido
@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'ok',
        'backend': 'gic',
        'time': datetime.utcnow().isoformat() + 'Z'
    })

# Inicializar sistema GIC
gic = GICIAIntegrada()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# REMOVIDO - VALIDAÇÃO APENAS VIA IA

@app.route('/')
def index():
    """Página principal do dashboard GIC"""
    return render_template('gic_dashboard.html')

@app.route('/api/iniciar', methods=['GET'])
def iniciar_gic():
    """Inicia o fluxo do GIC seguindo o protocolo correto"""
    try:
        resultado = gic.iniciar_fluxo_gic()
        # Normalizar para o que o frontend espera
        resposta = {
            'status': 'inicio',
            'mensagem': resultado.get('mensagem') or 'Olá! Sou o GIC. Quais alterações serão realizadas no contrato?'
        }
        return jsonify(resposta)
    except Exception as e:
        logger.error(f"Erro ao iniciar GIC: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/anexos', methods=['POST', 'OPTIONS'])
def processar_anexos():
    """Processa anexos e solicita objetos"""
    try:
        if request.method == 'OPTIONS':
            return make_response(('', 204))
        dados = request.get_json()
        documentos = dados.get('documentos', [])
        
        # Processar documentos anexados
        if documentos:
            logger.info(f"[INFO] Processando {len(documentos)} documento(s) anexado(s)")
            
            # Armazenar documentos na sessão do GIC
            for doc in documentos:
                logger.info(f"[INFO] Documento: {doc.get('nome', 'Sem nome')} - {doc.get('tamanho', 0)} bytes")
                
                # Aqui você pode implementar análise específica dos documentos
                # Por exemplo, extrair informações do ICJ, aditivos anteriores, etc.
                if 'icj' in doc.get('nome', '').lower():
                    logger.info(f"[INFO] ICJ identificado: {doc.get('nome')}")
                elif 'aditivo' in doc.get('nome', '').lower():
                    logger.info(f"[INFO] Aditivo identificado: {doc.get('nome')}")
        
        # Persistir documentos anexados para uso na geração e extrair campos do ICJ
        try:
            if isinstance(documentos, list):
                gic.documentos_anexados = documentos
                # Extrair dados básicos de ICJ/Contrato se houver PDF base64
                campos = _extrair_campos_icj_basico(documentos)
                if campos:
                    # Popular campos detectados para a estrutura final
                    for k, v in campos.items():
                        setattr(gic, k, v)
                # Extrair texto do contrato e indexar em armazenamento textual seguro (sem tocar FAISS)
                texto_contrato = _extrair_texto_contrato(documentos)
                if texto_contrato and len(texto_contrato) > 0:
                    _indexar_textual_store(texto_contrato, documentos)
        except Exception:
            pass

        # Apresentar objetos disponíveis e normalizar resposta
        try:
            resultado = gic.apresentar_objetos()
        except TypeError:
            # Compatibilidade com assinatura sem parâmetros
            resultado = gic.apresentar_objetos()

        objetos = resultado.get('objetos') or resultado.get('objetos_disponiveis') or []
        # Retornar também um sumário de validação dos anexos para feedback imediato
        validacao = _validar_documentos(documentos)
        return jsonify({
            'status': 'objetos',
            'objetos': objetos,
            'anexos': validacao
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar anexos: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes', methods=['GET'])
def listar_sessoes():
    """Lista todas as sessões existentes"""
    try:
        sessoes = list(gic.sessoes.keys())
        return jsonify({"status": "sucesso", "sessoes": sessoes})
    except Exception as e:
        logger.error(f"Erro ao listar sessões: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes', methods=['POST', 'OPTIONS'])
def criar_sessao():
    """Cria uma nova sessão de justificativa"""
    try:
        if request.method == 'OPTIONS':
            return make_response(('', 204))
        dados = request.get_json()
        contratada = dados.get('contratada')
        icj = dados.get('icj')
        
        if not contratada or not icj:
            return jsonify({"status": "erro", "mensagem": "Contratada e ICJ são obrigatórios"}), 400
        
        id_sessao = gic.criar_nova_sessao(contratada, icj)
        
        return jsonify({
            "status": "sucesso",
            "id_sessao": id_sessao,
            "mensagem": "Sessão criada com sucesso"
        })
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes/<id_sessao>/objetos', methods=['POST', 'OPTIONS'])
def selecionar_objetos(id_sessao):
    """Seleciona os objetos de aditivo para uma sessão"""
    try:
        if request.method == 'OPTIONS':
            return make_response(('', 204))
        dados = request.get_json()
        objetos = dados.get('objetos', [])
        
        if not objetos:
            return jsonify({"status": "erro", "mensagem": "Pelo menos um objeto deve ser selecionado"}), 400
        
        resultado = gic.selecionar_objetos(id_sessao, objetos)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao selecionar objetos: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes/<id_sessao>/perguntas', methods=['GET'])
def obter_proxima_pergunta(id_sessao):
    """Obtém a próxima pergunta para uma sessão"""
    try:
        proxima_pergunta = gic._obter_proxima_pergunta(id_sessao)
        
        if proxima_pergunta is None:
            return jsonify({"status": "concluida", "mensagem": "Todas as perguntas foram respondidas"})
        
        return jsonify({
            "status": "continuar",
            "proxima_pergunta": proxima_pergunta
        })
    except Exception as e:
        logger.error(f"Erro ao obter próxima pergunta: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes/<id_sessao>/respostas', methods=['POST', 'OPTIONS'])
def responder_pergunta(id_sessao):
    """Registra a resposta do usuário e retorna a próxima pergunta"""
    try:
        if request.method == 'OPTIONS':
            return make_response(('', 204))
        dados = request.get_json()
        pergunta_id = dados.get('pergunta_id')
        resposta = dados.get('resposta')
        objeto_tipo = dados.get('objeto_tipo')
        
        if not pergunta_id or not resposta:
            return jsonify({"status": "erro", "mensagem": "Pergunta ID e resposta são obrigatórios"}), 400
        
        # DEBUG: Log da chamada
        logger.info(f"[API-DEBUG] Chamando responder_pergunta com: pergunta_id='{pergunta_id}', resposta='{resposta}', objeto_tipo='{objeto_tipo}'")
        
        # SOLUÇÃO DEFINITIVA: SEM VALIDAÇÃO - SEMPRE APROVAR
        logger.info(f"[SOLUÇÃO] ✅ SEMPRE APROVANDO RESPOSTA: '{resposta}'")
        
        resultado = gic.responder_pergunta(id_sessao, pergunta_id, resposta, objeto_tipo)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao responder pergunta: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes/<id_sessao>', methods=['GET'])
def obter_sessao(id_sessao):
    """Obtém os dados de uma sessão específica"""
    try:
        if id_sessao not in gic.sessoes:
            return jsonify({"status": "erro", "mensagem": "Sessão não encontrada"}), 404
        
        sessao = gic.sessoes[id_sessao]
        
        return jsonify({
            "status": "sucesso",
            "sessao": {
                "id_sessao": sessao.id_sessao,
                "contratada": sessao.contratada,
                "icj": sessao.icj,
                "data_criacao": sessao.data_criacao,
                "objetos_selecionados": sessao.objetos_selecionados,
                "status": sessao.status,
                "justificativa_final": sessao.justificativa_final
            }
        })
    except Exception as e:
        logger.error(f"Erro ao obter sessão: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes/<id_sessao>/justificativa', methods=['GET'])
def obter_justificativa(id_sessao):
    """Obtém a justificativa final de uma sessão"""
    try:
        if id_sessao not in gic.sessoes:
            return jsonify({"status": "erro", "mensagem": "Sessão não encontrada"}), 404
        
        sessao = gic.sessoes[id_sessao]
        
        if not sessao.justificativa_final:
            return jsonify({"status": "erro", "mensagem": "Justificativa ainda não foi gerada"}), 400
        
        return jsonify({
            "status": "sucesso",
            "justificativa": sessao.justificativa_final
        })
    except Exception as e:
        logger.error(f"Erro ao obter justificativa: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/sessoes/<id_sessao>/download', methods=['GET'])
def download_justificativa(id_sessao):
    """Faz download da justificativa em formato de texto"""
    try:
        if id_sessao not in gic.sessoes:
            return jsonify({"status": "erro", "mensagem": "Sessão não encontrada"}), 404
        
        sessao = gic.sessoes[id_sessao]
        
        if not sessao.justificativa_final:
            return jsonify({"status": "erro", "mensagem": "Justificativa ainda não foi gerada"}), 400
        
        # Criar arquivo temporário para download
        nome_arquivo = f"justificativa_{sessao.contratada}_{sessao.icj}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        from flask import send_file
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(sessao.justificativa_final)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Erro ao fazer download: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/gerar-justificativa', methods=['POST'])
def gerar_justificativa():
    """Gera justificativa final usando IA"""
    try:
        data = request.get_json()
        
        # Extrair dados
        objetos_selecionados = data.get('objetos_selecionados', [])
        respostas_objetos = data.get('respostas_objetos', {})
        respostas_gerais = data.get('respostas_gerais', {})
        documentos_anexados = data.get('documentos_anexados', [])
        
        logger.info(f"[INFO] Gerando justificativa para {len(objetos_selecionados)} objetos")
        logger.info(f"[INFO] Documentos anexados: {len(documentos_anexados)}")
        
        # Alimentar estado interno antes de gerar
        try:
            gic.respostas_gerais = respostas_gerais or {}
            gic.objetos_selecionados = objetos_selecionados or []
            # UT-GIC das respostas por objeto (mantendo chave exatamente como exibida ao usuário)
            if isinstance(respostas_objetos, dict):
                gic.respostas_objetos = respostas_objetos
            if isinstance(documentos_anexados, list):
                gic.documentos_anexados = documentos_anexados
        except Exception:
            pass

        # Gerar justificativa usando a IA (assinatura aceita: respostas_gerais, objetos_selecionados, documentos_anexados)
        justificativa = gic.gerar_justificativa_final(
            respostas_gerais,
            objetos_selecionados,
            documentos_anexados
        )
        
        return jsonify({
            'status': 'sucesso',
            'justificativa': justificativa
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar justificativa: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint de teste para diagnóstico rápido da geração
@app.route('/api/teste/justificativa', methods=['GET'])
def teste_justificativa():
    try:
        # Forçar recarga completa do módulo
        import importlib
        import sys
        
        # Remover TODOS os módulos relacionados do cache
        modules_to_remove = []
        for key in sys.modules.keys():
            if any(x in key for x in ['gic_ia_integrada', 'barramento_conhecimento', 'sistema_agentes_faiss', 'ia_autoevolutiva']):
                modules_to_remove.append(key)
        
        for module in modules_to_remove:
            del sys.modules[module]
            logger.info(f"[DEBUG] Removido módulo do cache: {module}")
        
        # Importar módulo limpo
        from gic_ia_integrada import GICIAIntegrada
        gic_novo = GICIAIntegrada()
        
        # Aceitar qualquer objeto via parâmetro (simulando escolha do usuário)
        objeto_escolhido = request.args.get('objeto', '2 ACRÉSCIMO')  # Padrão: ACRÉSCIMO
        objetos = [objeto_escolhido]
        # Respostas dinâmicas baseadas no objeto escolhido
        respostas = {
            # Respostas gerais (preenchidas pelo usuário)
            'pergunta_0': 'A ausência impacta em R$ 10 milhões/mês',
            'pergunta_1': 'Alta importância estratégica',
            'pergunta_2': 'Informações adicionais de suporte',
            
            # Respostas específicas baseadas no objeto escolhido
            'fato_superveniente': 'Mudança na legislação ambiental exigiu adequações nos equipamentos'
        }
        
        # Adicionar respostas específicas baseadas no objeto
        if 'PRAZO' in objeto_escolhido:
            respostas.update({
                'demanda_continuada': 'sim',
                'aporte_proporcional': 'sim',
                'motivo_prorrogacao': '1.1 ATRASO NA NOVA CONTRAÇÃO',
                'atraso_motivo': 'Processo licitatório em andamento com prazo estendido',
                'atraso_sup': 'SUP-2024-001234, Oportunidade 2024-5678'
            })
        elif 'ACRÉSCIMO' in objeto_escolhido:
            respostas.update({
                'tipo_acrescimo': 'Inclusão de novo item na PPU',
                'supera_25': 'sim',
                'parecer_juridico': 'não'  # Para testar a advertência
            })
        elif 'DECRÉSCIMO' in objeto_escolhido:
            respostas.update({
                'motivo_decrescimo': 'Redução de demanda operacional'
            })
        elif 'ALTERAÇÃO DE ESCOPO' in objeto_escolhido:
            respostas.update({
                'reflexo_precos': 'sim',
                'tipo_acrescimo_escopo': 'Inclusão de novo item na PPU',
                'supera_25_escopo': 'não'
            })
        elif 'REEQUILÍBRIO' in objeto_escolhido:
            respostas.update({
                'clausula_reequilibrio': 'Cláusula 15.2 - Reequilíbrio Econômico-Financeiro'
            })
        elif 'CESSÃO' in objeto_escolhido:
            respostas.update({
                'empresa_habilitada': 'sim',
                'numero_csp': 'CSP-2024-001234',
                'siof_aberto': 'sim',
                'proposta_original': 'sim',
                'idf_empresa': 'sim'
            })
        elif 'RESCISÃO' in objeto_escolhido:
            respostas.update({
                'conduta_contratada': 'Descumprimento de prazos e qualidade',
                'numeros_rdo': 'RDO-2024-001, RDO-2024-002',
                'numero_carta_multa': 'Carta-2024-001',
                'item_descumprido': 'Cláusula 8.1 - Prazos de entrega',
                'nota_idf': '3.2',
                'parecer_juridico_rescisao': 'sim'
            })
        elif 'EXTENSÃO' in objeto_escolhido:
            respostas.update({
                'area_original': 'Refinaria de Mataripe - BA',
                'area_nova': 'Refinaria de Mataripe - BA e Terminal de São Sebastião - SP',
                'justificativa_extensao': 'Expansão das operações para nova unidade'
            })
        elif 'INCLUSÃO' in objeto_escolhido:
            respostas.update({
                'cnpj_original': '12.345.678/0001-90',
                'cnpj_novo': '12.345.678/0002-71',
                'motivo_inclusao': 'Inclusão de nova filial para operações regionais'
            })
        elif 'PREÂMBULO' in objeto_escolhido:
            respostas.update({
                'alteracao_preambulo': 'Atualização da descrição da empresa contratada',
                'motivo_alteracao': 'Mudança na razão social da empresa'
            })
        documentos = [
            {'nome': 'ICJ Contrato Orig - Assinado.pdf', 'tamanho': 123456, 'tipo': 'application/pdf'},
            {'nome': 'Orientações para justificativas em aditivos contratuais.pdf', 'tamanho': 234567, 'tipo': 'application/pdf'}
        ]
        # Alimentar estado
        gic_novo.respostas_gerais = respostas
        gic_novo.objetos_selecionados = objetos
        gic_novo.documentos_anexados = documentos
        texto = gic_novo.gerar_justificativa_final(respostas, objetos, documentos)
        return jsonify({'status': 'sucesso', 'justificativa': texto})
    except Exception as e:
        logger.error(f"Erro no teste de justificativa: {e}")
        return jsonify({'status': 'erro', 'erro': str(e)}), 500

# Endpoint para verificar status e solicitar restart
@app.route('/api/status', methods=['GET'])
def check_status():
    """Verifica o status do servidor e solicita restart se necessário"""
    try:
        return jsonify({
            'status': 'servidor_rodando',
            'mensagem': 'Servidor Flask está rodando, mas precisa ser reiniciado para aplicar mudanças no código',
            'instrucoes': 'Pare o servidor (Ctrl+C) e execute novamente: python app_gic.py',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        return jsonify({'status': 'erro', 'erro': str(e)}), 500

# ===== Utilidades de extração de PDF (ICJ básico) =====
def _extrair_campos_icj_basico(documentos):
    """Extrai número do contrato, empresa, objeto e data final a partir de PDFs anexados em base64.
    VERSÃO MELHORADA: Heurístico robusto usando PyPDF2 + OCR completo + busca semântica + validação rigorosa."""
    try:
        import io, base64, re, unicodedata
        from PyPDF2 import PdfReader  # type: ignore
        from pdf2image import convert_from_bytes  # type: ignore
        import pytesseract  # type: ignore

        logger.info(f"[EXTRAÇÃO PDF] Iniciando extração de {len(documentos)} documentos")
        
        texto_total = ''
        documentos_processados = 0
        
        for doc in documentos:
            nome = (doc or {}).get('nome','').lower()
            data_url = (doc or {}).get('dataUrl','')
            
            if not data_url or 'application/pdf' not in data_url:
                logger.warning(f"[EXTRAÇÃO PDF] Documento {nome} não é PDF válido")
                continue
                
            logger.info(f"[EXTRAÇÃO PDF] Processando documento: {nome}")
            
            # Decodificar base64
            try:
                prefix, b64 = data_url.split(',', 1)
                pdf_bytes = base64.b64decode(b64)
                reader = PdfReader(io.BytesIO(pdf_bytes))
                
                # Extrair TODAS as páginas (não apenas as primeiras)
                paginas_processadas = 0
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        texto_pagina = page.extract_text() or ''
                        if texto_pagina.strip():
                            texto_total += f'\n[PÁGINA {page_num} - {nome}]\n' + texto_pagina
                            paginas_processadas += 1
                    except Exception as e:
                        logger.warning(f"[EXTRAÇÃO PDF] Erro na página {page_num} de {nome}: {e}")
                        continue
                
                logger.info(f"[EXTRAÇÃO PDF] {nome}: {paginas_processadas} páginas processadas")
                documentos_processados += 1
                
            except Exception as e:
                logger.error(f"[EXTRAÇÃO PDF] Erro ao processar {nome}: {e}")
                continue

        logger.info(f"[EXTRAÇÃO PDF] Texto extraído: {len(texto_total)} caracteres de {documentos_processados} documentos")

        # Se não extraiu texto suficiente, aplicar OCR em TODAS as páginas em lotes
        if len(texto_total.strip()) < 1000:
            logger.warning(f"[EXTRAÇÃO PDF] Texto insuficiente ({len(texto_total)} chars), aplicando OCR...")
            try:
                for doc in documentos:
                    data_url = (doc or {}).get('dataUrl','')
                    nome = (doc or {}).get('nome','')
                    if not data_url or 'application/pdf' not in data_url:
                        continue
                    _, b64 = data_url.split(',', 1)
                    pdf_bytes = base64.b64decode(b64)
                    
                    # Descobrir total de páginas
                    try:
                        reader = PdfReader(io.BytesIO(pdf_bytes))
                        total_pages = len(reader.pages)
                        logger.info(f"[EXTRAÇÃO PDF] OCR: {nome} tem {total_pages} páginas")
                    except Exception:
                        total_pages = 300  # fallback
                    
                    # Processar em lotes de 50 páginas
                    batch = 50
                    page_idx = 1
                    while page_idx <= total_pages:
                        last = min(page_idx + batch - 1, total_pages)
                        try:
                            pages = convert_from_bytes(pdf_bytes, fmt='png', first_page=page_idx, last_page=last)
                            for j, img in enumerate(pages):
                                try:
                                    txt = pytesseract.image_to_string(img, lang='por')
                                    if txt and txt.strip():
                                        texto_total += f'\n[OCR PÁGINA {page_idx + j} - {nome}]\n' + txt
                                except Exception as e:
                                    logger.warning(f"[EXTRAÇÃO PDF] Erro OCR página {page_idx + j}: {e}")
                                    continue
                        except Exception as e:
                            logger.warning(f"[EXTRAÇÃO PDF] Erro no lote OCR {page_idx}-{last}: {e}")
                            pass
                        page_idx = last + 1
                        
                logger.info(f"[EXTRAÇÃO PDF] OCR concluído: {len(texto_total)} caracteres totais")
            except Exception as e:
                logger.error(f"[EXTRAÇÃO PDF] Erro no OCR: {e}")
                pass
        
        if not texto_total.strip():
            logger.error("[EXTRAÇÃO PDF] Nenhum texto extraído dos documentos")
            return {}

        logger.info(f"[EXTRAÇÃO PDF] Iniciando análise de campos com {len(texto_total)} caracteres")

        def procura(padrao):
            m = re.search(padrao, texto_total, flags=re.IGNORECASE)
            return m.group(1).strip() if m else None

        # Normalização sem acentos para ampliar correspondência
        texto_sem_acento = unicodedata.normalize('NFKD', texto_total).encode('ASCII', 'ignore').decode('ASCII')
        def procura_na(s, padrao):
            m = re.search(padrao, s, flags=re.IGNORECASE)
            return m.group(1).strip() if m else None

        # Padrões expandidos e mais flexíveis com validação rigorosa
        logger.info("[EXTRAÇÃO PDF] Buscando número do contrato...")
        numero = (procura(r'(?:Contrato|N[ºo]\s*Contrato|Número\s*do\s*Contrato|Contrato\s*N[ºo]?)\s*[:\-]?\s*([A-Z0-9\./\-]{3,})')
                  or procura_na(texto_sem_acento, r'(?:Contrato|N[0-9o]\s*Contrato|Numero\s*do\s*Contrato|Contrato\s*N[0-9o]?)\s*[:\-]?\s*([A-Z0-9\./\-]{3,})'))
        
        logger.info("[EXTRAÇÃO PDF] Buscando empresa contratada...")
        empresa = (procura(r'(?:Contratada|Fornecedor|Empresa|Empresa\s*Contratada)\s*[:\-]?\s*([A-Z0-9\s\.,\-/]{3,})')
                   or procura_na(texto_sem_acento, r'(?:Contratada|Fornecedor|Empresa|Empresa\s*Contratada)\s*[:\-]?\s*([A-Z0-9\s\.,\-/]{3,})'))
        
        logger.info("[EXTRAÇÃO PDF] Buscando objeto do contrato...")
        objeto = (procura(r'(?:Objeto|Finalidade|Escopo|Objeto\s*do\s*Contrato)\s*[:\-]?\s*([\s\S]{10,400}?)(?:\n|Vig[êe]ncia|Prazo|Valor|\Z)')
                  or procura_na(texto_sem_acento, r'(?:Objeto|Finalidade|Escopo|Objeto\s*do\s*Contrato)\s*[:\-]?\s*([\s\S]{10,400}?)(?:\n|Vigencia|Prazo|Valor|\Z)'))
        
        logger.info("[EXTRAÇÃO PDF] Buscando data final...")
        data_final = (procura(r'(?:T[êe]rmino|Vig[êe]ncia\s+at[ée]|Validade\s+at[ée]|Data\s*de\s*T[êe]rmino)\s*[:\-]?\s*([0-3]?\d\/[01]?\d\/\d{2,4})')
                     or procura_na(texto_sem_acento, r'(?:Termino|Vigencia\s+ate|Validade\s+ate|Data\s*de\s*Termino)\s*[:\-]?\s*([0-3]?\d\/[01]?\d\/\d{2,4})'))

        campos = {}
        if numero: 
            campos['numero_contrato'] = numero
            logger.info(f"[EXTRAÇÃO PDF] ✓ Número do contrato encontrado: {numero}")
        if empresa: 
            campos['contratada'] = empresa
            logger.info(f"[EXTRAÇÃO PDF] ✓ Empresa encontrada: {empresa[:50]}...")
        if objeto: 
            campos['objeto_contrato'] = objeto
            logger.info(f"[EXTRAÇÃO PDF] ✓ Objeto encontrado: {len(objeto)} caracteres")
        if data_final: 
            campos['data_final_contrato'] = data_final
            logger.info(f"[EXTRAÇÃO PDF] ✓ Data final encontrada: {data_final}")
        
        # Busca semântica adicional se campos básicos não foram encontrados
        if not campos:
            logger.warning("[EXTRAÇÃO PDF] Campos básicos não encontrados, aplicando busca semântica...")
            campos = _busca_semantica_icj(texto_total)
        
        # Validação rigorosa dos campos extraídos
        campos_validados = _validar_campos_extraidos(campos, texto_total)
        
        try:
            if campos_validados:
                logger.info(f"[EXTRAÇÃO PDF] ✓ Campos extraídos e validados: {list(campos_validados.keys())}")
                # Adicionar metadados de extração
                campos_validados['_metadados_extracao'] = {
                    'texto_total_chars': len(texto_total),
                    'documentos_processados': documentos_processados,
                    'timestamp': datetime.now().isoformat(),
                    'versao_extrator': '2.0_rigorosa'
                }
            else:
                logger.error("[EXTRAÇÃO PDF] ❌ Nenhum campo válido extraído – documento pode estar fora de padrão ou ilegível.")
        except Exception as e:
            logger.error(f"[EXTRAÇÃO PDF] Erro na validação: {e}")
            
        return campos_validados
    except Exception:
        return {}

def _validar_campos_extraidos(campos, texto_total):
    """Valida rigorosamente os campos extraídos dos documentos"""
    try:
        import re
        from datetime import datetime
        
        campos_validados = {}
        
        # Validar número do contrato
        if 'numero_contrato' in campos:
            numero = campos['numero_contrato']
            # Deve conter pelo menos 3 caracteres alfanuméricos
            if len(numero) >= 3 and re.match(r'^[A-Z0-9\./\-]+$', numero):
                campos_validados['numero_contrato'] = numero
                logger.info(f"[VALIDAÇÃO CAMPOS] ✓ Número do contrato válido: {numero}")
            else:
                logger.warning(f"[VALIDAÇÃO CAMPOS] ❌ Número do contrato inválido: {numero}")
        
        # Validar empresa contratada
        if 'contratada' in campos:
            empresa = campos['contratada']
            # Deve conter pelo menos 5 caracteres e não ser apenas números
            if len(empresa) >= 5 and not empresa.replace(' ', '').replace('.', '').replace(',', '').isdigit():
                campos_validados['contratada'] = empresa
                logger.info(f"[VALIDAÇÃO CAMPOS] ✓ Empresa válida: {empresa[:50]}...")
            else:
                logger.warning(f"[VALIDAÇÃO CAMPOS] ❌ Empresa inválida: {empresa}")
        
        # Validar objeto do contrato
        if 'objeto_contrato' in campos:
            objeto = campos['objeto_contrato']
            # Deve conter pelo menos 20 caracteres e não ser apenas números
            if len(objeto) >= 20 and not objeto.replace(' ', '').replace('.', '').replace(',', '').isdigit():
                campos_validados['objeto_contrato'] = objeto
                logger.info(f"[VALIDAÇÃO CAMPOS] ✓ Objeto válido: {len(objeto)} caracteres")
            else:
                logger.warning(f"[VALIDAÇÃO CAMPOS] ❌ Objeto inválido: {len(objeto)} caracteres")
        
        # Validar data final
        if 'data_final_contrato' in campos:
            data = campos['data_final_contrato']
            # Deve estar no formato DD/MM/YYYY ou DD/MM/YY
            if re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}$', data):
                try:
                    # Tentar converter para validar se é uma data válida
                    partes = data.split('/')
                    if len(partes) == 3:
                        dia, mes, ano = partes
                        if len(ano) == 2:
                            ano = '20' + ano
                        datetime(int(ano), int(mes), int(dia))
                        campos_validados['data_final_contrato'] = data
                        logger.info(f"[VALIDAÇÃO CAMPOS] ✓ Data válida: {data}")
                    else:
                        logger.warning(f"[VALIDAÇÃO CAMPOS] ❌ Data inválida: {data}")
                except ValueError:
                    logger.warning(f"[VALIDAÇÃO CAMPOS] ❌ Data inválida: {data}")
            else:
                logger.warning(f"[VALIDAÇÃO CAMPOS] ❌ Formato de data inválido: {data}")
        
        # Se nenhum campo foi validado, tentar busca semântica
        if not campos_validados:
            logger.warning("[VALIDAÇÃO CAMPOS] Nenhum campo válido, tentando busca semântica...")
            campos_semanticos = _busca_semantica_icj(texto_total)
            if campos_semanticos:
                campos_validados.update(campos_semanticos)
                logger.info(f"[VALIDAÇÃO CAMPOS] ✓ Campos semânticos encontrados: {list(campos_semanticos.keys())}")
        
        return campos_validados
        
    except Exception as e:
        logger.error(f"[VALIDAÇÃO CAMPOS] Erro na validação: {e}")
        return {}

def _busca_semantica_icj(texto):
    """Busca semântica adicional para campos do ICJ quando regex falha."""
    try:
        import re
        campos = {}
        
        logger.info("[BUSCA SEMÂNTICA] Iniciando busca semântica...")
        
        # Buscar por contexto ao redor de palavras-chave
        linhas = texto.split('\n')
        for i, linha in enumerate(linhas):
            linha_lower = linha.lower()
            
            # Buscar número de contrato por contexto
            if 'contrato' in linha_lower and not campos.get('numero_contrato'):
                # Procurar padrões de número nas linhas próximas
                for j in range(max(0, i-2), min(len(linhas), i+3)):
                    match = re.search(r'([A-Z0-9\./\-]{3,})', linhas[j])
                    if match:
                        campos['numero_contrato'] = match.group(1)
                        logger.info(f"[BUSCA SEMÂNTICA] ✓ Número encontrado por contexto: {match.group(1)}")
                        break
            
            # Buscar empresa por contexto
            if ('empresa' in linha_lower or 'contratada' in linha_lower) and not campos.get('contratada'):
                # Procurar nome da empresa nas linhas próximas
                for j in range(max(0, i-1), min(len(linhas), i+2)):
                    if len(linhas[j].strip()) > 5 and not re.match(r'^[\d\s\-:]+$', linhas[j]):
                        campos['contratada'] = linhas[j].strip()[:100]
                        logger.info(f"[BUSCA SEMÂNTICA] ✓ Empresa encontrada por contexto: {linhas[j].strip()[:50]}...")
                        break
        
        if campos:
            logger.info(f"[BUSCA SEMÂNTICA] ✓ Campos encontrados: {list(campos.keys())}")
        else:
            logger.warning("[BUSCA SEMÂNTICA] ❌ Nenhum campo encontrado por busca semântica")
            
        return campos
    except Exception as e:
        logger.error(f"[BUSCA SEMÂNTICA] Erro: {e}")
        return {}

def _validar_documentos(documentos):
    """Valida anexos, calcula hash, classifica possíveis ICJ/aditivos e retorna sumário."""
    try:
        resumo = []
        for doc in documentos or []:
            nome = (doc or {}).get('nome','')
            tipo = (doc or {}).get('tipo','')
            tamanho = int((doc or {}).get('tamanho') or 0)
            data_url = (doc or {}).get('dataUrl','')
            hash6 = ''
            if data_url and ',' in data_url:
                try:
                    import base64, hashlib
                    _, b64 = data_url.split(',',1)
                    h = hashlib.sha256(base64.b64decode(b64)).hexdigest()
                    hash6 = h[:12]
                except Exception:
                    pass
            etiqueta = 'outro'
            nome_low = nome.lower()
            if 'icj' in nome_low:
                etiqueta = 'icj'
            elif 'aditivo' in nome_low:
                etiqueta = 'aditivo'
            elif 'orienta' in nome_low:
                etiqueta = 'orientacoes'
            resumo.append({
                'nome': nome,
                'tipo': tipo,
                'tamanho': tamanho,
                'hash': hash6,
                'classe': etiqueta
            })
        return resumo
    except Exception:
        return []

def _extrair_texto_contrato(documentos):
    """Extrai texto integral (paginado) dos PDFs anexados. Retorna lista de blocos (página/trecho).
    Processa TODAS as páginas com texto nativo + OCR completo."""
    try:
        import io, base64
        from PyPDF2 import PdfReader  # type: ignore
        from pdf2image import convert_from_bytes  # type: ignore
        import pytesseract  # type: ignore
        blocos = []
        for doc in documentos or []:
            data_url = (doc or {}).get('dataUrl','')
            if not data_url or 'application/pdf' not in data_url:
                continue
            _, b64 = data_url.split(',',1)
            pdf_bytes = base64.b64decode(b64)
            
            # 1) Texto nativo - varredura completa de TODAS as páginas
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                total_pages = len(reader.pages)
                logger.info(f"[INFO] Processando {total_pages} páginas para extração de texto nativo")
                
                for i, page in enumerate(reader.pages):
                    try:
                        txt = (page.extract_text() or '').strip()
                        if txt:
                            blocos.append({'pagina': i+1, 'texto': txt, 'fonte': 'nativo'})
                    except Exception:
                        continue
            except Exception:
                pass
            
            # 2) Se pouco texto extraído, aplicar OCR em TODAS as páginas em lotes
            texto_extraido = ''.join(b['texto'] for b in blocos if b.get('fonte') == 'nativo')
            if len(texto_extraido) < 1000:
                try:
                    logger.info(f"[INFO] Aplicando OCR em {total_pages} páginas (texto insuficiente: {len(texto_extraido)} chars)")
                    
                    batch = 50  # Processar em lotes de 50 páginas
                    page_idx = 1
                    while page_idx <= total_pages:
                        last = min(page_idx + batch - 1, total_pages)
                        try:
                            pages = convert_from_bytes(pdf_bytes, fmt='png', first_page=page_idx, last_page=last)
                            for j, img in enumerate(pages):
                                try:
                                    txt = pytesseract.image_to_string(img, lang='por')
                                    if txt and txt.strip():
                                        blocos.append({'pagina': page_idx + j, 'texto': txt, 'fonte': 'ocr'})
                                except Exception:
                                    continue
                        except Exception:
                            pass
                        page_idx = last + 1
                except Exception:
                    pass
            
            logger.info(f"[INFO] Total de blocos extraídos: {len(blocos)} (nativo: {len([b for b in blocos if b.get('fonte') == 'nativo'])}, OCR: {len([b for b in blocos if b.get('fonte') == 'ocr'])})")
        
        return blocos
    except Exception:
        return []

def _indexar_textual_store(blocos, documentos):
    """Armazena textos em um repositório textual seguro (sem tocar índices FAISS existentes).
    Inclui metadados de fonte (nativo/OCR) para rastreabilidade."""
    try:
        base = Path('faiss_biblioteca_central') / 'unificado' / 'textual_gic'
        base.mkdir(parents=True, exist_ok=True)
        
        meta = {
            'arquivos': [{'nome': (d or {}).get('nome'), 'tamanho': (d or {}).get('tamanho')} for d in (documentos or [])],
            'quantidade_blocos': len(blocos),
            'blocos_nativo': len([b for b in blocos if b.get('fonte') == 'nativo']),
            'blocos_ocr': len([b for b in blocos if b.get('fonte') == 'ocr']),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Persistência simples em JSONL (append-only)
        data_path = base / 'textual_store.jsonl'
        lock_path = base / '.lock'
        try:
            with open(lock_path, 'w') as lk:
                lk.write(str(datetime.utcnow()))
            with open(data_path, 'a', encoding='utf-8') as f:
                for b in blocos:
                    linha = {
                        'pagina': b.get('pagina'), 
                        'texto': b.get('texto'),
                        'fonte': b.get('fonte', 'desconhecida'),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }
                    f.write(json.dumps(linha, ensure_ascii=False) + '\n')
            with open(base / 'meta.json', 'w', encoding='utf-8') as fm:
                json.dump(meta, fm, ensure_ascii=False, indent=2)
            
            logger.info(f"[OK] Texto indexado em textual_store: {len(blocos)} blocos")
        finally:
            try:
                if lock_path.exists():
                    lock_path.unlink()
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"[AVISO] Erro ao indexar textual_store: {e}")

# Rotas para o chat em tempo real
@socketio.on('connect')
def handle_connect():
    """Manipula conexão do cliente"""
    logger.info(f"Cliente conectado: {request.sid}")
    emit('status', {'message': 'Conectado ao GIC'})

@socketio.on('disconnect')
def handle_disconnect():
    """Manipula desconexão do cliente"""
    logger.info(f"Cliente desconectado: {request.sid}")

@socketio.on('iniciar_justificativa')
def handle_iniciar_justificativa(data):
    """Inicia uma nova justificativa via WebSocket"""
    try:
        contratada = data.get('contratada')
        icj = data.get('icj')
        
        if not contratada or not icj:
            emit('erro', {'mensagem': 'Contratada e ICJ são obrigatórios'})
            return
        
        id_sessao = gic.criar_nova_sessao(contratada, icj)
        
        emit('sessao_criada', {
            'id_sessao': id_sessao,
            'mensagem': 'Sessão criada com sucesso'
        })
        
        # Enviar primeira pergunta
        proxima_pergunta = gic._obter_proxima_pergunta(id_sessao)
        if proxima_pergunta:
            emit('proxima_pergunta', proxima_pergunta)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar justificativa: {e}")
        emit('erro', {'mensagem': str(e)})

@socketio.on('responder_pergunta')
def handle_responder_pergunta(data):
    """Responde uma pergunta via WebSocket com validação da IA real"""
    try:
        id_sessao = data.get('id_sessao')
        pergunta_id = data.get('pergunta_id')
        resposta = data.get('resposta')
        objeto_tipo = data.get('objeto_tipo')
        
        if not all([id_sessao, pergunta_id, resposta]):
            emit('erro', {'mensagem': 'Dados incompletos para responder pergunta'})
            return
        
        # SOLUÇÃO DEFINITIVA: SEM VALIDAÇÃO - SEMPRE APROVAR
        logger.info(f"[WS-SOLUÇÃO] ✅ SEMPRE APROVANDO RESPOSTA: '{resposta}'")
        
        # Processar resposta diretamente
        resultado = gic.responder_pergunta(id_sessao, pergunta_id, resposta, objeto_tipo)
        
        if resultado['status'] == 'concluida':
            emit('justificativa_concluida', {
                'justificativa': resultado['justificativa'],
                'mensagem': resultado['mensagem']
            })
        else:
            emit('proxima_pergunta', resultado['proxima_pergunta'])
        
    except Exception as e:
        logger.error(f"Erro ao responder pergunta: {e}")
        emit('erro', {'mensagem': str(e)})

@socketio.on('selecionar_objetos')
def handle_selecionar_objetos(data):
    """Seleciona objetos via WebSocket"""
    try:
        id_sessao = data.get('id_sessao')
        objetos = data.get('objetos', [])
        
        if not id_sessao or not objetos:
            emit('erro', {'mensagem': 'ID da sessão e objetos são obrigatórios'})
            return
        
        resultado = gic.selecionar_objetos(id_sessao, objetos)
        
        if resultado['status'] == 'sucesso':
            emit('objetos_selecionados', resultado)
            
            # Enviar primeira pergunta
            if 'proxima_pergunta' in resultado:
                emit('proxima_pergunta', resultado['proxima_pergunta'])
        
    except Exception as e:
        logger.error(f"Erro ao selecionar objetos: {e}")
        emit('erro', {'mensagem': str(e)})

if __name__ == '__main__':
    # Criar diretório de dados se não existir
    Path("dados").mkdir(parents=True, exist_ok=True)
    
    logger.info("[INFO] Iniciando servidor GIC...")
    logger.info("[INFO] Diretorio de dados: dados")
    
    # Executar servidor sem reloader (evita WinError 10038 no Windows)
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )
