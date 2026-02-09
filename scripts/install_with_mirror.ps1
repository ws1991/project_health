# 创建新的install_dependencies.ps1
$newScript = @'
Write-Host "🚀 安装AI Agent项目依赖" -ForegroundColor Cyan
Write-Host "=" * 60

# 检查是否在虚拟环境中
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  不在虚拟环境中！" -ForegroundColor Red
    Write-Host "请先激活虚拟环境: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 虚拟环境: $env:VIRTUAL_ENV" -ForegroundColor Green

# 升级pip
Write-Host "`n⬆️  升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 使用清华镜像源
Write-Host "`n📦 使用清华镜像源安装..." -ForegroundColor Yellow

# 核心AI包
$aiPackages = @("langchain==0.1.14", "langchain-core==0.1.53", "langchain-openai==0.0.5", "openai==1.12.0")

Write-Host "安装AI核心包..." -ForegroundColor Cyan
foreach ($pkg in $aiPackages) {
    Write-Host "  $pkg" -ForegroundColor Gray -NoNewline
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple $pkg --timeout 60 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌" -ForegroundColor Red
    }
}

# 数据处理包
$dataPackages = @("pandas==2.2.1", "numpy==1.26.4", "matplotlib==3.8.3")

Write-Host "`n安装数据处理包..." -ForegroundColor Cyan
foreach ($pkg in $dataPackages) {
    Write-Host "  $pkg" -ForegroundColor Gray -NoNewline
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple $pkg --timeout 120 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌" -ForegroundColor Red
    }
}

# 其他依赖
$otherPackages = @("pyyaml==6.0.1", "python-dotenv==1.0.1", "jupyter", "ipython")

Write-Host "`n安装其他依赖..." -ForegroundColor Cyan
foreach ($pkg in $otherPackages) {
    Write-Host "  $pkg" -ForegroundColor Gray -NoNewline
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple $pkg 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌" -ForegroundColor Red
    }
}

# 验证安装
Write-Host "`n✅ 验证安装..." -ForegroundColor Yellow

$testCode = @'
import sys
print(f"Python: {sys.version.split()[0]}")
print(f"路径: {sys.executable}")

packages = [
    ("langchain", "0.1.14"),
    ("langchain-core", "0.1.53"),
    ("openai", "1.12.0"),
    ("pandas", "2.2.1")
]

print("\n包版本检查:")
for name, expected in packages:
    try:
        if name == "langchain-core":
            import langchain_core as module
        else:
            module = __import__(name.replace("-", "_") if "-" in name else name)
        version = getattr(module, "__version__", "未知")
        print(f"  {name}: {version}")
    except ImportError:
        print(f"  {name}: ❌ 未安装")
'@

$testCode | Out-File -FilePath temp_check.py -Encoding UTF8
python temp_check.py
Remove-Item temp_check.py -ErrorAction SilentlyContinue

Write-Host "`n" + "=" * 60
Write-Host "🎉 依赖安装完成！" -ForegroundColor Green
Write-Host "`n下一步：" -ForegroundColor Cyan
Write-Host "1. 配置API密钥: notepad config\secrets.yaml" -ForegroundColor Yellow
Write-Host "2. 运行测试: python scripts\test_agent_integration.py" -ForegroundColor Yellow
'@

# 保存新脚本
$newScript | Out-File -FilePath scripts\install_deps.ps1 -Encoding UTF8
Write-Host "✅ 创建新安装脚本: scripts\install_deps.ps1" -ForegroundColor Green