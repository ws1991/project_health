@echo off
chcp 65001 > nul
echo.
echo ╔══════════════════════════════════════╗
echo ║    AI健康数据分析智能体系统         ║
echo ║   版本：2026.1.0                    ║
echo ╚══════════════════════════════════════╝
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在
    echo 请先运行: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/4] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo [2/4] 检查Python依赖...
python -c "
import sys
print(f'Python版本: {sys.version[:20]}')

required = ['langchain', 'langchain-community', 'pandas', 'matplotlib', 'pyyaml']
for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'✅ {pkg}')
    except:
        print(f'❌ {pkg}')
"

REM 检查Ollama
echo [3/4] 检查Ollama服务...
python -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=3)
    if response.status_code == 200:
        print('✅ Ollama服务正常')
    else:
        print('⚠️  Ollama服务异常')
except:
    print('❌ Ollama未运行，请执行: ollama serve')
"

REM 启动智能体
echo [4/4] 启动健康数据分析智能体...
python interactive_agent.py

pause