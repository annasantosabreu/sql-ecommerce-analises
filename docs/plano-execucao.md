# Plano de execução e validação

Este arquivo é o quadro de acompanhamento do projeto. Cada item só pode ser marcado como concluído quando houver evidência verificável.

## Papéis de revisão

- **Implementador:** desenvolve consultas, scripts, interface e documentação.
- **Validador:** revisa os arquivos de forma independente, confere consistência com o esquema, executa os testes disponíveis e registra falhas antes da aprovação.
- **Regra:** quem implementa não aprova sozinho a própria entrega. Itens sem execução real permanecem como pendentes de validação.

## Etapa 00 — Auditoria

- [x] Conferir estrutura, README, Docker, modelo, carga, qualidade, gerador e testes.
- [x] Registrar o estado inicial em `docs/auditoria-inicial.md`.
- [x] Criar branch de trabalho sem alterar `main`.
- [x] Registrar limitações da inspeção estática.

## Etapa 01 — Dashboard executivo (em andamento)

- [ ] Definir consultas SQL com métricas rastreáveis ao modelo.
- [ ] Implementar exportador PostgreSQL → JSON.
- [ ] Implementar KPIs, filtros, gráficos e tabelas.
- [ ] Adicionar validações automatizadas para consultas/exportação.
- [ ] Revisão independente: nomes, granularidade, filtros, nulos, datas e cálculos.
- [ ] Atualizar README com instruções reais de execução.
- [ ] Registrar evidências de execução real antes de publicar resultados.

## Etapa 02 — Análises aprofundadas

- [ ] Completar o conjunto de análises SQL planejadas.
- [ ] Documentar perguntas, definições, granularidade e limitações.
- [ ] Validar resultados com consultas de reconciliação.

## Etapa 03 — Qualidade e automação

- [ ] Consolidar testes automatizados.
- [ ] Configurar CI para executar testes e verificações estáticas.
- [ ] Preparar atualização agendada do JSON somente com banco acessível ao runner.
- [ ] Documentar segredos e configuração sem versionar credenciais.

## Etapa 04 — Otimização

- [ ] Selecionar consultas representativas.
- [ ] Capturar planos com `EXPLAIN (ANALYZE, BUFFERS)`.
- [ ] Comparar antes/depois com os mesmos dados e condições.
- [ ] Documentar limites e evitar alegações sem medição.

## Etapa 05 — Publicação e portfólio

- [ ] Publicar dashboard estático.
- [ ] Revisar README, imagens/evidências e instruções.
- [ ] Fazer revisão final de segurança, consistência e apresentação.
- [ ] Abrir PR para integrar a entrega validada à `main`.
