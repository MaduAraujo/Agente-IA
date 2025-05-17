# ✨ Agente Proativo Pessoal: Conectando Seus Dados Google com a Inteligência Artificial ✨

![Python Version](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green) 

## O que faz?

Um agente que, com permissão do usuário, monitora suas ferramentas (Calendário, Gmail, Google Drive) e sugere tarefas ou informações relevantes sem ser explicitamente perguntado, 
agindo de forma semi-autônoma ou proativa.


## Recursos Principais

- 🔒 Autenticação Segura: Implementa o fluxo padrão OAuth 2.0 do Google para acesso seguro aos seus dados, com armazenamento local e seguro das credenciais (token).
- 📅 Monitoramento de Agenda: Busca e informa sobre eventos próximos no Google Calendar.
- 📧 Análise de Emails Recentes: Examina metadados dos emails mais recentes no Gmail para identificar potenciais ações ou informações importantes.
- 📁 Rastreamento de Arquivos no Drive: Lista arquivos modificados recentemente no Google Drive, ajudando você a retomar trabalhos pendentes ou revisar documentos.
- 🧠 Análise Contextual com Gemini API: Envia os dados coletados (eventos, emails, arquivos) para a API Gemini para uma análise holística.
- 💡 Sugestões Inteligentes: Receba sugestões concisas e acionáveis geradas pela IA com base no seu contexto digital atual.
- 🔄 Execução Contínua: Roda em segundo plano (no terminal), verificando periodicamente seus serviços Google para fornecer alertas e sugestões em tempo real.

## Tecnologias Utilizadas

- Python 3.6+: Linguagem de programação principal utilizada para o desenvolvimento do agente.
- Google APIs: Utilizadas para acessar dados do Google Calendar, Gmail e Drive.
- OAuth 2.0: Protocolo de autenticação para garantir acesso seguro aos dados do usuário.
- Gemini API: API utilizada para análise contextual e geração de sugestões.
- Terminal: Ambiente de execução do agente, permitindo operação em segundo plano.

## Demonstração

Veja o Agente Proativo Pessoal em ação, mostrando o fluxo de autenticação, a coleta de dados e a apresentação de sugestões pela IA diretamente no console:

https://github.com/user-attachments/assets/02c16e0a-035e-4bec-a2f3-0afb8d4e014e

## Como Funciona: O Ciclo Proativo

**1. Coleta de Dados:** O agente se autentica com suas credenciais Google e acessa as APIs do Calendar, Gmail e Drive para coletar dados recentes (próximos eventos, emails recentes, arquivos modificados).<br>
**2. Formatação e Envio para IA:** Os dados coletados são formatados em um prompt claro e conciso. Este prompt, juntamente com a requisição para gerar conteúdo, é enviado para a Gemini API.<br>
**3. Análise e Geração de Sugestão:** O modelo Gemini processa o prompt, identifica padrões, correlações e possíveis necessidades de atenção com base nos dados fornecidos e gera uma resposta estruturada com sugestões.<br>
**4. Apresentação da Sugestão:** A resposta da Gemini é recebida pelo agente e exibida no console.

Este ciclo se repete automaticamente em um intervalo predefinido, mantendo você atualizado proativamente.
