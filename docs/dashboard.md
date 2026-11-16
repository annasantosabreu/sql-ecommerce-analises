# Dashboard executivo

## Escopo

O painel usa oito consultas SQL independentes em `sql/03_dashboard/` e gera um arquivo JSON com dados consultados diretamente no PostgreSQL.

### Definições dos indicadores

- **Faturamento entregue:** soma de preço dos itens e frete de pedidos com status `entregue`.
- **Pedidos entregues:** quantidade de pedidos com status `entregue`.
- **Ticket médio:** faturamento entregue dividido pela quantidade de pedidos entregues no período.
- **Prazo médio:** média de dias entre compra e entrega para pedidos entregues, considerando toda a base.
- **Faturamento mensal:** agrupado pelo mês da compra, somente pedidos entregues.
- **Faturamento por categoria/UF:** soma de preço dos itens e frete, atribuída à categoria do produto ou ao estado do cliente.
- **Ranking de vendedores:** soma do preço dos produtos (sem frete) em pedidos entregues.
- **Atraso médio:** média do atraso positivo entre data de entrega e data estimada, por UF do cliente.
- **Meios de pagamento:** valor e quantidade de pedidos entregues por tipo de pagamento.

O filtro de período da interface atua sobre as séries mensais e sobre os KPIs calculados a partir delas. Os demais quadros apresentam o recorte completo da base. O prazo médio exibido no cartão também considera a base completa.

## Executar localmente

1. Instale as dependências e prepare o banco conforme as instruções principais do README.
2. Copie `.env.example` para `.env` e configure a senha local.
3. Gere os CSVs, suba o PostgreSQL, crie o esquema e carregue os dados.
4. Com o banco acessível em `localhost:5432`, execute:

```bash
python -m pip install -r generator/requirements.txt
python -m dashboard.exportar
```

O exportador lê as configurações do arquivo `.env` e grava `data/dashboard.json`. O arquivo gerado não contém credenciais e não deve ser tratado como dado real.

Abra `dashboard/index.html` por um servidor HTTP local. Por exemplo, na raiz do projeto:

```bash
python -m http.server 8000
```

Acesse `http://localhost:8000/dashboard/`. Abrir o HTML diretamente via `file://` pode bloquear a leitura do JSON pelo navegador.

## Atualização

Execute novamente `python -m dashboard.exportar` depois de atualizar a carga no PostgreSQL. Para automatizar a atualização em GitHub Actions, o banco precisa estar acessível ao runner e as credenciais devem ser configuradas como GitHub Secrets. O PostgreSQL local em Docker não fica acessível à nuvem automaticamente.

## Validação

Os testes estruturais do pacote podem ser executados com:

```bash
python -m unittest discover -s tests -v
```

A execução dos testes não substitui a validação das consultas no PostgreSQL. Antes de divulgar resultados, execute o exportador com a base carregada e confira os totais diretamente no banco.
