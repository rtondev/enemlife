# ENEMPRO - Sistema de Preparação para ENEM

Sistema web desenvolvido para auxiliar estudantes na preparação para o Exame Nacional do Ensino Médio (ENEM), oferecendo funcionalidades de organização de estudos, criação de simulados, gerenciamento de questões e flashcards.

## Sobre o Projeto

O ENEMPRO é uma plataforma completa de estudos que permite aos usuários:
- Organizar conteúdos de estudo (vídeos, artigos, links)
- Criar e gerenciar flashcards personalizados
- Desenvolver simulados personalizados com questões próprias
- Compartilhar questões públicas com outros usuários
- Acompanhar estatísticas de progresso
- Gerenciar perfil e dados pessoais

## Tecnologias Utilizadas

- **Backend:** Python 3.x, Flask
- **Banco de Dados:** SQLite
- **Autenticação:** JWT (JSON Web Tokens)
- **Frontend:** HTML, CSS, JavaScript
- **Bibliotecas:** Flask-SQLAlchemy, Flask-JWT-Extended, Werkzeug

## Instalação

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passos para Instalação



2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute o aplicativo:
```bash
python app.py
```

6. Acesse o sistema em: `http://localhost:5000`

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional):
```
SECRET_KEY=sua-chave-secreta-aqui
JWT_SECRET_KEY=sua-chave-jwt-aqui
```

### Banco de Dados

O banco de dados SQLite será criado automaticamente na primeira execução. O arquivo `enempro.db` será gerado na pasta `instance/`.

### Usuário Administrador Padrão

- Email: `admin@enempro.com`
- Senha: `admin123`

**IMPORTANTE:** Altere a senha do administrador em produção!

## Uso

### Cadastro de Usuário

1. Acesse a página de cadastro
2. Preencha todos os campos obrigatórios
3. Aceite os termos de uso
4. Faça login com suas credenciais

### Funcionalidades Principais

- **Conteúdos:** Adicione links de vídeos, artigos e materiais de estudo
- **Flashcards:** Crie cards de revisão com informações importantes
- **Simulados:** Monte simulados personalizados com suas questões
- **Questões:** Crie questões próprias e compartilhe com a comunidade
- **Perfil:** Gerencie suas informações pessoais

## Testes

Para executar os testes (quando implementados):
```bash
pytest
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Merge Request

## Licença

Este projeto está licenciado sob a Licença GPL v3 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Equipe

- Clayton Rennan

## Contato

Para dúvidas ou sugestões, entre em contato através do GitLab Issues.

## Links Úteis

- [Documentação do Flask](https://flask.palletsprojects.com/)
- [Documentação do SQLAlchemy](https://docs.sqlalchemy.org/)
- [GitLab do Projeto](https://gitlab.com/seu-usuario/enempro)

---

**Desenvolvido como parte da disciplina de Análise e Projeto Orientados a Objetos**

