# Back up or restore the AURA PostgreSQL database (custom-format pg_dump).
# Backup:  powershell -ExecutionPolicy Bypass -File scripts\backup-db.ps1 backup  [-Db aura]
# Restore: powershell -ExecutionPolicy Bypass -File scripts\backup-db.ps1 restore -File <dump> -Db <target_db>
# Production: run against the hosted DATABASE_URL instead, and store dumps encrypted, off-site.
param(
    [ValidateSet('backup', 'restore')][string]$Action = 'backup',
    [string]$Db = 'aura',
    [string]$File = '',
    [string]$PgHost = '127.0.0.1',
    [int]$Port = 5433,
    [string]$User = 'aura'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$bin = Join-Path $root '.local\pgsql\bin'
$dir = Join-Path (Split-Path -Parent $root) 'AURA_BACKUPS\db'   # outside the Git repository
New-Item -ItemType Directory -Force $dir | Out-Null

if ($Action -eq 'backup') {
    $out = Join-Path $dir ("{0}-{1}.dump" -f $Db, (Get-Date -Format 'yyyyMMdd-HHmmss'))
    & "$bin\pg_dump.exe" -h $PgHost -p $Port -U $User -d $Db -Fc -f $out
    if ($LASTEXITCODE -ne 0) { throw "pg_dump failed" }
    Write-Output $out
} else {
    if (-not (Test-Path $File)) { throw "Backup file not found: $File" }
    if ($Db -eq 'aura') { throw "Refusing to restore over the live 'aura' database. Restore into a new database, check it, then switch." }
    & "$bin\psql.exe" -h $PgHost -p $Port -U postgres -qc "DROP DATABASE IF EXISTS $Db" | Out-Null
    & "$bin\psql.exe" -h $PgHost -p $Port -U postgres -qc "CREATE DATABASE $Db OWNER $User" | Out-Null
    & "$bin\pg_restore.exe" -h $PgHost -p $Port -U $User -d $Db --no-owner $File
    if ($LASTEXITCODE -ne 0) { throw "pg_restore failed" }
    Write-Output "Restored $File into $Db"
}
