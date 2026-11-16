"""Gera CSVs inteiramente sinteticos para o projeto de analise de e-commerce.

Uso:
    python -m generator.gerar_dados

Os arquivos sao gravados em DIRETORIO_DADOS (padrao: data/gerados), que nao deve
ser versionado. A mesma semente e as mesmas versoes de dependencias reproduzem
os mesmos dados.
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from faker import Faker

from generator.config import Configuracao, NOMES_CATEGORIAS

# Cidades brasileiras reais usadas apenas como localizacao geografica sintetica.
# Os pesos estaduais sao aproximacoes para produzir uma distribuicao plausivel,
# nao uma estimativa estatistica ou censo populacional.
LOCALIDADES = {
    "AC": (0.004, ["Rio Branco", "Cruzeiro do Sul", "Sena Madureira"]),
    "AL": (0.014, ["Maceio", "Arapiraca", "Palmeira dos Indios"]),
    "AP": (0.004, ["Macapa", "Santana", "Laranjal do Jari"]),
    "AM": (0.021, ["Manaus", "Parintins", "Itacoatiara"]),
    "BA": (0.073, ["Salvador", "Feira de Santana", "Vitoria da Conquista"]),
    "CE": (0.044, ["Fortaleza", "Juazeiro do Norte", "Sobral"]),
    "DF": (0.014, ["Brasilia", "Ceilandia", "Taguatinga"]),
    "ES": (0.019, ["Vitoria", "Vila Velha", "Serra"]),
    "GO": (0.034, ["Goiania", "Anapolis", "Aparecida de Goiania"]),
    "MA": (0.033, ["Sao Luis", "Imperatriz", "Caxias"]),
    "MT": (0.018, ["Cuiaba", "Varzea Grande", "Rondonopolis"]),
    "MS": (0.014, ["Campo Grande", "Dourados", "Tres Lagoas"]),
    "MG": (0.103, ["Belo Horizonte", "Uberlandia", "Juiz de Fora", "Contagem"]),
    "PA": (0.040, ["Belem", "Santarem", "Maraba"]),
    "PB": (0.020, ["Joao Pessoa", "Campina Grande", "Patos"]),
    "PR": (0.056, ["Curitiba", "Londrina", "Maringa", "Cascavel"]),
    "PE": (0.045, ["Recife", "Caruaru", "Petrolina"]),
    "PI": (0.016, ["Teresina", "Parnaiba", "Picos"]),
    "RJ": (0.078, ["Rio de Janeiro", "Niteroi", "Petropolis", "Campos dos Goytacazes"]),
    "RN": (0.016, ["Natal", "Mossoro", "Parnamirim"]),
    "RS": (0.054, ["Porto Alegre", "Caxias do Sul", "Pelotas", "Santa Maria"]),
    "RO": (0.008, ["Porto Velho", "Ji-Parana", "Ariquemes"]),
    "RR": (0.003, ["Boa Vista", "Rorainopolis", "Caracarai"]),
    "SC": (0.037, ["Florianopolis", "Joinville", "Blumenau", "Chapeco"]),
    "SP": (0.219, ["Sao Paulo", "Campinas", "Santos", "Ribeirao Preto", "Sorocaba"]),
    "SE": (0.011, ["Aracaju", "Itabaiana", "Lagarto"]),
    "TO": (0.008, ["Palmas", "Araguaina", "Gurupi"]),
}

STATUS = ["entregue", "cancelado", "em_transporte", "indisponivel", "aprovado"]
PESOS_STATUS = [0.78, 0.08, 0.05, 0.03, 0.06]
TIPOS_PAGAMENTO = ["cartao_credito", "cartao_debito", "pix", "boleto"]
PESOS_PAGAMENTO = [0.48, 0.12, 0.31, 0.09]
COMENTARIOS = [
    "Produto recebido em boas condicoes.",
    "A compra atendeu as expectativas.",
    "Entrega dentro do prazo informado.",
    "O produto corresponde a descricao.",
    "A embalagem poderia ser melhor.",
    "A entrega demorou mais que o esperado.",
    "Boa experiencia de compra.",
    "O pedido chegou com atraso.",
]


def dinheiro(valor: float | Decimal) -> str:
    """Formata valores com duas casas e arredondamento comercial."""
    decimal = valor if isinstance(valor, Decimal) else Decimal(str(valor))
    return str(decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def timestamp(valor: datetime | None) -> str:
    return valor.isoformat(sep=" ", timespec="seconds") if valor else ""


def gravar_csv(caminho: Path, cabecalho: Sequence[str], linhas: Iterable[Sequence[object]]) -> int:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    quantidade = 0
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        escritor.writerow(cabecalho)
        for linha in linhas:
            escritor.writerow(linha)
            quantidade += 1
    return quantidade


def escolher_localidade(rng: np.random.Generator) -> tuple[str, str]:
    estados = list(LOCALIDADES)
    pesos = np.array([LOCALIDADES[uf][0] for uf in estados], dtype=float)
    pesos /= pesos.sum()
    uf = str(rng.choice(estados, p=pesos))
    cidade = str(rng.choice(LOCALIDADES[uf][1]))
    return cidade, uf


def gerar_datas_base(cfg: Configuracao, rng: np.random.Generator) -> tuple[list[date], np.ndarray]:
    dias: list[date] = []
    pesos: list[float] = []
    dia_atual = cfg.data_inicio
    while dia_atual <= cfg.data_fim:
        peso_mes = 1.65 if dia_atual.month == 11 else 1.85 if dia_atual.month == 12 else 1.0
        peso_semana = 1.12 if dia_atual.weekday() < 5 else 0.78
        dias.append(dia_atual)
        pesos.append(peso_mes * peso_semana)
        dia_atual += timedelta(days=1)
    vetor = np.asarray(pesos, dtype=float)
    vetor /= vetor.sum()
    return dias, vetor


def gerar_instantes_compra(
    quantidade: int, dias: list[date], pesos_dias: np.ndarray, rng: np.random.Generator
) -> list[datetime]:
    horas = np.array(list(range(7, 24)), dtype=int)
    pesos_horas = np.array([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 9, 8, 7, 5, 3], dtype=float)
    pesos_horas /= pesos_horas.sum()
    indices_dia = rng.choice(len(dias), size=quantidade, p=pesos_dias)
    indices_hora = rng.choice(horas, size=quantidade, p=pesos_horas)
    minutos = rng.integers(0, 60, size=quantidade)
    segundos = rng.integers(0, 60, size=quantidade)
    instantes = [
        datetime.combine(dias[int(i)], time(int(h), int(m), int(s)))
        for i, h, m, s in zip(indices_dia, indices_hora, minutos, segundos)
    ]
    return sorted(instantes)


def distribuicao_pedidos_por_cliente(cfg: Configuracao, rng: np.random.Generator) -> list[int]:
    recorrentes = int(round(cfg.volume_clientes * cfg.percentual_recorrentes))
    recorrentes = min(recorrentes, cfg.volume_pedidos // 2)
    clientes_unicos = cfg.volume_clientes - recorrentes
    pedidos_base = clientes_unicos + (2 * recorrentes)
    extras = cfg.volume_pedidos - pedidos_base
    if extras < 0:
        raise ValueError("Volume de pedidos insuficiente para a quantidade de clientes recorrentes.")
    pesos = np.minimum(rng.pareto(1.8, size=recorrentes) + 1.0, 25.0)
    pesos = pesos / pesos.sum()
    adicionais = rng.multinomial(extras, pesos) if recorrentes else np.array([], dtype=int)
    contagens = [1] * clientes_unicos + [2 + int(x) for x in adicionais]
    rng.shuffle(contagens)
    if len(contagens) != cfg.volume_clientes or sum(contagens) != cfg.volume_pedidos:
        raise RuntimeError("Falha ao distribuir pedidos entre clientes.")
    return contagens


def dias_transito(uf_cliente: str, uf_vendedor: str, rng: np.random.Generator) -> int:
    regiao = {
        "AC": "N", "AP": "N", "AM": "N", "PA": "N", "RO": "N", "RR": "N", "TO": "N",
        "AL": "NE", "BA": "NE", "CE": "NE", "MA": "NE", "PB": "NE", "PE": "NE",
        "PI": "NE", "RN": "NE", "SE": "NE", "DF": "CO", "GO": "CO", "MT": "CO",
        "MS": "CO", "ES": "SE", "MG": "SE", "RJ": "SE", "SP": "SE", "PR": "S",
        "RS": "S", "SC": "S",
    }
    if uf_cliente == uf_vendedor:
        adicional = 0
    elif regiao[uf_cliente] == regiao[uf_vendedor]:
        adicional = 2
    else:
        adicional = 5
    return int(rng.integers(2, 7)) + adicional


def gerar(cfg: Configuracao) -> dict[str, int]:
    cfg.validar()
    rng = np.random.default_rng(cfg.semente)
    aleatorio = random.Random(cfg.semente)
    fake = Faker("pt_BR")
    fake.seed_instance(cfg.semente)

    saida = cfg.diretorio_saida
    saida.mkdir(parents=True, exist_ok=True)

    # 1. Clientes e vendedores: somente localizacao e data de cadastro.
    fim_datetime = datetime.combine(cfg.data_fim, time(23, 59, 59))
    inicio_datetime = datetime.combine(cfg.data_inicio, time.min)
    clientes = []
    for identificador in range(1, cfg.volume_clientes + 1):
        cidade, uf = escolher_localidade(rng)
        cadastro = inicio_datetime - timedelta(days=int(rng.integers(0, 731)))
        clientes.append((identificador, cidade, uf, cadastro))

    vendedores = []
    for identificador in range(1, cfg.volume_vendedores + 1):
        cidade, uf = escolher_localidade(rng)
        cadastro = inicio_datetime - timedelta(days=int(rng.integers(30, 1800)))
        vendedores.append((identificador, cidade, uf, cadastro))

    contagens = distribuicao_pedidos_por_cliente(cfg, rng)
    dias, pesos_dias = gerar_datas_base(cfg, rng)
    ordens_cliente_data: list[tuple[int, datetime]] = []
    for cliente_id, quantidade in enumerate(contagens, start=1):
        datas_cliente = gerar_instantes_compra(quantidade, dias, pesos_dias, rng)
        ordens_cliente_data.extend((cliente_id, instante) for instante in datas_cliente)
    aleatorio.shuffle(ordens_cliente_data)

    def linhas_categorias():
        for categoria_id, nome in enumerate(NOMES_CATEGORIAS[: cfg.volume_categorias], start=1):
            yield categoria_id, nome

    quantidade_clientes = gravar_csv(
        saida / "clientes.csv", ["id", "cidade", "estado", "data_cadastro"],
        ((i, cidade, uf, timestamp(data)) for i, cidade, uf, data in clientes),
    )
    quantidade_vendedores = gravar_csv(
        saida / "vendedores.csv", ["id", "cidade", "estado", "data_cadastro"],
        ((i, cidade, uf, timestamp(data)) for i, cidade, uf, data in vendedores),
    )
    quantidade_categorias = gravar_csv(
        saida / "categorias.csv", ["id", "nome"], linhas_categorias()
    )
    # O catalogo e montado uma unica vez e reutilizado pelos itens dos pedidos.
    produtos_cache = []
    linhas_produto = []
    for produto_id in range(1, cfg.volume_produtos + 1):
        categoria_id = int(rng.integers(1, cfg.volume_categorias + 1))
        categoria = NOMES_CATEGORIAS[categoria_id - 1]
        preco = float(np.clip(rng.lognormal(mean=4.0, sigma=0.75), 8.0, 3500.0))
        peso = int(rng.integers(30, 18001))
        produtos_cache.append((produto_id, categoria_id, preco, peso))
        linhas_produto.append((produto_id, categoria_id, f"Produto sintetico {produto_id:04d} - {categoria}", dinheiro(preco), peso))
    quantidade_produtos = gravar_csv(
        saida / "produtos.csv", ["id", "categoria_id", "nome", "preco_base", "peso_g"], linhas_produto
    )

    estados_vendedores = {linha[0]: linha[2] for linha in vendedores}
    linhas_pedidos = []
    linhas_itens = []
    linhas_pagamentos = []
    linhas_avaliacoes = []
    quantidade_reviews = 0
    entregas_sem_aprovacao = 0
    pedidos_atrasados = 0

    for pedido_id, (cliente_id, compra) in enumerate(ordens_cliente_data, start=1):
        status = str(rng.choice(STATUS, p=PESOS_STATUS))
        cliente_uf = clientes[cliente_id - 1][2]
        previsao_dias = int(rng.integers(5, 12))
        aprovacao: datetime | None = None
        envio: datetime | None = None
        entrega: datetime | None = None
        vendedor_principal = int(rng.integers(1, cfg.volume_vendedores + 1))
        vendedor_uf = estados_vendedores[vendedor_principal]
        transito = dias_transito(cliente_uf, vendedor_uf, rng)
        estimada = compra + timedelta(days=previsao_dias + max(0, transito - 4))
        atraso_dias = 0

        if status == "entregue":
            # Uma pequena parcela representa a inconsistência intencional documentada.
            sem_aprovacao = bool(rng.random() < 0.005)
            aprovacao = None if sem_aprovacao else compra + timedelta(hours=int(rng.integers(1, 49)))
            if sem_aprovacao:
                entregas_sem_aprovacao += 1
            envio_base = aprovacao or compra
            envio = envio_base + timedelta(hours=int(rng.integers(3, 49)))
            entrega = envio + timedelta(days=transito + int(rng.integers(0, 5)))
            atraso_dias = max(0, (entrega.date() - estimada.date()).days)
            if atraso_dias > 0:
                pedidos_atrasados += 1
        elif status == "em_transporte":
            aprovacao = compra + timedelta(hours=int(rng.integers(1, 49)))
            envio = aprovacao + timedelta(hours=int(rng.integers(3, 49)))
        elif status == "aprovado":
            aprovacao = compra + timedelta(hours=int(rng.integers(1, 49)))
        elif status == "cancelado" and rng.random() < 0.80:
            aprovacao = compra + timedelta(hours=int(rng.integers(1, 49)))

        linhas_pedidos.append((
            pedido_id, cliente_id, status, timestamp(compra), timestamp(aprovacao),
            timestamp(envio), timestamp(entrega), timestamp(estimada),
        ))

        quantidade_itens = int(rng.choice([1, 2, 3, 4, 5], p=[0.34, 0.32, 0.20, 0.10, 0.04]))
        total_pedido = Decimal("0.00")
        for sequencia in range(1, quantidade_itens + 1):
            produto_id, categoria_id, preco_base, peso_g = produtos_cache[int(rng.integers(0, len(produtos_cache)))]
            vendedor_id = int(rng.integers(1, cfg.volume_vendedores + 1))
            desconto = float(rng.uniform(0.78, 1.18))
            preco = Decimal(dinheiro(preco_base * desconto))
            frete_unitario = Decimal(dinheiro(max(4.0, (peso_g / 1000) * rng.uniform(1.1, 3.2) + transito * 0.75)))
            linhas_itens.append((pedido_id, sequencia, produto_id, vendedor_id, str(preco), str(frete_unitario)))
            total_pedido += preco + frete_unitario

        tipo_pagamento = str(rng.choice(TIPOS_PAGAMENTO, p=PESOS_PAGAMENTO))
        parcelas = int(rng.integers(1, 13)) if tipo_pagamento == "cartao_credito" else 1
        linhas_pagamentos.append((pedido_id, 1, tipo_pagamento, parcelas, dinheiro(total_pedido)))

        if status == "entregue" and rng.random() < 0.58:
            ruido = float(rng.normal(0, 0.75))
            nota = int(np.clip(round(4.75 - (atraso_dias * 0.22) + ruido), 1, 5))
            comentario = COMENTARIOS[int(rng.integers(0, len(COMENTARIOS)))]
            # Usa o gerador Faker pt_BR para selecionar comentarios em portugues,
            # sem introduzir nomes ou identificadores pessoais no conjunto.
            if rng.random() < 0.25:
                comentario = str(fake.random_element(elements=COMENTARIOS))
            data_avaliacao = (entrega or compra) + timedelta(days=int(rng.integers(1, 15)))
            quantidade_reviews += 1
            linhas_avaliacoes.append((
                quantidade_reviews, pedido_id, nota, comentario[:300], timestamp(data_avaliacao)
            ))

    # Exportacao em CSV com delimitador explicito para uso posterior de COPY no PostgreSQL.
    quantidade_pedidos = gravar_csv(
        saida / "pedidos.csv",
        ["id", "cliente_id", "status", "data_compra", "data_aprovacao", "data_envio", "data_entrega", "data_estimada_entrega"],
        linhas_pedidos,
    )
    quantidade_itens = gravar_csv(
        saida / "itens_pedido.csv",
        ["pedido_id", "sequencia", "produto_id", "vendedor_id", "preco", "frete"],
        linhas_itens,
    )
    quantidade_pagamentos = gravar_csv(
        saida / "pagamentos.csv", ["pedido_id", "sequencia", "tipo", "parcelas", "valor"],
        linhas_pagamentos,
    )
    quantidade_avaliacoes = gravar_csv(
        saida / "avaliacoes.csv", ["id", "pedido_id", "nota", "comentario_curto", "data_avaliacao"],
        linhas_avaliacoes,
    )

    manifesto = {
        "aviso": "Todos os registros deste projeto sao sinteticos; nao representam clientes, vendedores ou transacoes reais.",
        "semente": cfg.semente,
        "periodo_compras": {"inicio": cfg.data_inicio.isoformat(), "fim": cfg.data_fim.isoformat()},
        "configuracao": {
            "clientes": cfg.volume_clientes,
            "vendedores": cfg.volume_vendedores,
            "categorias": cfg.volume_categorias,
            "produtos": cfg.volume_produtos,
            "pedidos": cfg.volume_pedidos,
            "percentual_clientes_recorrentes_configurado": cfg.percentual_recorrentes,
        },
        "linhas_geradas": {
            "clientes": quantidade_clientes,
            "vendedores": quantidade_vendedores,
            "categorias": quantidade_categorias,
            "produtos": quantidade_produtos,
            "pedidos": quantidade_pedidos,
            "itens_pedido": quantidade_itens,
            "pagamentos": quantidade_pagamentos,
            "avaliacoes": quantidade_avaliacoes,
        },
        "ocorrencias_intencionais": {
            "entregas_sem_aprovacao": entregas_sem_aprovacao,
            "pedidos_entregues_com_atraso": pedidos_atrasados,
            "pedidos_sem_avaliacao": quantidade_pedidos - quantidade_reviews,
        },
        "observacao": "Os totais refletem esta execucao do gerador e nao sao conclusoes sobre um negocio real.",
    }
    (saida / "manifesto.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifesto["linhas_geradas"]


def main() -> None:
    configuracao = Configuracao()
    contagens = gerar(configuracao)
    print("Arquivos sinteticos gerados em:", configuracao.diretorio_saida.resolve())
    for tabela, quantidade in contagens.items():
        print(f"- {tabela}: {quantidade:,} registros".replace(",", "."))


if __name__ == "__main__":
    main()
