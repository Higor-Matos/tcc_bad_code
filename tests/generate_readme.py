import os
import json
from datetime import datetime
import subprocess

def get_exclude_dirs():
    print("Obtendo diretórios a serem excluídos...")
    exclude_dirs = [
        "../tests",
        "../venv",
        "../venv/*",
        "../venv/lib",
        "../venv/lib/python3.12",
        "../venv/lib/python3.12/site-packages",
        "../lib",
        "../lib/*",
    ]
    print(f"Excluindo diretórios: {exclude_dirs}")
    return ",".join(exclude_dirs)

def run_pytest():
    print("Executando testes de desempenho com pytest e benchmark...")
    try:
        result = subprocess.run(
            [
                "pytest",
                "-m", "performance",  # Executar apenas os testes marcados como "performance"
                "--disable-warnings",
                "--tb=short",
                "--benchmark-json=benchmark_report.json"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        print("Testes de desempenho executados com sucesso.")
        lines = result.stdout.decode("utf-8").splitlines()
        summary_line = None
        for line in lines:
            if " passed" in line and "failed" not in line and "warnings" not in line:
                summary_line = line
        return summary_line if summary_line else "Resumo dos testes não encontrado."
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar pytest: {e}")
        print(f"Saída de erro: {e.stderr.decode('utf-8')}")
        return "Erro ao executar pytest."

def extract_complexity():
    print("Calculando complexidade do código com Radon...")
    exclude_dirs_str = get_exclude_dirs()
    try:
        result = subprocess.run(
            ["radon", "cc", "../", "-a", "-s", "--exclude", exclude_dirs_str],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        output = result.stdout.decode("utf-8")
        print(f"Saída do Radon: {output}")

        with open("complexity_report.txt", "w", encoding="utf-8") as file:
            file.write(output)

        lines = output.split("\n")
        for line in lines:
            if "Average complexity" in line:
                average_complexity = line.split()[-1].strip("()")
                print(f"Complexidade média: {average_complexity}")
                return average_complexity
        return None
    except subprocess.CalledProcessError as e:
        print(f"Erro ao calcular complexidade: {e}")
        return "Erro ao calcular complexidade."

def run_security_scan():
    print("Executando análise de segurança com Bandit...")
    exclude_dirs_str = get_exclude_dirs()
    try:
        result = subprocess.run(
            [
                "bandit",
                "-r",
                "../",
                "--exclude",
                exclude_dirs_str,
                "-f",
                "json",
                "-o",
                "security_report.json",
                "--exit-zero"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print(f"Saída do Bandit: {result.stdout.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar Bandit: {e}")
        print(f"Saída de erro: {e.stderr.decode('utf-8')}")

    with open("security_report.json", "r", encoding="utf-8") as file:
        bandit_result = json.load(file)
    return bandit_result

def format_security_results(bandit_result):
    print("Formatando resultados da análise de segurança...")
    issues = bandit_result.get("results", [])
    if not issues:
        print("Nenhum problema de segurança encontrado.")
        return "Nenhum problema de segurança encontrado.\n\n"
    else:
        formatted_results = "Os seguintes problemas de segurança foram encontrados:\n\n"
        for issue in issues:
            formatted_results += (
                f"### [{issue['issue_severity']}] {issue['issue_text']}\n"
                f"- **Arquivo**: {issue['filename']}\n"
                f"- **Linha**: {issue['line_number']}\n"
                f"- **Detalhes**: [{issue['test_id']}]({issue['more_info']})\n\n"
            )
        return formatted_results

def format_benchmark_results(benchmark_report):
    """Formata os resultados do benchmark e calcula tempo por nota e por email."""
    benchmark_results = json.loads(benchmark_report)
    num_notas = 1000
    formatted_results = []

    for bench in benchmark_results["benchmarks"]:
        name = bench["name"]
        mean_time = bench["stats"]["mean"]
        total_time = mean_time * num_notas
        rounds = bench["stats"]["rounds"]

        formatted_results.append(
            f"### {name}\n"
            f"- **Tempo Médio por Nota**: {mean_time:.6f} segundos\n"
            f"- **Tempo Total para {num_notas} Notas**: {total_time:.6f} segundos\n"
            f"- **Rodadas**: {rounds}\n"
        )

    return "\n".join(formatted_results)

def create_readme(test_output, complexity, security_results, performance_report="benchmark_report.json"):
    print("Gerando o arquivo README.md...")
    with open("README.md", "w", encoding="utf-8") as readme:
        readme.write("# Relatório de Qualidade do Código\n\n")
        readme.write(f"Relatório gerado em: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}\n\n")

        # Resultados dos testes
        readme.write("## Resultados dos Testes Automatizados\n")
        readme.write(f"**Status dos Testes**: {test_output}\n\n")

        # Complexidade de código
        readme.write("## Complexidade Média do Código\n")
        readme.write(f"A complexidade média do código é: **{complexity}**\n\n")

        # Análise de segurança
        readme.write("## Análise de Segurança\n")
        readme.write(security_results)

        # Relatório de desempenho
        if os.path.exists(performance_report) and os.path.getsize(performance_report) > 0:
            try:
                with open(performance_report, "r", encoding="utf-8") as benchmark_file:
                    benchmark_data = benchmark_file.read()
                    if benchmark_data.strip():
                        formatted_benchmark = format_benchmark_results(benchmark_data)
                        readme.write("## Relatório de Desempenho\n")
                        readme.write(
                            "Os testes de desempenho medem a eficiência e a velocidade de execução das principais funções do sistema.\n\n"
                        )
                        readme.write(formatted_benchmark)
                    else:
                        readme.write("## Relatório de Desempenho\n")
                        readme.write("Nenhum benchmark válido encontrado.\n\n")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                readme.write("## Relatório de Desempenho\n")
                readme.write(f"Erro ao ler o relatório de desempenho: {e}\n\n")
        else:
            readme.write("## Relatório de Desempenho\n")
            readme.write("Nenhum relatório de desempenho foi gerado.\n\n")

        # Conclusão dos testes de desempenho
        readme.write("### Conclusão\n")
        readme.write("Este relatório apresenta o desempenho do sistema ao processar notas e enviar emails. "
                     "Os resultados mostram o tempo médio por nota e por email, assim como o tempo total estimado "
                     "para o processamento de 1000 notas.\n\n")

def main():
    test_output = run_pytest()
    complexity = extract_complexity()
    bandit_result = run_security_scan()
    security_results = format_security_results(bandit_result)
    create_readme(test_output, complexity, security_results)

if __name__ == "__main__":
    main()
