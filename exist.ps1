# 在 F:\python\project_health 目录中运行
Write-Host "🔍 文件系统检查" -ForegroundColor Cyan
Write-Host "=" * 40

$checks = @(
    @{Name="项目目录"; Path="."; Expected=$true},
    @{Name="虚拟环境目录"; Path="venv"; Expected=$true},
    @{Name="Python解释器"; Path="venv\Scripts\python.exe"; Expected=$true},
    @{Name="激活脚本(PowerShell)"; Path="venv\Scripts\Activate.ps1"; Expected=$true},
    @{Name="激活脚本(CMD)"; Path="venv\Scripts\Activate.bat"; Expected=$true},
    @{Name="主程序"; Path="interactive_agent.py"; Expected=$true},
    @{Name="Agent工具"; Path="agent\tools.py"; Expected=$true},
    @{Name="宪法文件"; Path="agent\constitution.txt"; Expected=$true}
)

foreach ($check in $checks) {
    $exists = Test-Path $check.Path
    $status = if ($exists) { "✅" } else { "❌" }
    $color = if ($exists) { "Green" } else { "Red" }
    Write-Host "$status $($check.Name): $($check.Path)" -ForegroundColor $color
}

Write-Host "=" * 40