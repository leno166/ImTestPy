# watch-log.ps1
# 实时监控并输出指定日志文件的内容（UTF-8 编码）
param(
    [Parameter(Mandatory = $false)]
    [string]$Path = "../bin/logs/system.log"
)

# 检查文件是否存在
if (-Not (Test-Path -Path $Path))
{
    Write-Error "文件不存在: $Path"
    exit 1
}

Write-Host "正在监控文件: $Path (按 Ctrl+C 停止)" -ForegroundColor Green

try
{
    Get-Content -Path $Path -Wait -Encoding UTF8
}
catch
{
    Write-Error "读取文件时出错: $_"
}