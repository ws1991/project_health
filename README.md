# 宪法AI健康数据分析系统

> **学习状态**：AIagent本地大模型架构学习已完结 ✅ | **当前目标**：切换至Kaggle实战应用

## 项目概述
这是一个用于学习和理解模块化AI系统架构的教育项目。核心目标是实现一个在“宪法”（规则集）约束下，安全分析用户健康数据的智能体系统。
最初设计架构打算使用openAI作为大模型API，但是因为deepseek不提供免费token，openAI需要外网VPN，以及本地电脑适配ollama所以优化了结构。
优化后使用ollama作为本地大模型核心的智能体，使用langchain框架组装各个组件，集成了pandas、numpy为工具箱使用。使用了matplotlib作为图形化工具。
大模型添加使用前，项目在初步的src和scripts包中的quick_analysis.py中尝试了分析本地csv文件的pandas、numpy工具和图形化工具matplotlib、seaborn的使用。其中seaborn包的初始化功能对图形文件的中文数据造成冲突问题解决花费很多时间。

## 核心架构
- **`agent/orchestrator.py`**：系统大脑，协调工具与宪法检查。调用了tools工具集合并实现判断使用其中的哪些方法工具。并且添加了默认位置/data/raw/health.csv的原生csv数据融合入用户的上下文功能。
- **`agent/constitution.txt`**：健康数据分析智能体宪法 V1.0。
- **`constitution/engine/constitution_engine.py`**：宪法警察，执行输入/输出的安全规则检查。使用parser、data、rule中的具体实现完成宪法检查。
- **`constitution/parser/constitution_parser.py`**：宪法转换，将yaml宪法格式转换为机器语言可理解的Python类。
- **`constitution/parser/schema.py`**：宪法数据格式的定义类，仅作定义数据，parser使用它将yaml宪法格式转换为机器语言可理解的Python类。
- **`constitution/rules/detection_rules.py`**：宪法检查条款的实现，逐条实现parser中宪法条款的Python类。
- **`constitution/rules/rule_evaluator.py`**：宪法的最终分发，将detection的检查条款分发给具体的用户输入的Python类。
- **`constitution/data/constitution_structured.yaml`**：宪法V2.0yaml版。
- **`agent/tools.py`**：工具集，包含数据分析、验证等功能。其最初设计理念是先调用原有的src包中的工具，如果出现调用错误再实现自己生成相关的健康数据分析工具集 - 宪法集成版。其中还包含针对特定数据格式csv的专用工具。宪法感知的工具基类。解析中文日期格式，消除警告。没有详细检查是否符合该设计理念，是否存在代码的冗余。作为下一步的优化检查步骤。
- **`interactive_agent.py`**：用户交互入口。

## 我学到的关键点
1.  **模块化设计**：理解了如何将数据管理、规则引擎、工具执行分离。
2.  **接口定义**：体验了模块间通过清晰接口（如 `EnforcementDecision` dataclass）通信的重要性。
3.  **数据流**：掌握了用户请求从输入→宪法预检→工具执行→宪法后检→输出的完整流程。
4.  **错误调试**：实践了在复杂系统中定位和修复接口兼容性问题。

## 如何运行
1.  确保安装依赖：`pip install -r requirements.txt`
2.  运行交互界面：`python interactive_agent_fixed.py`
3.  示例命令：`分析我的健康数据`

## 归档说明
- 本项目的主要学习目标（理解系统架构）已达成。
- 项目代码将作为**架构设计参考**保留，不再新增功能。
- **接下来的学习重心将转向Kaggle平台的数据科学实战**，以应用和巩固Python/Pandas/ML技能。

---

## 我的Kaggle征程
- **目标竞赛**：[Titanic: Machine Learning from Disaster](https://www.kaggle.com/c/titanic)
- **学习焦点**：Pandas数据操作、Sklearn建模流程、特征工程基础。
- **链接**：[我的Kaggle主页](https://www.kaggle.com/你的用户名)

## ⚠️ 已知问题与学习收获
- **`ConstitutionalToolSelector` 接口不匹配**：`ConstitutionEngine` 返回的 `EnforcementDecision` (dataclass) 对象与工具选择器预期的字典格式存在不一致。这暴露了**模块间接口契约设计**的重要性。
- **学习点**：通过此问题，深入实践了在复杂系统中定位集成问题、理解不同数据类型的差异。此问题本身不影响核心架构的理解，留作一个标志性的“学习里程碑”。
- **状态**：本项目的主要教学目的（理解模块化AI系统架构）已达成，因此该问题将被保留作为学习过程的见证，不再投入时间修复。
