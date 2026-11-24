# Run on Windows after Flutter is installed.
# Example: .\scripts\new_app.ps1 -AppName "Habit Tracker" -ProjectName habit_tracker -Org com.example
param(
  [Parameter(Mandatory = $true)][string]$AppName,
  [Parameter(Mandatory = $true)][string]$ProjectName,
  [Parameter(Mandatory = $true)][string]$Org
)
$ErrorActionPreference = "Stop"
if ($ProjectName -cnotmatch '^[a-z][a-z0-9_]*$') { throw "ProjectName must be lowercase snake_case" }
if ($Org -cnotmatch '^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)+$') { throw "Org must look like com.example" }
$root = Split-Path -Parent $PSScriptRoot
$folder = Join-Path (Split-Path -Parent $root) $ProjectName
if (Test-Path $folder) { throw "Folder already exists: $folder" }
flutter create --project-name $ProjectName --org $Org $folder
if ($LASTEXITCODE -ne 0) { throw "Flutter create failed" }
Write-Host "Created $AppName at $folder"
Write-Host "Bundle ID: $Org.$ProjectName"
Write-Host "Next: edit lib/main.dart, choose an icon, and create a new GitHub repository for this app."
