"""
Google Gmail API Client para sistema biomimético AI-Biomimetica
Fase 6.3: Percepção Multimodal - Integração com Gmail

Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Funcionalidades:
- Leitura de emails (caixa de entrada, labels)
- Envio de emails
- Gerenciamento de labels/categorias
- Busca avançada de emails
- Análise de conteúdo (futuro: classificação biomimética)

Dependências:
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- google-auth
- base64, email (bibliotecas padrão)

Escopos Gmail API:
- https://www.googleapis.com/auth/gmail.readonly (leitura)
- https://www.googleapis.com/auth/gmail.send (envio)
- https://www.googleapis.com/auth/gmail.labels (labels)
- https://www.googleapis.com/auth/gmail.modify (modificação)
"""

import os
import pickle
import base64
import mimetypes
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos da API Gmail (permissões)
SCOPES_READONLY = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES_SEND = ['https://www.googleapis.com/auth/gmail.send']
SCOPES_MODIFY = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES_FULL = ['https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    """Cliente para integração com Google Gmail API"""
    
    def __init__(self, 
                 credentials_path: str = "credentials.json",
                 token_path: str = "token_gmail.pickle",
                 storage_dir: str = "storage",
                 scopes: List[str] = None):
        """
        Inicializa cliente Gmail API.
        
        Args:
            credentials_path: Caminho para arquivo credentials.json
            token_path: Caminho para salvar token de autenticação
            storage_dir: Diretório para armazenamento persistente
            scopes: Escopos de permissão (padrão: modify - leitura+escrita)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.storage_dir = storage_dir
        self.scopes = scopes or SCOPES_MODIFY
        self.service = None
        
        # Garantir diretório de storage existe
        os.makedirs(storage_dir, exist_ok=True)
    
    def authenticate(self) -> Any:
        """
        Autentica com Google OAuth2 e retorna serviço Gmail.
        
        Returns:
            Serviço Google Gmail API construído
        """
        creds = None
        
        # Caminho completo para token
        token_full_path = os.path.join(self.storage_dir, self.token_path)
        
        # Tentar carregar token salvo
        if os.path.exists(token_full_path):
            with open(token_full_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais para próxima vez
            with open(token_full_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Construir serviço Gmail API
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def get_service(self) -> Any:
        """Retorna serviço (autentica se necessário)"""
        if not self.service:
            self.authenticate()
        return self.service
    
    def list_messages(self, 
                     max_results: int = 10,
                     label_ids: List[str] = None,
                     query: str = None) -> List[Dict[str, Any]]:
        """
        Lista mensagens da caixa de entrada.
        
        Args:
            max_results: Número máximo de mensagens
            label_ids: IDs das labels para filtrar
            query: Query de busca Gmail (ex: "from:exemplo@gmail.com")
            
        Returns:
            Lista de mensagens (metadados)
        """
        try:
            service = self.get_service()
            
            # Construir parâmetros da query
            params = {
                'userId': 'me',
                'maxResults': max_results
            }
            
            if query:
                params['q'] = query
            
            if label_ids:
                params['labelIds'] = label_ids
            
            # Executar busca
            response = service.users().messages().list(**params).execute()
            
            messages = response.get('messages', [])
            
            # Formatar resultados
            formatted_messages = []
            for msg in messages:
                formatted = {
                    'id': msg.get('id'),
                    'threadId': msg.get('threadId'),
                    'labelIds': msg.get('labelIds', []),
                    'snippet': msg.get('snippet', ''),
                    'historyId': msg.get('historyId'),
                    'internalDate': msg.get('internalDate')
                }
                formatted_messages.append(formatted)
            
            return formatted_messages
            
        except HttpError as error:
            print(f'❌ Erro ao listar mensagens: {error}')
            return []
        except Exception as e:
            print(f'❌ Erro inesperado em list_messages: {e}')
            return []
    
    def get_message(self, message_id: str, format: str = 'full') -> Optional[Dict[str, Any]]:
        """
        Obtém mensagem completa pelo ID.
        
        Args:
            message_id: ID da mensagem
            format: Formato da mensagem ('full', 'metadata', 'minimal')
            
        Returns:
            Mensagem completa com headers e body
        """
        try:
            service = self.get_service()
            
            # Buscar mensagem completa
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            ).execute()
            
            # Extrair partes da mensagem
            headers = {}
            for header in message.get('payload', {}).get('headers', []):
                name = header.get('name', '').lower()
                value = header.get('value', '')
                headers[name] = value
            
            # Extrair body/texto
            body = self._extract_message_body(message.get('payload', {}))
            
            # Formatar resposta
            formatted_message = {
                'id': message.get('id'),
                'threadId': message.get('threadId'),
                'labelIds': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'historyId': message.get('historyId'),
                'internalDate': message.get('internalDate'),
                'headers': headers,
                'body': body,
                'subject': headers.get('subject', 'Sem assunto'),
                'from': headers.get('from', 'Desconhecido'),
                'to': headers.get('to', ''),
                'date': headers.get('date', ''),
                'hasAttachments': self._has_attachments(message.get('payload', {}))
            }
            
            return formatted_message
            
        except HttpError as error:
            print(f'❌ Erro ao buscar mensagem {message_id}: {error}')
            return None
        except Exception as e:
            print(f'❌ Erro inesperado em get_message: {e}')
            return None
    
    def send_message(self, 
                    to: str,
                    subject: str,
                    body: str,
                    cc: str = None,
                    bcc: str = None,
                    attachments: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Envia email via Gmail API.
        
        Args:
            to: Destinatário (pode ser lista separada por vírgulas)
            subject: Assunto
            body: Corpo do email (HTML ou texto)
            cc: CC (opcional)
            bcc: BCC (opcional)
            attachments: Lista de caminhos para anexos
            
        Returns:
            Mensagem enviada ou None em caso de erro
        """
        try:
            service = self.get_service()
            
            # Criar mensagem
            if attachments:
                message = self._create_message_with_attachments(to, subject, body, cc, bcc, attachments)
            else:
                message = self.create_message('me', to, subject, body, cc, bcc)
            
            # Enviar mensagem
            sent_message = service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            print(f'✅ Email enviado com sucesso! ID: {sent_message.get("id")}')
            return sent_message
            
        except HttpError as error:
            print(f'❌ Erro ao enviar email: {error}')
            return None
        except Exception as e:
            print(f'❌ Erro inesperado em send_message: {e}')
            return None
    
    def create_draft(self,
                    to: str,
                    subject: str,
                    body: str,
                    cc: str = None,
                    bcc: str = None) -> Optional[Dict[str, Any]]:
        """
        Cria rascunho no Gmail.
        
        Args:
            to: Destinatário
            subject: Assunto
            body: Corpo do email
            cc: CC (opcional)
            bcc: BCC (opcional)
            
        Returns:
            Rascunho criado ou None em caso de erro
        """
        try:
            service = self.get_service()
            
            # Criar mensagem
            message = self.create_message('me', to, subject, body, cc, bcc)
            
            # Criar rascunho
            draft = service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            print(f'✅ Rascunho criado! ID: {draft.get("id")}')
            return draft
            
        except HttpError as error:
            print(f'❌ Erro ao criar rascunho: {error}')
            return None
        except Exception as e:
            print(f'❌ Erro inesperado em create_draft: {e}')
            return None
    
    def list_labels(self) -> List[Dict[str, Any]]:
        """
        Lista todas as labels da conta Gmail.
        
        Returns:
            Lista de labels
        """
        try:
            service = self.get_service()
            
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            formatted_labels = []
            for label in labels:
                formatted = {
                    'id': label.get('id'),
                    'name': label.get('name'),
                    'type': label.get('type'),
                    'messageListVisibility': label.get('messageListVisibility', ''),
                    'labelListVisibility': label.get('labelListVisibility', ''),
                    'messagesTotal': label.get('messagesTotal', 0),
                    'messagesUnread': label.get('messagesUnread', 0),
                    'threadsTotal': label.get('threadsTotal', 0),
                    'threadsUnread': label.get('threadsUnread', 0)
                }
                formatted_labels.append(formatted)
            
            return formatted_labels
            
        except HttpError as error:
            print(f'❌ Erro ao listar labels: {error}')
            return []
        except Exception as e:
            print(f'❌ Erro inesperado em list_labels: {e}')
            return []
    
    def create_label(self, 
                    name: str,
                    label_type: str = "user",
                    color: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Cria nova label no Gmail.
        
        Args:
            name: Nome da label
            label_type: Tipo (user, system)
            color: Configuração de cor
            
        Returns:
            Label criada ou None em caso de erro
        """
        try:
            service = self.get_service()
            
            label_body = {
                'name': name,
                'type': label_type,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            if color:
                label_body['color'] = color
            
            label = service.users().labels().create(
                userId='me',
                body=label_body
            ).execute()
            
            print(f'✅ Label criada: {name} (ID: {label.get("id")})')
            return label
            
        except HttpError as error:
            print(f'❌ Erro ao criar label: {error}')
            return None
        except Exception as e:
            print(f'❌ Erro inesperado em create_label: {e}')
            return None
    
    def search_messages(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Busca mensagens usando query Gmail.
        
        Args:
            query: Query Gmail (ex: "from:exemplo label:inbox newer_than:1d")
            max_results: Número máximo de resultados
            
        Returns:
            Lista de mensagens encontradas
        """
        # Usar list_messages com query
        return self.list_messages(max_results=max_results, query=query)
    
    def get_unread_count(self) -> int:
        """
        Retorna número de emails não lidos.
        
        Returns:
            Contagem de emails não lidos
        """
        try:
            labels = self.list_labels()
            
            for label in labels:
                if label.get('name') == 'INBOX':
                    return label.get('messagesUnread', 0)
            
            # Fallback: buscar mensagens não lidas
            unread_messages = self.search_messages("is:unread", max_results=1)
            if unread_messages:
                # Se queremos apenas saber se há não lidos
                inbox_label = next((l for l in labels if l.get('name') == 'INBOX'), None)
                if inbox_label:
                    return inbox_label.get('messagesUnread', 1 if unread_messages else 0)
            
            return 0
            
        except Exception as e:
            print(f'⚠️  Erro ao contar emails não lidos: {e}')
            # Fallback simples
            unread = self.search_messages("is:unread", max_results=100)
            return len(unread)
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Marca email como lido.
        
        Args:
            message_id: ID da mensagem
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            service = self.get_service()
            
            # Remover label UNREAD
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            print(f'✅ Email {message_id} marcado como lido')
            return True
            
        except HttpError as error:
            print(f'❌ Erro ao marcar email como lido: {error}')
            return False
        except Exception as e:
            print(f'❌ Erro inesperado em mark_as_read: {e}')
            return False
    
    def archive_message(self, message_id: str) -> bool:
        """
        Arquiva email (remove da caixa de entrada).
        
        Args:
            message_id: ID da mensagem
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            service = self.get_service()
            
            # Remover label INBOX
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            
            print(f'✅ Email {message_id} arquivado (removido da caixa de entrada)')
            return True
            
        except HttpError as error:
            print(f'❌ Erro ao arquivar email: {error}')
            return False
        except Exception as e:
            print(f'❌ Erro inesperado em archive_message: {e}')
            return False
    
    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """Extrai corpo da mensagem da estrutura do payload"""
        try:
            # Se tem parts (mensagem multipart)
            if 'parts' in payload:
                # Primeiro, tentar encontrar texto simples (plain text)
                for part in payload['parts']:
                    # Verificar se é parte de texto
                    mime_type = part.get('mimeType', '')
                    if mime_type.startswith('text/plain'):
                        if 'body' in part and 'data' in part['body']:
                            data = part['body']['data']
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                # Se não encontrou plain text, usar HTML
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    if mime_type.startswith('text/html'):
                        if 'body' in part and 'data' in part['body']:
                            data = part['body']['data']
                            html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            # Simplificar HTML para texto
                            import re
                            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
                            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                            return clean_text
            
            # Se não tem parts, tentar body direto
            if 'body' in payload and 'data' in payload['body']:
                data = payload['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            # Se tem body sem data (pode ser vazio)
            if 'body' in payload:
                return '[Corpo da mensagem vazio ou não disponível]'
            
            return '[Corpo da mensagem não disponível]'
            
        except Exception as e:
            print(f'⚠️  Erro ao extrair corpo da mensagem: {e}')
            return '[Erro ao extrair conteúdo]'
    
    def _has_attachments(self, payload: Dict[str, Any]) -> bool:
        """Verifica se mensagem tem anexos"""
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    # Se tem filename, é anexo
                    if 'filename' in part and part['filename']:
                        return True
                    # Verificar recursivamente em sub-parts
                    if 'parts' in part and self._has_attachments(part):
                        return True
            
            return False
        except Exception:
            return False
    
    def _create_message_with_attachments(self,
                                       to: str,
                                       subject: str,
                                       body: str,
                                       cc: str = None,
                                       bcc: str = None,
                                       attachments: List[str] = None) -> Dict[str, Any]:
        """Cria mensagem com anexos"""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Adicionar corpo
        msg_body = MIMEText(body)
        message.attach(msg_body)
        
        # Adicionar anexos
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    try:
                        content_type, encoding = mimetypes.guess_type(file_path)
                        if content_type is None or encoding is not None:
                            content_type = 'application/octet-stream'
                        
                        main_type, sub_type = content_type.split('/', 1)
                        
                        with open(file_path, 'rb') as f:
                            attachment = MIMEBase(main_type, sub_type)
                            attachment.set_payload(f.read())
                        
                        encoders.encode_base64(attachment)
                        
                        filename = os.path.basename(file_path)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{filename}"'
                        )
                        
                        message.attach(attachment)
                        print(f'✅ Anexo adicionado: {filename}')
                        
                    except Exception as e:
                        print(f'⚠️  Erro ao anexar {file_path}: {e}')
                else:
                    print(f'⚠️  Arquivo não encontrado: {file_path}')
        
        # Codificar para formato Gmail
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
    # Métodos utilitários
    @staticmethod
    def create_message(sender: str,
                      to: str,
                      subject: str,
                      body: str,
                      cc: str = None,
                      bcc: str = None) -> Dict[str, Any]:
        """
        Cria estrutura de mensagem para envio via API.
        
        Args:
            sender: Remetente
            to: Destinatário
            subject: Assunto
            body: Corpo
            cc: CC (opcional)
            bcc: BCC (opcional)
            
        Returns:
            Dicionário com mensagem formatada
        """
        message = MIMEText(body)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
    @staticmethod
    def parse_gmail_query(query_parts: Dict[str, Any]) -> str:
        """
        Converte dicionário de parâmetros em query Gmail.
        
        Args:
            query_parts: Ex: {'from': 'exemplo', 'newer_than': '1d', 'label': 'inbox'}
            
        Returns:
            Query Gmail formatada
        """
        parts = []
        for key, value in query_parts.items():
            if key == 'newer_than':
                parts.append(f"newer_than:{value}")
            elif key == 'older_than':
                parts.append(f"older_than:{value}")
            elif key == 'from':
                parts.append(f"from:{value}")
            elif key == 'to':
                parts.append(f"to:{value}")
            elif key == 'subject':
                parts.append(f"subject:{value}")
            elif key == 'label':
                parts.append(f"label:{value}")
            elif key == 'has':
                parts.append(f"has:{value}")
            elif key == 'filename':
                parts.append(f"filename:{value}")
        
        return " ".join(parts)


# Exemplo de uso
if __name__ == "__main__":
    print("📧 Gmail Client - Fase 6.3 Implementada")
    print("=" * 50)
    
    try:
        # Inicializar cliente
        client = GmailClient()
        print("✅ Cliente Gmail inicializado")
        
        # Testar autenticação
        print("\n🔑 Testando autenticação...")
        service = client.authenticate()
        print("✅ Autenticação bem-sucedida!")
        
        # Listar labels
        print("\n🏷️  Listando labels...")
        labels = client.list_labels()
        print(f"   Encontradas {len(labels)} labels")
        
        # Mostrar algumas labels importantes
        important_labels = ['INBOX', 'SENT', 'DRAFT', 'TRASH']
        for label_name in important_labels:
            label = next((l for l in labels if l.get('name') == label_name), None)
            if label:
                unread = label.get('messagesUnread', 0)
                total = label.get('messagesTotal', 0)
                print(f"   • {label_name}: {total} mensagens ({unread} não lidas)")
        
        # Contar emails não lidos
        print(f"\n📬 Emails não lidos: {client.get_unread_count()}")
        
        # Buscar últimos 5 emails
        print("\n📥 Buscando últimos 5 emails...")
        messages = client.list_messages(max_results=5)
        print(f"   Encontrados {len(messages)} emails recentes")
        
        if messages:
            # Mostrar primeiro email
            first_msg = messages[0]
            print(f"\n📄 Primeiro email (ID: {first_msg['id'][:20]}...)")
            print(f"   Snippet: {first_msg.get('snippet', '')[:100]}...")
        
        print("\n" + "=" * 50)
        print("🎯 Gmail API implementada com sucesso!")
        print("\n📋 Métodos disponíveis:")
        print("   ✅ list_messages() - Lista emails")
        print("   ✅ get_message() - Obtém email completo")
        print("   ✅ send_message() - Envia email")
        print("   ✅ create_draft() - Cria rascunho")
        print("   ✅ list_labels() - Lista labels")
        print("   ✅ search_messages() - Busca avançada")
        print("   ✅ get_unread_count() - Contagem não lidos")
        print("   ✅ mark_as_read() - Marca como lido")
        print("   ✅ archive_message() - Arquiva email")
        
        print("\n🔧 Pronto para integração com sistema biomimético!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verifique se credentials.json está correto")
        print("   2. Ative Gmail API no Google Cloud Console")
        print("   3. Adicione escopos Gmail às credenciais OAuth")
        print("   4. Confirme URLs de redirecionamento")