-- Esquema relacional do projeto SQL E-commerce Analises.
-- Compatibilidade: PostgreSQL 16.
-- Os dados carregados neste banco sao integralmente sinteticos.

BEGIN;

CREATE TABLE IF NOT EXISTS clientes (
    id              BIGINT PRIMARY KEY,
    cidade          VARCHAR(100) NOT NULL CHECK (BTRIM(cidade) <> ''),
    estado          CHAR(2) NOT NULL CHECK (estado IN (
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    )),
    data_cadastro   TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS vendedores (
    id              BIGINT PRIMARY KEY,
    cidade          VARCHAR(100) NOT NULL CHECK (BTRIM(cidade) <> ''),
    estado          CHAR(2) NOT NULL CHECK (estado IN (
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    )),
    data_cadastro   TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS categorias (
    id              BIGINT PRIMARY KEY,
    nome            VARCHAR(80) NOT NULL UNIQUE CHECK (BTRIM(nome) <> '')
);

CREATE TABLE IF NOT EXISTS produtos (
    id              BIGINT PRIMARY KEY,
    categoria_id    BIGINT NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    nome            VARCHAR(160) NOT NULL CHECK (BTRIM(nome) <> ''),
    preco_base      NUMERIC(12, 2) NOT NULL CHECK (preco_base > 0),
    peso_g          INTEGER NOT NULL CHECK (peso_g > 0)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id                      BIGINT PRIMARY KEY,
    cliente_id              BIGINT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    status                  VARCHAR(20) NOT NULL CHECK (status IN (
        'entregue', 'cancelado', 'em_transporte', 'indisponivel', 'aprovado'
    )),
    data_compra             TIMESTAMP NOT NULL,
    data_aprovacao          TIMESTAMP,
    data_envio              TIMESTAMP,
    data_entrega            TIMESTAMP,
    data_estimada_entrega   TIMESTAMP NOT NULL,
    CONSTRAINT ck_pedidos_aprovacao_posterior_compra
        CHECK (data_aprovacao IS NULL OR data_aprovacao >= data_compra),
    CONSTRAINT ck_pedidos_envio_posterior_aprovacao
        CHECK (data_envio IS NULL OR data_envio >= COALESCE(data_aprovacao, data_compra)),
    CONSTRAINT ck_pedidos_entrega_posterior_envio
        CHECK (data_entrega IS NULL OR (data_envio IS NOT NULL AND data_entrega >= data_envio)),
    CONSTRAINT ck_pedidos_previsao_posterior_compra
        CHECK (data_estimada_entrega >= data_compra),
    CONSTRAINT ck_pedidos_status_entregue
        CHECK (status <> 'entregue' OR (data_envio IS NOT NULL AND data_entrega IS NOT NULL)),
    CONSTRAINT ck_pedidos_status_transporte
        CHECK (status <> 'em_transporte' OR (data_aprovacao IS NOT NULL AND data_envio IS NOT NULL AND data_entrega IS NULL)),
    CONSTRAINT ck_pedidos_status_aprovado
        CHECK (status <> 'aprovado' OR data_aprovacao IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    pedido_id       BIGINT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    sequencia       SMALLINT NOT NULL CHECK (sequencia > 0),
    produto_id      BIGINT NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    vendedor_id     BIGINT NOT NULL REFERENCES vendedores(id) ON DELETE RESTRICT,
    preco           NUMERIC(12, 2) NOT NULL CHECK (preco > 0),
    frete           NUMERIC(12, 2) NOT NULL CHECK (frete >= 0),
    PRIMARY KEY (pedido_id, sequencia)
);

CREATE TABLE IF NOT EXISTS pagamentos (
    pedido_id       BIGINT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    sequencia       SMALLINT NOT NULL CHECK (sequencia > 0),
    tipo            VARCHAR(30) NOT NULL CHECK (tipo IN (
        'cartao_credito', 'cartao_debito', 'pix', 'boleto'
    )),
    parcelas        SMALLINT NOT NULL CHECK (parcelas BETWEEN 1 AND 12),
    valor           NUMERIC(12, 2) NOT NULL CHECK (valor > 0),
    PRIMARY KEY (pedido_id, sequencia)
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id              BIGINT PRIMARY KEY,
    pedido_id       BIGINT NOT NULL UNIQUE REFERENCES pedidos(id) ON DELETE CASCADE,
    nota            SMALLINT NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario_curto VARCHAR(300),
    data_avaliacao  TIMESTAMP NOT NULL
);

COMMIT;
