import json
from generate_readme import run_security_scan

def test_security():
    bandit_result = run_security_scan()

    with open("security_report.json", "w", encoding="utf-8") as file:
        json.dump(bandit_result, file, indent=2)

    issues = bandit_result.get("results", [])

    high_severity_issues = [
        issue for issue in issues if issue.get("issue_severity") == "HIGH"
    ]
    medium_severity_issues = [
        issue for issue in issues if issue.get("issue_severity") == "MEDIUM"
    ]

    assert len(high_severity_issues) == 0, f"Foram encontrados {len(high_severity_issues)} problemas de segurança de severidade ALTA"
    assert len(medium_severity_issues) == 0, f"Foram encontrados {len(medium_severity_issues)} problemas de segurança de severidade MÉDIA"
