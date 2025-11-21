# 📊 Certificates Monitor

Sistema de monitoramento em tempo real de geração e envio de certificados.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🎯 Sobre o Projeto

O **Certificates Monitor** é uma aplicação web desenvolvida em Flask que fornece visualização e análise de dados, oferecendo insights sobre certificados gerados, falhas no sistema e métricas operacionais.

### ✨ Funcionalidades

- 📈 **Dashboard Interativo** com métricas em tempo real
- 📜 **Gestão de Certificados** com listagem paginada e filtros
- ⚠️ **Monitoramento de Falhas** na fila de processamento
- 📊 **Gráficos de Evolução** temporal de certificados
- 🔄 **Auto-atualização** automática a cada 5 minutos
- 🔐 **Conexão Segura** via túnel SSH

---

## 🛠️ Tecnologias Utilizadas

### Backend

- **Python 3.12+**
- **Flask 3.0** - Framework web
- **PyMySQL** - Conector MySQL
- **Paramiko** - Cliente SSH
- **SSHTunnel** - Túnel SSH para MySQL
- **APScheduler** - Agendamento de tarefas

### Frontend

- **HTML5 / CSS3**
- **Chart.js** - Gráficos interativos
- **Jinja2** - Template engine

### Infraestrutura

- **MySQL 8.0** - Banco de dados
- **SSH** - Acesso seguro ao servidor

---

## 📂 Estrutura do Projeto

```
certificates-monitor/
├── config/
│   ├── config.py             # Template de configurações
│   └── queries.py            # Queries SQL centralizadas
├── models/
│   └── database.py           # Modelos de dados
├── static/
│   └── css/
│       └── style.css         # Estilos customizados
├── templates/
│   ├── dashboard.html        # Dashboard principal
│   ├── certificates.html     # Página de certificados
│   └── failures.html         # Página de falhas
├── utils/
│   ├── mysql_monitor.py      # Monitor principal MySQL
│   └── ssh_client.py         # Cliente SSH e túnel
├── .env.example              # Template de variáveis de ambiente
├── .gitignore
├── app.py                    # Aplicação Flask principal
├── LICENSE
├── pyproject.toml            # Dependências Python (Poetry)
├── README.md
└── requirements.txt          # Dependências Python
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.12 ou superior
- Acesso SSH ao servidor
- Credenciais do banco MySQL

### 1. Clone o repositório

```bash
git clone https://github.com/rodineicosta/certificates-monitor.git
cd certificates-monitor
```

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
# ou
poetry install
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# SSH Configuration
SSH_HOST=seu-servidor.com
SSH_PORT=22
SSH_USERNAME=seu_usuario
SSH_PASSWORD=sua_senha

# Database Configuration
DB_USERNAME=db_usuario
DB_PASSWORD=db_senha
DB_DATABASE=db_nome
DB_PORT=3306
```

### 5. Execute a aplicação

```bash
python app.py
```

Acesse: [http://localhost:5001](http://localhost:5001)

---

## 📊 Funcionalidades Detalhadas

### Dashboard Principal

- **Cards de Métricas:**
  - Total de Certificados
  - Falhas de Processamento
  - Total de Alunos
  - Membros da Equipe

- **Gráfico de Evolução:**
  - Certificados gerados nos últimos 7 dias
  - Visualização em linha temporal

- **Verificações de Integridade:**
  - Certificados sem template
  - Templates inválidos (legados)

### Página de Certificados

- Listagem completa de certificados
- Informações: ID, Aluno, Curso, Status, Data de Criação
- Badges coloridos por status
- Paginação e ordenação por data

### Página de Falhas

- Tarefas com erro na fila de processamento
- Detalhes: ID, Aluno, Curso, Certificado, Tentativas, Última Atualização
- Paginação e ordenação por data

---

## 🔧 Configuração Avançada

### Alterar Intervalo de Atualização

No arquivo `app.py`:

```python
scheduler.add_job(
    func=update_monitoring_data,
    trigger="interval",
    minutes=5,  # Altere aqui (padrão: 5 minutos)
    ...
)
```

### Ajustar Quantidade de Registros por Página

Nos arquivos `app.py` (rotas `/certificates` e `/failures`):

```python
per_page = 10  # Altere aqui
```

---

## 📈 Roadmap Futuro

- [ ] Sistema de autenticação
- [ ] Exportação de relatórios
- [ ] Sistema de logs estruturado
- [ ] Alertas via email/Slack/Telegram
- [ ] API REST
- [ ] Testes automatizados
- [ ] Dashboard analytics avançado

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer *fork* do projeto
2. Criar uma *branch* para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Enviar para a *branch* (`git push origin feature/AmazingFeature`)
5. Abrir um *Pull Request*

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Rodinei Costa**

- GitHub: [@rodineicosta](https://github.com/rodineicosta)
- LinkedIn: [Rodinei Costa](https://linkedin.com/in/rodineicosta)

---

## 🙏 Agradecimentos

- Comunidade Flask
- Chart.js

---

**Desenvolvido com ❤️ para monitoramento eficiente de certificados digitais.**
