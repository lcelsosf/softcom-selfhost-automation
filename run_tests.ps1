[CmdletBinding()]
param(
    [ValidateSet("desktop", "web")]
    [string]$Environment,

    [string]$DeviceUrl,

    [switch]$Destructive,

    [switch]$NoDestructive
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectRoot

function Read-RequiredChoice {
    param(
        [string]$Prompt,
        [hashtable]$Choices
    )

    while ($true) {
        $answer = (Read-Host $Prompt).Trim().ToLowerInvariant()
        if ($Choices.ContainsKey($answer)) {
            return $Choices[$answer]
        }
        Write-Host "Opcao invalida. Tente novamente." -ForegroundColor Yellow
    }
}

function Read-RequiredDeviceUrl {
    while ($true) {
        $answer = (Read-Host "Informe a URL completa do dispositivo").Trim()
        $parsed = $null
        if ([Uri]::TryCreate($answer, [UriKind]::Absolute, [ref]$parsed) -and
            $parsed.Scheme -in @("http", "https") -and
            $parsed.AbsolutePath.TrimEnd("/").EndsWith("/device/add")) {
            return $answer
        }
        Write-Host "A URL deve ser HTTP(S) e apontar para /device/add." -ForegroundColor Yellow
    }
}

if ($Destructive -and $NoDestructive) {
    throw "Use apenas -Destructive ou -NoDestructive."
}

if (-not $Environment) {
    $Environment = Read-RequiredChoice `
        "Escolha o ambiente: [1] Desktop  [2] Web" `
        @{ "1" = "desktop"; "desktop" = "desktop"; "2" = "web"; "web" = "web" }
}

if (-not $DeviceUrl) {
    $DeviceUrl = Read-RequiredDeviceUrl
}

$runDestructive = $Destructive.IsPresent
if (-not $Destructive -and -not $NoDestructive) {
    $runDestructive = Read-RequiredChoice `
        "Executar testes destrutivos? [S/N]" `
        @{ "s" = $true; "sim" = $true; "n" = $false; "nao" = $false; "não" = $false }
}

if ($runDestructive) {
    Write-Host "ATENCAO: os testes destrutivos podem alterar dados do ambiente." -ForegroundColor Yellow
    $confirmed = Read-RequiredChoice `
        "Confirma a execucao destrutiva? [S/N]" `
        @{ "s" = $true; "sim" = $true; "n" = $false; "nao" = $false; "não" = $false }
    if (-not $confirmed) {
        Write-Host "Execucao cancelada."
        exit 0
    }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "O comando 'uv' nao foi encontrado no PATH."
}

$env:SELFHOST_ENVIRONMENT = $Environment
$env:SELFHOST_DEVICE_URL = $DeviceUrl
$env:SELFHOST_DESTRUCTIVE_TESTS_ENABLED = $runDestructive.ToString().ToLowerInvariant()

$allureResults = Join-Path $projectRoot "allure-results"
$allureReport = Join-Path $projectRoot "allure-report"

foreach ($directory in @($allureResults, $allureReport)) {
    if (Test-Path -LiteralPath $directory) {
        Remove-Item -LiteralPath $directory -Recurse -Force
    }
    New-Item -ItemType Directory -Path $directory | Out-Null
}

$pytestArguments = @(
    "run", "--extra", "report", "pytest",
    "--environment", $Environment,
    "--run-api-tests",
    "-v", "-ra", "--tb=short",
    "--alluredir=$allureResults"
)

if ($Environment -eq "desktop") {
    $pytestArguments += "tests/contract/test_desktop_endpoints.py"
} else {
    $pytestArguments += @("-m", "api and not desktop")
}

if ($runDestructive) {
    $pytestArguments += "--run-destructive-tests"
}

Write-Host ""
Write-Host "Executando testes no ambiente $Environment..." -ForegroundColor Cyan
& uv @pytestArguments
$testExitCode = $LASTEXITCODE

$allureCommand = $null
$allurePrefixArguments = @()
$allure = Get-Command allure -ErrorAction SilentlyContinue
if ($allure) {
    $allureCommand = $allure.Source
} else {
    $npx = Get-Command npx.cmd -ErrorAction SilentlyContinue
    if (-not $npx) {
        $npx = Get-Command npx -ErrorAction SilentlyContinue
    }
    if ($npx) {
        $allureCommand = $npx.Source
        $allurePrefixArguments = @("--yes", "allure-commandline")
        Write-Host "Allure CLI local nao encontrado; usando npx." -ForegroundColor Yellow
    } else {
        Write-Warning "Allure CLI e npx nao foram encontrados. Resultados: $allureResults"
        exit $testExitCode
    }
}

Write-Host ""
Write-Host "Gerando relatorio Allure..." -ForegroundColor Cyan
& $allureCommand @allurePrefixArguments generate $allureResults --clean -o $allureReport
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Nao foi possivel gerar o relatorio Allure."
    exit $testExitCode
}

Write-Host "Abrindo o relatorio no navegador padrao..." -ForegroundColor Cyan
& $allureCommand @allurePrefixArguments open $allureReport

exit $testExitCode
