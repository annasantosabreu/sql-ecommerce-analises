# Exportação dos resultados para o dashboard

O `index.html` é uma página estática: ele não se conecta diretamente ao PostgreSQL. O script abaixo executa as consultas SQL localmente e grava somente os resultados agregados em `data/dashboard.json`.

## 1. Pré-requisitos

- Docker Desktop aberto e container `banco` em execução.
- Banco `ecommerce` criado e carregado.
- Arquivo `.env` configurado na raiz.

## 2. Instalar a dependência

Na raiz do repositório:

```powershell
python -m pip install -r dashboard/requirements.txt
```

## 3. Exportar os resultados

```powershell
python dashboard/exportar_dashboard.py
```

O script executa as oito consultas em `sql/03_analises/` e cria `data/dashboard.json`.

## 4. Visualizar localmente

Na raiz do projeto:

```powershell
python -m http.server 8000
```

Abra `http://localhost:8000`.

> Abrir o `index.html` com duplo clique pode bloquear a leitura do JSON pelo navegador. Use o servidor local acima.

## 5. Publicar no GitHub Pages

Depois de revisar o JSON e confirmar que ele contém apenas resultados agregados:

1. Adicione `index.html`, `dashboard/`, `sql/03_analises/` e `data/dashboard.json` à branch de trabalho.
2. Faça commit e push.
3. Em GitHub → Settings → Pages, selecione a branch e a pasta `/ (root)`.

## Atualização dos dados

Sempre que a base mudar, execute novamente `python dashboard/exportar_dashboard.py` e publique o JSON atualizado.

## Segurança e privacidade

- Não publique `.env`, senhas, dumps do banco ou CSVs individuais.
- O JSON contém agregações, sem dados pessoais ou registros de pedidos individuais.
- O navegador não recebe credenciais e não acessa o PostgreSQL.
- Os dados são sintéticos e a página informa essa condição.
