# Project-local PostgreSQL for development and tests (no Windows service, no system install).
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\dev-db.ps1 start|stop|status
param([ValidateSet('start', 'stop', 'status')][string]$Action = 'start')

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$bin = Join-Path $root '.local\pgsql\bin'
$data = Join-Path $root '.local\pgdata'
$log = Join-Path $root '.local\postgres.log'
$port = 5433  # avoids clashing with any system PostgreSQL on 5432

if (-not (Test-Path "$bin\pg_ctl.exe")) { throw "PostgreSQL binaries not found in $bin" }

if ($Action -eq 'status') { & "$bin\pg_ctl.exe" -D $data status; exit $LASTEXITCODE }
if ($Action -eq 'stop') { & "$bin\pg_ctl.exe" -D $data stop -m fast; exit $LASTEXITCODE }

if (-not (Test-Path "$data\PG_VERSION")) {
    # Local-only cluster: trust auth bound to 127.0.0.1. Never use these settings on a server.
    & "$bin\initdb.exe" -D $data -U postgres -A trust -E UTF8 --locale=C | Out-Null
    Add-Content "$data\postgresql.conf" "`nlisten_addresses = '127.0.0.1'`nport = $port`nshared_buffers = 64MB`nmax_connections = 30`n"
}
& "$bin\pg_ctl.exe" -D $data -l $log -w start
& "$bin\psql.exe" -h 127.0.0.1 -p $port -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='aura'" | ForEach-Object { $exists = $_ }
if (-not $exists) {
    & "$bin\psql.exe" -h 127.0.0.1 -p $port -U postgres -c "CREATE ROLE aura LOGIN PASSWORD 'aura'" | Out-Null
    & "$bin\psql.exe" -h 127.0.0.1 -p $port -U postgres -c "CREATE DATABASE aura OWNER aura" | Out-Null
    & "$bin\psql.exe" -h 127.0.0.1 -p $port -U postgres -c "CREATE DATABASE aura_test OWNER aura" | Out-Null
}
Write-Output "PostgreSQL running on 127.0.0.1:$port (databases: aura, aura_test)"
