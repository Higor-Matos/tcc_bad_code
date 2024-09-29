# Relatório de Qualidade do Código

Relatório gerado em: 29-Sep-2024 18:32:55

## Resultados dos Testes Automatizados
**Status dos Testes**: ================= 1 passed, 2 deselected, 1 warning in 51.01s ==================

## Complexidade Média do Código
A complexidade média do código é: **2.9130434782608696**

## Análise de Segurança
Os seguintes problemas de segurança foram encontrados:

### [MEDIUM] Possible SQL injection vector through string-based query construction.
- **Arquivo**: ../painel_cliente.py
- **Linha**: 219
- **Detalhes**: [B608](https://bandit.readthedocs.io/en/1.7.10/plugins/b608_hardcoded_sql_expressions.html)

## Relatório de Desempenho
Os testes de desempenho medem a eficiência e a velocidade de execução das principais funções do sistema.

### test_process_all_users_performance
- **Tempo Médio por Nota**: 7.111923 segundos
- **Tempo Total para 1000 Notas**: 7111.922567 segundos
- **Rodadas**: 5
### Conclusão
Este relatório apresenta o desempenho do sistema ao processar notas e enviar emails. Os resultados mostram o tempo médio por nota e por email, assim como o tempo total estimado para o processamento de 1000 notas.

