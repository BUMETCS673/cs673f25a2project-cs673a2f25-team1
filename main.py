from statement_reader.parser import Parser
from statement_reader.risk_control import RiskControl

if __name__ == "__main__":
    parsed_data = Parser().parse("sample_statement.pdf")

    rc = RiskControl(parsed_data)
    risks = rc.run_all_checks()

    if risks:
        print("发现风险：")
        for r in risks:
            print(r)
    else:
        print("未发现风险")

