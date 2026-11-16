\set ON_ERROR_STOP on

-- A carga usa os CSVs montados pelo Docker em /dados.
-- O delimitador ; corresponde ao formato produzido pelo gerador Python.

TRUNCATE TABLE
    avaliacoes,
    pagamentos,
    itens_pedido,
    pedidos,
    produtos,
    categorias,
    vendedores,
    clientes;

\copy clientes (id, cidade, estado, data_cadastro) FROM '/dados/clientes.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy vendedores (id, cidade, estado, data_cadastro) FROM '/dados/vendedores.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy categorias (id, nome) FROM '/dados/categorias.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy produtos (id, categoria_id, nome, preco_base, peso_g) FROM '/dados/produtos.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy pedidos (id, cliente_id, status, data_compra, data_aprovacao, data_envio, data_entrega, data_estimada_entrega) FROM '/dados/pedidos.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy itens_pedido (pedido_id, sequencia, produto_id, vendedor_id, preco, frete) FROM '/dados/itens_pedido.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy pagamentos (pedido_id, sequencia, tipo, parcelas, valor) FROM '/dados/pagamentos.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')
\copy avaliacoes (id, pedido_id, nota, comentario_curto, data_avaliacao) FROM '/dados/avaliacoes.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', NULL '')

ANALYZE;

SELECT 'clientes' AS tabela, COUNT(*) AS registros FROM clientes
UNION ALL SELECT 'vendedores', COUNT(*) FROM vendedores
UNION ALL SELECT 'categorias', COUNT(*) FROM categorias
UNION ALL SELECT 'produtos', COUNT(*) FROM produtos
UNION ALL SELECT 'pedidos', COUNT(*) FROM pedidos
UNION ALL SELECT 'itens_pedido', COUNT(*) FROM itens_pedido
UNION ALL SELECT 'pagamentos', COUNT(*) FROM pagamentos
UNION ALL SELECT 'avaliacoes', COUNT(*) FROM avaliacoes
ORDER BY tabela;
