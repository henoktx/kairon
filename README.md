### KaironAPP - Sistema de Agendamento e Execução de Tarefas com Django e Temporal.io

#### Arquitetura Proposta

O sistema é composto por dois grandes blocos: **KaironAPP** (aplicação Django) e **Serviços Externos** (incluindo o Temporal.io).  
A arquitetura é orientada a microsserviços, com integração entre Django, Temporal.io e serviços auxiliares como envio de e-mails.

- **KaironAPP (Django):**
  - **NotificationsAPP:** Responsável pelo envio de notificações (ex: e-mails).
  - **ReportsAPP:** Geração de relatórios.
  - **WorkflowAPP:** Criação e gerenciamento de workflows.
  - **ExecutionsAPP:** Gerenciamento da execução de tarefas e workflows.
  - **UsersAPP:** Gerenciamento de usuários.
  - **TemporalAPP:** Camada de integração com o Temporal.io, responsável por iniciar, agendar e resetar workflows, além de executar atividades e workers.

- **Serviços Externos:**
  - **Temporal.io:** Orquestração de workflows e atividades assíncronas.
    - **TemporalServer:** Servidor principal do Temporal.
    - **TemporalWorker:** Executores das atividades.
    - **TemporalDatabase:** Persistência dos estados dos workflows.
  - **MailerSender:** Serviço externo para envio de e-mails.
  - **PostgreSQL:** Banco de dados principal da aplicação Django.

O fluxo principal envolve a criação de workflows via Django, que são orquestrados pelo Temporal.io, com persistência no PostgreSQL e notificações enviadas por serviços externos.

---

#### Instruções de Deploy Local (Sem Docker)

**Requisitos:**

- **Python 3.10+**
- **PostgreSQL 13+**
- **Temporal CLI e Server** ([instalação oficial](https://docs.temporal.io/temporal-cli))
- **[Temporal Python SDK](https://python.temporal.io/)**
- **uv (opcional, para ambiente virtual leve)**

**1. Instale o PostgreSQL**

- Instale o PostgreSQL conforme seu sistema operacional.
- Crie o banco e usuário:

```bash
sudo -u postgres psql
CREATE DATABASE kairon;
\q
```

**2. Instale o Temporal Server**

- Siga as instruções oficiais: [Temporal Quick Install](https://docs.temporal.io/server/quick-install)
- Exemplo para rodar localmente (usando o Temporal CLI):

```bash
temporal server start-dev
```

Isso inicia o Temporal Server e o Temporal Web UI (por padrão em http://localhost:8233).

**3. Clone o projeto e crie o ambiente Python**

```bash
git clone https://github.com/seu-usuario/kairon.git
cd kairon
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se preferir, pode usar o [uv](https://github.com/astral-sh/uv) para instalar dependências rapidamente:

```bash
uv pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` com as configurações do banco e do Temporal, por exemplo:

```
DATABASE_URL=postgres://kairon:kairon@localhost:5432/kairon
TEMPORAL_ADDRESS=localhost:7233
```

**5. Execute as migrações do Django**

```bash
python manage.py migrate
```

**6. Inicie o Worker do Temporal**

O projeto possui um comando customizado para rodar o worker:

```bash
python manage.py runworker
```

**7. Inicie o servidor Django**

```bash
python manage.py runserver 
```

**Ordem recomendada de inicialização:**

1. Temporal Server  
   `temporal server start-dev --db-filename temporal.db`
2. Worker  
   `python manage.py runworker`
3. Django  
   `python manage.py runserver`

---

#### Explicação Detalhada da Modelagem

A modelagem do sistema foi pensada para garantir rastreabilidade, reprocessamento e escalabilidade das execuções, aproveitando o Temporal.io para orquestração e resiliência.

**Principais modelos:**

- **Workflow:**  
  Representa um fluxo de trabalho configurável, que pode ser agendado e executado. Contém informações como nome, descrição, parâmetros de entrada e status.  
  Permite versionamento e reutilização de fluxos.

- **Execution:**  
  Cada vez que um workflow é disparado, uma instância de Execution é criada.  
  Armazena o status da execução (em andamento, finalizado, com erro, etc), timestamps de início/fim, referência ao workflow original e ao usuário responsável.

- **TaskExecution:**  
  Representa a execução de uma tarefa individual dentro de um workflow.  
  Permite rastrear o progresso granular, status, logs e resultados de cada etapa do workflow.

- **User:**  
  Usuários do sistema, com informações de autenticação, permissões e associação a execuções e workflows.

- **Notification/Report:**  
  Modelos auxiliares para envio de notificações (ex: e-mail) e geração de relatórios automáticos, integrados ao ciclo de vida das execuções.

**Relacionamentos:**

- Um **Workflow** pode ter várias **Executions**.
- Uma **Execution** pode ter várias **TaskExecutions**.
- Um **User** pode ser responsável por vários **Workflows** e **Executions**.

**Exemplo de fluxo:**

1. Usuário cria um Workflow.
2. Workflow é disparado, criando uma Execution.
3. Execution dispara várias TaskExecutions, cada uma representando uma etapa do processo.
4. A Execution é startada manualmente.
5. O progresso e status são atualizados em tempo real, com logs e notificações.
6. Ao final, relatórios podem ser gerados e enviados.
7. Em caso de falha, a Execution pode ser resetada.

Essa modelagem permite rastreabilidade completa, reprocessamento de execuções, auditoria e integração fácil com o Temporal.io.

---

#### Explicação do Uso do Temporal.io

O **Temporal.io** é utilizado como motor de orquestração de workflows assíncronos e tolerantes a falhas.

- **Workflows** são definidos na camada Django e disparados via integração com o TemporalAPP.
- **Activities** são as tarefas atômicas executadas pelos workers do Temporal.
- **Workers** ficam escutando por novas execuções e processam as atividades.
- O **TemporalServer** gerencia o estado dos workflows, garantindo reexecução em caso de falhas e persistência dos estados.
- O **TemporalDatabase** armazena o histórico e estado dos workflows.
- O Django interage com o Temporal via SDK (Python), disparando workflows, agendando execuções e monitorando estados.

**Principais vantagens do uso do Temporal.io:**

- Orquestração robusta de tarefas distribuídas.
- Garantia de execução (mesmo em caso de falhas).
- Observabilidade e rastreabilidade dos workflows.
- Facilidade para reprocessar ou resetar execuções.

---

#### Referências

- [Temporal.io Documentation](https://docs.temporal.io/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Temporal Python SDK](https://python.temporal.io/)
- [uv - Python package manager](https://github.com/astral-sh/uv)

---