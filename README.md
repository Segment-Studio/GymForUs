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