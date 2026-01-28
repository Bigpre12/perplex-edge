# Database migration helper script for Windows PowerShell

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Message
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Split-Path -Parent $ScriptDir

Push-Location $BackendDir

try {
    switch ($Command) {
        { $_ -in "up", "upgrade" } {
            Write-Host "Running migrations..." -ForegroundColor Cyan
            alembic upgrade head
            Write-Host "Migrations complete." -ForegroundColor Green
        }
        { $_ -in "down", "downgrade" } {
            Write-Host "Rolling back last migration..." -ForegroundColor Yellow
            alembic downgrade -1
            Write-Host "Rollback complete." -ForegroundColor Green
        }
        { $_ -in "new", "create" } {
            if (-not $Message) {
                Write-Host "Usage: .\migrate.ps1 new 'migration description'" -ForegroundColor Red
                exit 1
            }
            Write-Host "Creating new migration: $Message" -ForegroundColor Cyan
            alembic revision -m $Message
        }
        { $_ -in "auto", "autogenerate" } {
            if (-not $Message) {
                Write-Host "Usage: .\migrate.ps1 auto 'migration description'" -ForegroundColor Red
                exit 1
            }
            Write-Host "Auto-generating migration: $Message" -ForegroundColor Cyan
            alembic revision --autogenerate -m $Message
        }
        "history" {
            alembic history
        }
        "current" {
            alembic current
        }
        default {
            Write-Host "Database Migration Script" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Usage: .\migrate.ps1 <command> [message]"
            Write-Host ""
            Write-Host "Commands:"
            Write-Host "  up, upgrade              Run all pending migrations"
            Write-Host "  down, downgrade          Rollback last migration"
            Write-Host "  new, create 'msg'        Create a new empty migration"
            Write-Host "  auto, autogenerate 'msg' Auto-generate migration from models"
            Write-Host "  history                  Show migration history"
            Write-Host "  current                  Show current migration version"
        }
    }
} finally {
    Pop-Location
}
