# Importações de bibliotecas padrão do Python
import google.generativeai as genai
import os
import time
import pickle
import traceback 
from datetime import datetime, timedelta, UTC

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# --- Configurações Globais ---
CLIENT_SECRETS_FILE = 'client_secrets.json'
CREDENTIALS_FILE = 'credentials.pickle'

# Escopos OAuth 2.0 necessários. Definem a quais dados do usuário seu aplicativo terá acesso.
# calendar.readonly: Permite ler eventos do calendário do usuário.
# gmail.readonly: Permite ler emails do usuário.
# drive.readonly: Permite ler arquivos e metadados do Google Drive do usuário.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]

# --- Funções de Autenticação ---
def authenticate_google_oauth():
    creds = None
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'rb') as token:
                creds = pickle.load(token)
            print("Credenciais carregadas de credentials.pickle.")
        except Exception as e:
            print(f"Erro ao carregar credenciais do arquivo: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Credenciais expiradas, tentando refrescar...")
            try:
                creds.refresh(Request())
                print("Credenciais refrescadas com sucesso.")
            except Exception as e:
                print(f"Erro ao refrescar credenciais: {e}")
                creds = None

        if not creds or not creds.valid:
            print("Iniciando fluxo de autenticação OAuth 2.0...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                print("Fluxo de autenticação concluído.")
            except FileNotFoundError:
                print(f"Erro: Arquivo '{CLIENT_SECRETS_FILE}' não encontrado.")
                print("Por favor, baixe o arquivo client_secrets.json do Google Cloud Console e coloque-o no diretório correto.")
                return None
            except Exception as e:
                print(f"Erro durante o fluxo de autenticação: {e}")
                traceback.print_exc()
                return None

        if creds and creds.valid:
            try:
                with open(CREDENTIALS_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                print("Credenciais salvas em credentials.pickle.")
            except Exception as e:
                print(f"Erro ao salvar credenciais: {e}")

    if creds and creds.valid:
        print("Autenticação OAuth 2.0 bem-sucedida.")
        return creds
    else:
        print("Falha na autenticação OAuth 2.0.")
        return None

# --- Implementação para Interação com APIs do Google ---
class GoogleCalendarAPI:
    def __init__(self, credentials):
        self.service = None
        if credentials:
            try:
                self.service = build('calendar', 'v3', credentials=credentials)
                print("GoogleCalendarAPI inicializada.")
            except Exception as e:
                print(f"Erro ao inicializar GoogleCalendarAPI: {e}")
        else:
            print("Credenciais não fornecidas para GoogleCalendarAPI.")


    def get_upcoming_events(self, time_window_hours=24):
        if not self.service:
            print("Serviço Calendar não inicializado. Não foi possível buscar eventos.")
            return []

        now = datetime.now(UTC).isoformat()
        time_max = (datetime.now(UTC) + timedelta(hours=time_window_hours)).isoformat()

        print(f"Buscando eventos futuros nas próximas {time_window_hours} horas...")
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
        except Exception as e:
            print(f"Erro ao buscar eventos do Calendar: {e}")
            traceback.print_exc()
            return []

        if not events:
            print('Nenhum evento futuro encontrado.')
            return []

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            formatted_events.append({
                "summary": event.get('summary', 'Evento sem título'),
                "start": start,
                "end": end,
                "location": event.get('location'),
                "description": event.get('description')
            })
        return formatted_events

class GoogleGmailAPI:
    def __init__(self, credentials):
        self.service = None
        if credentials:
            try:
                self.service = build('gmail', 'v1', credentials=credentials)
                print("GoogleGmailAPI inicializada.")
            except Exception as e:
                print(f"Erro ao inicializar GoogleGmailAPI: {e}")
        else:
            print("Credenciais não fornecidas para GoogleGmailAPI.")

    def get_recent_emails(self, num_emails=10):
        if not self.service:
            print("Serviço Gmail não inicializado. Não foi possível buscar emails.")
            return []

        print(f"Buscando os últimos {num_emails} emails...")
        try:
            results = self.service.users().messages().list(userId='me', maxResults=num_emails).execute()
            messages = results.get('messages', [])
        except Exception as e:
            print(f"Erro ao buscar lista de emails do Gmail: {e}")
            traceback.print_exc()
            return []

        if not messages:
            print('Nenhum email encontrado.')
            return []

        formatted_emails = []
        for message in messages:
            try:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()

                headers = msg['payload']['headers']
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'Sem Assunto')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Remetente Desconhecido')
                date_sent = next((header['value'] for header in headers if header['name'] == 'Date'), 'Data Desconhecida')

                snippet = msg.get('snippet', 'Sem snippet')
                formatted_emails.append({
                    "id": message['id'],
                    "subject": subject,
                    "sender": sender,
                    "date": date_sent,
                    "snippet": snippet
                })
            except Exception as e:
                print(f"Erro ao obter detalhes do email {message['id']}: {e}")
                traceback.print_exc()
                continue 
        return formatted_emails

class GoogleDriveAPI:
    def __init__(self, credentials):
        self.service = None
        if credentials:
            try:
                self.service = build('drive', 'v3', credentials=credentials)
                print("GoogleDriveAPI inicializada.")
            except Exception as e:
                print(f"Erro ao inicializar GoogleDriveAPI: {e}")
        else:
            print("Credenciais não fornecidas para GoogleDriveAPI.")

    def get_recent_files(self, num_files=10):
        if not self.service:
            print("Serviço Drive não inicializado. Não foi possível buscar arquivos.")
            return []

        print(f"Buscando os últimos {num_files} arquivos no Drive...")
        try:
            thirty_days_ago = (datetime.now(UTC) - timedelta(days=30)).isoformat()
            query = f"modifiedTime > '{thirty_days_ago}'"
            results = self.service.files().list(
                pageSize=num_files,
                fields="nextPageToken, files(id, name, modifiedTime, mimeType)",
                orderBy="modifiedTime desc",
                q=query
            ).execute()
            items = results.get('files', [])
        except Exception as e:
            print(f"Erro ao buscar arquivos do Drive: {e}")
            traceback.print_exc()
            return []

        if not items:
            print('Nenhum arquivo recente encontrado no Drive.')
            return []

        formatted_files = []
        for item in items:
            formatted_files.append({
                "id": item.get('id'),
                "name": item.get('name'),
                "modifiedTime": item.get('modifiedTime'),
                "mimeType": item.get('mimeType')
            })
        return formatted_files

# --- Implementação para Interação com Gemini API ---

class GeminiAI:
    def __init__(self, api_key):
        self.model = None

        if not api_key or api_key == "SUA_CHAVE_GEMINI_AQUI":
            print("AVISO: Chave da Gemini API não configurada corretamente.")
            print("Certifique-se de que a variável de ambiente GOOGLE_API_KEY está definida com sua chave real.")
            return
        try:
            print("Configurando a Gemini API com a chave...")
            genai.configure(api_key=api_key)
            print("Cliente Gemini API configurado com sucesso.")

            print("Tentando obter o modelo Gemini...")
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("Modelo Gemini inicializado com sucesso.")
        except Exception as e:
            print(f"Erro ao inicializar GeminiAI ou obter modelo: {e}")
            traceback.print_exc()
            self.model = None

    def analyze_and_suggest(self, context_data):
        if not self.model:
            print("Modelo Gemini não disponível. Não foi possível gerar sugestão.")
            return "Erro: Modelo de IA não disponível."
        print("Enviando dados de contexto para a Gemini API para análise e sugestão...")

        # Formata os dados coletados para o prompt
        events_str = "\n".join([f"- {e.get('summary', 'Evento sem título')} em {e.get('start', 'Data desconhecida')}" for e in context_data.get('events', [])]) if context_data.get('events') else "Nenhum evento recente."
        emails_str = "\n".join([f"- Assunto: {e.get('subject', 'Sem Assunto')} (De: {e.get('sender', 'Remetente Desconhecido')})" for e in context_data.get('emails', [])]) if context_data.get('emails') else "Nenhum email recente."
        files_str = "\n".join([f"- {f.get('name', 'Arquivo sem nome')} (Modificado em: {f.get('modifiedTime', 'Data desconhecida')})" for f in context_data.get('drive_files', [])]) if context_data.get('drive_files') else "Nenhum arquivo recente no Drive."

        prompt = f"""
Você é um agente proativo que analisa a atividade recente do usuário em seus serviços Google (Agenda, Gmail, Drive)
e oferece sugestões úteis e concisas.

Analise os seguintes dados:

Eventos do Google Calendar (próximas 24h):
{events_str}

Emails recentes do Gmail (últimos 10):
{emails_str}

Arquivos recentes do Google Drive (últimos 10 modificados nos últimos 30 dias):
{files_str}

Com base nesses dados, identifique:
- Conflitos de agenda ou eventos importantes próximos.
- Possíveis itens de ação implícitos em emails (ex: responder a um email, seguir uma instrução).
- Oportunidades para ser proativo com base em arquivos recentes (ex: revisar um documento modificado recentemente, continuar trabalhando em um projeto).
- Qualquer outra informação relevante que possa exigir atenção do usuário.

Gere uma ou mais sugestões concisas para o usuário.
Se não houver sugestões claras ou nada relevante for encontrado, diga apenas "Tudo parece em ordem."

Formato da sugestão (use bullet points):
- [Tipo de Sugestão, ex: Agenda, Email, Drive, Geral]: [Texto da Sugestão]

Exemplos:
- Agenda: Você tem um evento importante "Reunião de Projeto" em 30 minutos.
- Email: O email com assunto "Feedback sobre o relatório" pode exigir uma resposta.
- Drive: O arquivo "Plano de Marketing Q3" foi modificado recentemente, talvez queira revisá-lo.
- Geral: Considere reservar um tempo para revisar os emails não lidos.
"""

        try:
            response = self.model.generate_content(contents=prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                print("Gemini API retornou uma resposta vazia.")
                return "Não foi possível gerar sugestão de IA no momento."
        except Exception as e:
            print(f"Erro ao chamar a Gemini API para gerar conteúdo: {e}")
            traceback.print_exc()
            return "Erro ao gerar sugestão de IA."


# --- Agente Proativo Principal ---

class ProactiveAgent:
    def __init__(self, google_credentials, gemini_api_key):
        self.calendar_api = GoogleCalendarAPI(google_credentials)
        self.gmail_api = GoogleGmailAPI(google_credentials)
        self.drive_api = GoogleDriveAPI(google_credentials)
        self.gemini_ai = GeminiAI(gemini_api_key)
        self.polling_interval_seconds = 60 * 15

    def collect_context_data(self):
        print("\n--- Coletando dados de contexto ---")
        events = self.calendar_api.get_upcoming_events() if self.calendar_api.service else []
        emails = self.gmail_api.get_recent_emails() if self.gmail_api.service else []
        drive_files = self.drive_api.get_recent_files() if self.drive_api.service else []
        print("--- Coleta de dados concluída ---\n")
        return {
            "events": events,
            "emails": emails,
            "drive_files": drive_files
        }

    def process_and_suggest(self, context_data):
        if not self.gemini_ai.model:
            print("Modelo Gemini não disponível para processamento.")
            return "Erro: Modelo de IA não disponível para gerar sugestões."

        suggestion = self.gemini_ai.analyze_and_suggest(context_data)
        return suggestion

    def present_suggestion(self, suggestion):
        if suggestion and suggestion.strip() and \
           suggestion.strip() != "Tudo parece em ordem." and \
           not suggestion.startswith("Erro:"):
            print("\n--- Sugestão do Agente Proativo ---")
            print(suggestion)
            print("-----------------------------------\n")
        elif suggestion and suggestion.strip() == "Tudo parece em ordem.":
            print("Nenhuma sugestão proativa no momento.")
        elif suggestion and suggestion.startswith("Erro:"):
            print(f"Ocorreu um erro ao gerar sugestão: {suggestion}")
        else:
             print("Sugestão recebida está vazia ou inválida.")


    def run(self):
        if not self.calendar_api.service and not self.gmail_api.service and not self.drive_api.service:
            print("Nenhum serviço Google inicializado. O agente não pode coletar dados.")
            return

        can_suggest = self.gemini_ai.model is not None
        if not can_suggest:
            print("Modelo Gemini não inicializado. O agente pode coletar dados, mas NÃO pode gerar sugestões de IA.")

        print(f"Agente Proativo iniciado. Verificando a cada {self.polling_interval_seconds} segundos...")
        try:
            while True:
                context_data = self.collect_context_data()

                if can_suggest:
                    suggestion = self.process_and_suggest(context_data)
                    self.present_suggestion(suggestion)
                else:
                    print("Dados coletados, mas modelo Gemini não disponível para sugestão.")

                print(f"Próxima verificação em {self.polling_interval_seconds} segundos...")
                time.sleep(self.polling_interval_seconds)
        except KeyboardInterrupt:
            print("\nAgente Proativo encerrado pelo usuário.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante a execução do agente: {e}")
            traceback.print_exc()


# --- Ponto de Entrada Principal ---

if __name__ == "__main__":
    print("Iniciando autenticação com Google OAuth 2.0...")
    google_credentials = authenticate_google_oauth()

    if not google_credentials:
        print("Não foi possível obter credenciais OAuth 2.0. Encerrando script.")
    else:
        print("\nObtendo chave da Gemini API da variável de ambiente GOOGLE_API_KEY...")
        gemini_api_key = os.getenv("GOOGLE_API_KEY")

        if not gemini_api_key or gemini_api_key == "SUA_CHAVE_GEMINI_AQUI":
            print("\nERRO: Variável de ambiente GOOGLE_API_KEY não definida ou ainda contém o placeholder.")
            print("Por favor, defina a variável de ambiente com sua chave da Gemini API real.")
            print("Exemplo (Linux/macOS): export GOOGLE_API_KEY='sua_chave'")
            print("Exemplo (Windows CMD): set GOOGLE_API_KEY=sua_chave")
            print("Encerrando script devido à falta da chave Gemini API.")
        else:
            print("Chave da Gemini API encontrada.")
            print("Inicializando Agente Proativo...")
            agent = ProactiveAgent(google_credentials, gemini_api_key)
            agent.run()