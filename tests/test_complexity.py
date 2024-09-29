import subprocess

def test_code_complexity():
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
    exclude_dirs_str = ",".join(exclude_dirs)

    result = subprocess.run(
        ["radon", "cc", "../", "-a", "-s", "--exclude", exclude_dirs_str],
        stdout=subprocess.PIPE,
        check=True,
    )
    output = result.stdout.decode("utf-8")

    with open("complexity_report.txt", "w", encoding="utf-8") as file:
        file.write(output)

    lines = output.split("\n")
    for line in lines:
        if "Average complexity" in line:
            average_complexity = float(line.split()[-1].strip("()"))
            break

    assert average_complexity <= 10, f"A complexidade média do código é muito alta: {average_complexity}"
