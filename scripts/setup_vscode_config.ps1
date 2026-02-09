Write-Host "⚙️  设置VS Code开发环境" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. 创建.vscode目录
Write-Host "`n📁 创建.vscode目录..." -ForegroundColor Yellow
New-Item -Path .vscode -ItemType Directory -Force

# 2. 创建settings.json
Write-Host "`n⚙️  创建settings.json..." -ForegroundColor Yellow
$settings = @'
{
    // 文件排除设置
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.git": true,
        "**/venv": true,
        "**/.env": true,
        "**/*.pyc": true
    },
    
    // Python设置
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.testing.pytestEnabled": true,
    
    // 编辑器设置
    "editor.formatOnSave": true,
    "editor.wordWrap": "on",
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.trimTrailingWhitespace": true,
    
    // YAML文件设置
    "[yaml]": {
        "editor.insertSpaces": true,
        "editor.tabSize": 2,
        "editor.autoIndent": "advanced"
    },
    
    // Git设置
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    "git.autofetch": true
}
'@

$settings | Out-File -FilePath .vscode/settings.json -Encoding UTF8
Write-Host "✅ settings.json 已创建" -ForegroundColor Green

# 3. 创建launch.json（调试配置）
Write-Host "`n🐞 创建launch.json（调试配置）..." -ForegroundColor Yellow
$launch = @'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: 当前文件",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: 测试AI Agent",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/scripts/test_agent_integration.py",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: 启动交互助手",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/scripts/start_agent.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
'@

$launch | Out-File -FilePath .vscode/launch.json -Encoding UTF8
Write-Host "✅ launch.json 已创建" -ForegroundColor Green

# 4. 创建extensions.json（扩展推荐）
Write-Host "`n🔌 创建extensions.json（推荐扩展）..." -ForegroundColor Yellow
$extensions = @'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-toolsai.jupyter",
        "redhat.vscode-yaml",
        "eamodio.gitlens",
        "usernamehw.errorlens",
        "njpwerner.autodocstring"
    ]
}
'@

$extensions | Out-File -FilePath .vscode/extensions.json -Encoding UTF8
Write-Host "✅ extensions.json 已创建" -ForegroundColor Green

# 5. 更新.gitignore
Write-Host "`n📝 更新.gitignore..." -ForegroundColor Yellow
Add-Content -Path .gitignore -Value @"

# ========== VS Code ==========
.vscode/
!.vscode/settings.json
!.vscode/launch.json
!.vscode/extensions.json
*.code-workspace
"@

Write-Host "✅ .gitignore 已更新" -ForegroundColor Green

# 6. 验证设置
Write-Host "`n🔍 验证VS Code配置..." -ForegroundColor Cyan

if (Test-Path ".vscode/settings.json") {
    Write-Host "✅ VS Code配置创建成功" -ForegroundColor Green
    Write-Host "`n📋 已创建的文件:" -ForegroundColor Yellow
    Get-ChildItem .vscode | Format-Table Name, Length
    
    Write-Host "`n🚀 下一步:" -ForegroundColor Cyan
    Write-Host "1. 重新打开VS Code: code ." -ForegroundColor Yellow
    Write-Host "2. 安装推荐扩展（右下角会有提示）" -ForegroundColor Yellow
    Write-Host "3. 选择Python解释器（右下角选择 venv）" -ForegroundColor Yellow
    Write-Host "4. 按F5测试调试功能" -ForegroundColor Yellow
} else {
    Write-Host "❌ VS Code配置创建失败" -ForegroundColor Red
}