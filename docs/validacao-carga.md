# Etapa (b) — carga e qualidade

## Preparacao

1. Copie `.env.example` para `.env` e altere `POSTGRES_PASSWORD` para uma senha local.
2. Gere os CSVs com `python -m generator.gerar_dados`.
3. Confirme que os oito CSVs e o `manifesto.json` estao em `data/gerados/`.
4. Abra o Docker Desktop e aguarde o mecanismo ficar em execucao.

## Subir PostgreSQL 16

```powershell
docker compose up -d
docker compose ps
```

A coluna de estado deve indicar que o servico esta saudavel (`healthy`).

## Criar tabelas e carregar CSVs

```powershell
docker compose exec banco psql -U ecommerce -d ecommerce -f /sql/00_schema.sql
docker compose exec banco psql -U ecommerce -d ecommerce -f /sql/01_carga.sql
```

Os comandos acima usam os valores padrao de usuario e banco definidos no `docker-compose.yml`. Se voce personalizar `POSTGRES_USER` ou `POSTGRES_DB` no `.env`, substitua `ecommerce` pelos valores escolhidos.

## Rodar verificacoes de qualidade

```powershell
docker compose exec banco psql -U ecommerce -d ecommerce -f /sql/02_qualidade.sql
```

Esperado: zero pedidos sem itens, zero pedidos sem pagamento, zero divergencias entre pagamento e itens + frete, zero avaliacoes de pedidos nao entregues e zero datas invalidas. Entregas sem aprovacao e pedidos sem avaliacao sao ocorrencias intencionais e devem ser apenas quantificados/documentados.

## Consultar contagens

```powershell
docker compose exec banco psql -U ecommerce -d ecommerce -c "SELECT 'pedidos' AS tabela, COUNT(*) FROM pedidos;"
```

## Observacoes

- O servico monta `data/gerados/` somente para leitura em `/dados`.
- Os CSVs nao devem ser versionados no Git.
- O volume `postgres_data` persiste o banco entre reinicializacoes. Para apagar os dados do banco e recriar tudo do zero, use `docker compose down -v`; isso apaga o volume local do PostgreSQL.
- Os dados sao sinteticos e nao representam operacoes de uma empresa real.
