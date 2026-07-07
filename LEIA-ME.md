# Dashboard — Estatística de uso do Microsoft Copilot (MPPA)

Dashboard web em Python (Streamlit), responsivo para celulares, com uma aba
para cada arquivo CSV e filtros interativos em todas as abas.

## Como executar (com uv)

1. Instale o uv (se ainda não tiver). No Windows (PowerShell):

   ```
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Na pasta do projeto, execute:

   ```
   uv run dashboard.py
   ```

Pronto. O uv cria o ambiente e instala as dependências automaticamente
(estão declaradas dentro do próprio `dashboard.py`, no cabeçalho PEP 723 —
não é preciso pip nem requirements).

O navegador abre em `http://locYalhost:8501`.
Para acessar do celular na mesma rede: `http://SEU-IP:8501`.

Alternativa equivalente:

```
uv run streamlit run dashboard.py
```

## Estrutura

| Arquivo | Aba |
|---|---|
| agentes.csv | 🤖 Agentes |
| usuarios-e-agentes.csv | 👥 Usuários e Agentes |
| usuarios-uso-agentes.csv | 📈 Uso de Agentes por Usuário |
| uso-copilot-chat.csv | 💬 Copilot Chat |
| uso-copilot.csv | 🧩 Copilot M365 |

## Filtros

Cada aba tem um painel "🔎 Filtros" com parâmetros específicos (usuário,
agente, tipo de criador, mínimo de prompts/respostas, faixa de dias ativos,
aplicativo com atividade e período da última atividade). KPIs, gráficos e
tabelas respondem aos filtros, e os dados filtrados podem ser baixados em CSV.

## Atualizar os dados

Basta substituir os 5 arquivos CSV na pasta (mantendo os mesmos nomes) e
recarregar a página (menu ⋮ → Rerun, ou tecla R).
