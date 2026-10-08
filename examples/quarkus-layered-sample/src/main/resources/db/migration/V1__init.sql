CREATE TABLE cliente (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cidade VARCHAR(120),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE venda (
    id BIGSERIAL PRIMARY KEY,
    cliente_id BIGINT NOT NULL REFERENCES cliente (id), -- sem índice (PER-IDX-001)
    data_venda DATE NOT NULL,
    total NUMERIC(14, 2) NOT NULL
);

CREATE TABLE item_venda (
    id BIGSERIAL PRIMARY KEY,
    venda_id BIGINT NOT NULL REFERENCES venda (id),
    produto VARCHAR(200) NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario NUMERIC(14, 2) NOT NULL
);
