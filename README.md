# Campeonato Amador

Sistema web em Django para gerenciar um campeonato de futebol amador: times, jogadores, árbitros, partidas e gols.

O relatório completo está em `docs/Relatorio_Campeonato_Amador.pdf`.

## Requisitos

- **Python 3.12 ou mais novo** (o Django 6.1 não funciona em versões anteriores). Para conferir: `python --version`

## Como executar (Windows)

Dentro da pasta do projeto:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Acesse **http://127.0.0.1:8000**

> Se o PowerShell bloquear o `activate`, rode antes: `Set-ExecutionPolicy -Scope Process Bypass`
> (ou use o Prompt de Comando, o `cmd`, no lugar do PowerShell).

O banco `db.sqlite3` já vem com dados de exemplo e com os usuários abaixo.
Se precisar recriar os usuários: `python manage.py criar_usuarios`

## Usuários de teste

| Usuário | Senha | Nível |
|---|---|---|
| admin | admin123 | admin: vê, cadastra, edita e exclui (também entra no painel `/admin`) |
| usuario | usuario123 | user: só visualiza |

## Testes

```
python manage.py test
```
