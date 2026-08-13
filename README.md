# 🏋️ GymForUs
> **Plataforma inteligente de planejamento fitness e nutrição orientada por IA.**

O **GymForUs** é uma aplicação SaaS desenvolvida pela **Segment Studio** que combina inteligência artificial, regras de segurança fitness e um painel intuitivo para oferecer rotinas de treino e nutrição personalizadas, promovendo evolução constante sem prescrições extremas ou inseguras.

---

## ✨ Principais Funcionalidades

- **🎯 Planejamento Baseado em Objetivos:** Algoritmos adaptados para hipertrofia, emagrecimento e ganho de força.
- **🤖 Motor de IA com Safety-Fallback:** Geração de treinos por IA com sistema de segurança e contingência baseado em regras.
- **📊 Dashboard do Usuário:** Acompanhamento de progresso, histórico de planos salvos e perfil personalizado.
- **🔒 Segurança & Privacidade:** Autenticação robusta, criptografia de dados e proteção de rotas.
- **📱 Interface Moderna:** Design responsivo no estilo *dark mode*, otimizado para desktop e dispositivos móveis.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12, Flask 3.0, SQLite
- **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Jinja2 Templates)
- **Engine de IA:** API de LLM integrada com lógica server-side e fallback
- **Testes & Qualidade:** Pytest

---

## 📂 Estrutura do Projeto

```text
GymForUs/
├── ai/         # Módulos de integração e lógica de fallback da IA
├── backend/    # Rotas de API, autenticação e banco de dados
├── config/     # Configurações de ambiente da aplicação
├── frontend/   # Templates visuais e ativos estáticos
├── tests/      # Suíte de testes automatizados
└── utils/      # Utilitários de validação e cálculos métricos
```

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.12+
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/Segment-Studio/GymForUs.git
cd GymForUs

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Copie o arquivo de variáveis de ambiente
cp .env.example .env

# 5. Preencha o .env com suas configurações (veja seção abaixo)

# 6. Rode a aplicação
flask run
```

A aplicação estará disponível em `http://127.0.0.1:5000`.

---

## 🔑 Variáveis de Ambiente

Copie o `.env.example` para `.env` e configure os valores conforme sua necessidade:

| Variável | Descrição | Exemplo |
|---|---|---|
| `HOST` | Host onde a aplicação vai rodar | `127.0.0.1` |
| `PORT` | Porta local da aplicação | `5000` |
| `DEBUG` | Ativa modo debug do Flask | `false` |
| `SECRET_KEY` | Chave secreta do Flask (sessões, CSRF, etc) | *gere uma chave única* |
| `SESSION_COOKIE_SECURE` | Exige HTTPS para cookies de sessão | `false` (local) / `true` (produção) |
| `CORS_ALLOWED_ORIGINS` | Origens permitidas via CORS | `http://127.0.0.1:5000,http://localhost:5000` |
| `AI_PROVIDER` | Provedor de IA usado (`rule-based` para fallback sem IA externa) | `rule-based` ou `openai` |
| `AI_API_URL` | URL do endpoint da API de IA | *depende do provedor* |
| `AI_API_KEY` | Chave de API do provedor de IA | *sua chave secreta* |
| `AI_MODEL` | Modelo de IA a ser usado | `gpt-4o-mini` |
| `AI_TIMEOUT_SECONDS` | Timeout para chamadas à IA | `12` |
| `AI_FALLBACK_ENABLED` | Ativa o sistema de fallback baseado em regras caso a IA falhe | `true` |
| `RATE_LIMIT_REQUESTS` | Número máximo de requisições por janela | `60` |
| `RATE_LIMIT_WINDOW_SECONDS` | Duração da janela de rate limit (segundos) | `60` |

> ⚠️ **Importante:** nunca envie o arquivo `.env` para o repositório. Ele já deve estar listado no `.gitignore`. Use o `.env.example` apenas como referência de estrutura.

---

## ☁️ Deploy no Vercel

O GymForUs foi projetado para ser facilmente espelhado e implantado na Vercel.

### 1. Faça o fork/clone do repositório
Espelhe este repositório para a sua conta no GitHub (ou faça deploy direto a partir do seu fork).

### 2. Importe o projeto na Vercel
- Acesse [vercel.com/new](https://vercel.com/new)
- Selecione o repositório do GymForUs
- A Vercel deve detectar automaticamente o projeto Python/Flask (via `vercel.json` ou configuração equivalente no repositório)

### 3. Configure as variáveis de ambiente
No painel do projeto na Vercel, vá em **Settings → Environment Variables** e adicione as variáveis listadas na seção acima — principalmente:
- `SECRET_KEY`
- `AI_PROVIDER`
- `AI_API_URL`
- `AI_API_KEY`
- `AI_MODEL`

> Em produção, recomenda-se `SESSION_COOKIE_SECURE=true` e ajustar `CORS_ALLOWED_ORIGINS` para o domínio final da aplicação.

### 4. Deploy
Clique em **Deploy**. A Vercel vai buildar e publicar a aplicação automaticamente a cada push na branch principal.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas alterações (`git commit -m 'Adiciona minha feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é desenvolvido e mantido pela **Segment Studio**. Verifique o arquivo `LICENSE` no repositório para mais detalhes sobre os termos de uso.
