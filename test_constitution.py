# test_constitution.py
from constitution.parser.constitution_parser import ConstitutionParser

# 加载宪法
parser = ConstitutionParser()
config = parser.load_from_file("constitution/data/constitution_structured.yaml")

print(f" 宪法加载成功！")
print(f"版本: {config.version}")
print(f"条款数: {len(config.clauses)}")
print(f"条款组数: {len(config.clause_groups)}")

# 显示所有条款
for clause in config.clauses:
    print(f"\n {clause.id}: {clause.name}")
    print(f"   描述: {clause.description}")
    print(f"   规则数: {len(clause.detection_rules)}")
