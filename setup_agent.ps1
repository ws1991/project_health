# setup_agent.ps1
Write-Host "🤖 AI健康智能体启动器" -ForegroundColor Cyan
Write-Host "=" * 50

# 进入项目目录
$projectPath = "F:\python\project_health"
Write-Host "转到项目目录: $projectPath" -NoNewline

if (Test-Path $projectPath) {
    Set-Location $projectPath
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ (目录不存在)" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -NoNewline
$activatePath = "venv\Scripts\Activate.ps1"
if (Test-Path $activatePath) {
    .\venv\Scripts\Activate.ps1
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ (激活脚本不存在)" -ForegroundColor Red
    Write-Host "请检查: ls $activatePath"
    exit 1
}

# 验证激活
Write-Host "验证环境..." -NoNewline
python -c "
import sys
path = sys.executable.lower()
if 'venv' in path:
    print(' ✅ 虚拟环境激活成功')
else:
    print(' ❌ 虚拟环境未激活')
print(f'Python路径: {sys.executable}')
"

# 启动智能体系统
Write-Host "=" * 50
Write-Host "🚀 启动宪法集成智能体系统..." -ForegroundColor Green
Write-Host "可用命令:"
Write-Host "  '使用宪法约束的健康数据分析'"
Write-Host "  '生成完整的宪法约束分析报告'"
Write-Host "  'help' - 查看所有命令"
Write-Host "  'exit' - 退出系统"
Write-Host "=" * 50

python interactive_agent.py