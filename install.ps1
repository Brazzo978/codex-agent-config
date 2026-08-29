[CmdletBinding()]
param(
    [switch]$Check,
    [string]$TargetDir,
    [Alias('LlamaCodeHost')]
    [string]$OpenCodeHost,
    [Alias('LlamaCodeProfile')]
    [string]$OpenCodeModel,
    [ValidateSet('auto', 'ollama', 'llamacode')]
    [string]$OpenCodeBackend = 'auto',
    [string]$LlamaCodeUser = 'root',
    [string]$LlamaCodeSshKey,
    [Alias('LlamaCodeRemoteProject')]
    [string]$LlamaCodeRemoteWorkspace
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$payloadRoot = Join-Path $repoRoot 'payload'
$sourceAgents = Join-Path $payloadRoot 'agents'
$sourceSkill = Join-Path $payloadRoot 'skills\route-subagents'
$sourceRouting = Join-Path $payloadRoot 'AGENTS.routing.md'

$codexHomeCandidate = if (-not [string]::IsNullOrWhiteSpace($TargetDir)) {
    $TargetDir
} elseif ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex'
} else {
    $env:CODEX_HOME
}

$codexHome = [IO.Path]::GetFullPath($codexHomeCandidate)
$volumeRoot = [IO.Path]::GetPathRoot($codexHome)
if ($codexHome.TrimEnd('\') -eq $volumeRoot.TrimEnd('\')) {
    throw "Refusing to use a volume root as CODEX_HOME: $codexHome"
}

$beginMarker = '<!-- BEGIN CODEX-AGENT-CONFIG ROUTING -->'
$endMarker = '<!-- END CODEX-AGENT-CONFIG ROUTING -->'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$script:Failures = 0
$script:Changed = 0
$script:BackupRoot = $null
$timestamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')

function Normalize-Text {
    param([AllowEmptyString()][string]$Text)
    if ($null -eq $Text) { return '' }
    return (($Text -replace "`r`n", "`n") -replace "`r", "`n").TrimEnd("`n")
}

function Assert-RegularSourceFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required source file is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.PSObject.Properties.Name -contains 'LinkType') -and $item.LinkType) {
        throw "Source files must not be links: $Path"
    }
}

function Assert-SafeDestinationFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) {
        throw "Expected a file but found a directory: $Path"
    }
    if (($item.PSObject.Properties.Name -contains 'LinkType') -and $item.LinkType) {
        throw "Refusing to replace a linked destination: $Path"
    }
}

function Test-SameFile {
    param([string]$Source, [string]$Destination)
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) { return $false }
    $sourceItem = Get-Item -LiteralPath $Source
    $destinationItem = Get-Item -LiteralPath $Destination
    if ($sourceItem.Length -ne $destinationItem.Length) { return $false }
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Source).Hash -eq
        (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash
}

function Ensure-BackupRoot {
    if ($null -eq $script:BackupRoot) {
        $script:BackupRoot = Join-Path $codexHome "backups\codex-agent-config\$timestamp"
        New-Item -ItemType Directory -Force -Path $script:BackupRoot | Out-Null
    }
}

function Backup-ExistingFile {
    param([string]$Destination, [string]$RelativePath)
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) { return }
    Ensure-BackupRoot
    $backupPath = Join-Path $script:BackupRoot $RelativePath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
    Copy-Item -LiteralPath $Destination -Destination $backupPath
}

function Copy-Atomically {
    param([string]$Source, [string]$Destination)
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $staged = Join-Path $parent ('.codex-agent-config-' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        Copy-Item -LiteralPath $Source -Destination $staged
        Move-Item -LiteralPath $staged -Destination $Destination -Force
    } finally {
        if (Test-Path -LiteralPath $staged) { Remove-Item -LiteralPath $staged -Force }
    }
}

function Install-PayloadFile {
    param([string]$Source, [string]$Destination, [string]$RelativePath)
    Assert-RegularSourceFile $Source
    Assert-SafeDestinationFile $Destination

    if (Test-SameFile $Source $Destination) {
        Write-Output "CURRENT  $RelativePath"
        return
    }

    if ($Check) {
        Write-Output "DIFF     $RelativePath"
        $script:Failures++
        return
    }

    Backup-ExistingFile $Destination $RelativePath
    Copy-Atomically $Source $Destination
    if (-not (Test-SameFile $Source $Destination)) {
        throw "Post-install verification failed: $Destination"
    }
    Write-Output "INSTALLED $RelativePath"
    $script:Changed++
}

function Remove-ManagedLegacyFile {
    param([string]$Destination, [string]$RelativePath)
    if (-not (Test-Path -LiteralPath $Destination)) { return }
    Assert-SafeDestinationFile $Destination

    if ($Check) {
        Write-Output "STALE    $RelativePath"
        $script:Failures++
        return
    }

    Backup-ExistingFile $Destination $RelativePath
    Remove-Item -LiteralPath $Destination -Force
    if (Test-Path -LiteralPath $Destination) {
        throw "Could not remove obsolete managed file: $Destination"
    }
    Write-Output "REMOVED  $RelativePath"
    $script:Changed++
}

Assert-RegularSourceFile $sourceRouting
$agentFiles = @(Get-ChildItem -LiteralPath $sourceAgents -File -Filter '*.toml' | Sort-Object Name)
if ($agentFiles.Count -ne 19) {
    throw "Expected 19 custom-agent profiles, found $($agentFiles.Count)."
}

$skillFiles = @(Get-ChildItem -LiteralPath $sourceSkill -File -Recurse |
    Where-Object { $_.Extension -ne '.pyc' -and $_.FullName -notmatch '[\\/]__pycache__[\\/]' } |
    Sort-Object FullName)
if ($skillFiles.Count -lt 3) {
    throw "The route-subagents skill payload is incomplete."
}

foreach ($file in $agentFiles) {
    Install-PayloadFile $file.FullName (Join-Path $codexHome "agents\$($file.Name)") "agents\$($file.Name)"
}

$skillPrefix = $sourceSkill.TrimEnd('\') + '\'
foreach ($file in $skillFiles) {
    Assert-RegularSourceFile $file.FullName
    $relativeInsideSkill = $file.FullName.Substring($skillPrefix.Length)
    $relative = "skills\route-subagents\$relativeInsideSkill"
    Install-PayloadFile $file.FullName (Join-Path $codexHome $relative) $relative
}

if (-not [string]::IsNullOrWhiteSpace($OpenCodeHost)) {
    $workerConfigRelative = 'opencode-worker.json'
    $workerConfig = Join-Path $codexHome $workerConfigRelative
    Assert-SafeDestinationFile $workerConfig
    $workerOutputLimit = if ($OpenCodeBackend -eq 'llamacode') { 16384 } else { 32768 }
    $workerSettings = [ordered]@{
        host = $OpenCodeHost.Trim()
        backend = $OpenCodeBackend
        timeout = 0
        max_context_bytes = 49152
        effort = 'medium'
        context_limit = 110592
        output_limits = [ordered]@{
            low = $workerOutputLimit
            medium = $workerOutputLimit
            xhigh = $workerOutputLimit
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($OpenCodeModel)) {
        $workerSettings['model'] = $OpenCodeModel.Trim()
    }
    if ($OpenCodeBackend -eq 'llamacode') {
        $workerSettings['ssh_user'] = $LlamaCodeUser.Trim()
        if (-not [string]::IsNullOrWhiteSpace($LlamaCodeSshKey)) {
            $workerSettings['ssh_key'] = [IO.Path]::GetFullPath($LlamaCodeSshKey)
        }
        $workerSettings['launcher_command'] = 'llamacode'
        if (-not [string]::IsNullOrWhiteSpace($LlamaCodeRemoteWorkspace)) {
            $workerSettings['remote_workspace'] = $LlamaCodeRemoteWorkspace
        }
    }
    $desiredWorkerConfig = Normalize-Text ($workerSettings | ConvertTo-Json)
    $existingWorkerConfig = if (Test-Path -LiteralPath $workerConfig -PathType Leaf) {
        Normalize-Text ([IO.File]::ReadAllText($workerConfig))
    } else {
        ''
    }
    if ($existingWorkerConfig -eq $desiredWorkerConfig) {
        Write-Output "CURRENT  $workerConfigRelative"
    } elseif ($Check) {
        Write-Output "DIFF     $workerConfigRelative"
        $script:Failures++
    } else {
        Backup-ExistingFile $workerConfig $workerConfigRelative
        New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
        $stagedWorkerConfig = Join-Path $codexHome ('.opencode-worker-' + [guid]::NewGuid().ToString('N') + '.tmp')
        try {
            [IO.File]::WriteAllText($stagedWorkerConfig, $desiredWorkerConfig + "`n", $utf8NoBom)
            Move-Item -LiteralPath $stagedWorkerConfig -Destination $workerConfig -Force
        } finally {
            if (Test-Path -LiteralPath $stagedWorkerConfig) { Remove-Item -LiteralPath $stagedWorkerConfig -Force }
        }
        Write-Output "INSTALLED $workerConfigRelative"
        $script:Changed++
    }
}

$legacyRoutingExamplesRelative = 'skills\route-subagents\references\routing-examples.md'
$legacyRoutingExamples = Join-Path $codexHome $legacyRoutingExamplesRelative
Remove-ManagedLegacyFile $legacyRoutingExamples $legacyRoutingExamplesRelative

$routingText = Normalize-Text ([IO.File]::ReadAllText($sourceRouting))
$managedBlock = "$beginMarker`n$routingText`n$endMarker"
$globalAgents = Join-Path $codexHome 'AGENTS.md'
Assert-SafeDestinationFile $globalAgents

$existingText = if (Test-Path -LiteralPath $globalAgents -PathType Leaf) {
    Normalize-Text ([IO.File]::ReadAllText($globalAgents))
} else {
    ''
}

$pattern = '(?s)' + [regex]::Escape($beginMarker) + '.*?' + [regex]::Escape($endMarker)
$matches = [regex]::Matches($existingText, $pattern)
if ($matches.Count -gt 1) {
    throw "Multiple managed routing blocks found in $globalAgents"
}

if ($matches.Count -eq 1) {
    $match = $matches[0]
    $desiredText = $existingText.Substring(0, $match.Index) + $managedBlock +
        $existingText.Substring($match.Index + $match.Length)
} elseif ($existingText -eq $routingText -or [string]::IsNullOrWhiteSpace($existingText)) {
    $desiredText = $managedBlock
} else {
    $desiredText = $existingText.TrimEnd() + "`n`n" + $managedBlock
}

$desiredText = Normalize-Text $desiredText
if ((Normalize-Text $existingText) -eq $desiredText) {
    Write-Output 'CURRENT  AGENTS.md managed routing block'
} elseif ($Check) {
    Write-Output 'DIFF     AGENTS.md managed routing block'
    $script:Failures++
} else {
    Backup-ExistingFile $globalAgents 'AGENTS.md'
    New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
    $stagedAgents = Join-Path $codexHome ('.codex-agent-config-' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [IO.File]::WriteAllText($stagedAgents, $desiredText + "`n", $utf8NoBom)
        Move-Item -LiteralPath $stagedAgents -Destination $globalAgents -Force
    } finally {
        if (Test-Path -LiteralPath $stagedAgents) { Remove-Item -LiteralPath $stagedAgents -Force }
    }
    Write-Output 'INSTALLED AGENTS.md managed routing block'
    $script:Changed++
}

if (-not $Check) {
    foreach ($file in $agentFiles) {
        if (-not (Test-SameFile $file.FullName (Join-Path $codexHome "agents\$($file.Name)"))) {
            throw "Final verification failed for agent profile: $($file.Name)"
        }
    }
    foreach ($file in $skillFiles) {
        $relativeInsideSkill = $file.FullName.Substring($skillPrefix.Length)
        if (-not (Test-SameFile $file.FullName (Join-Path $codexHome "skills\route-subagents\$relativeInsideSkill"))) {
            throw "Final verification failed for skill file: $relativeInsideSkill"
        }
    }
    if (Test-Path -LiteralPath $legacyRoutingExamples) {
        throw "Final verification failed: obsolete routing-examples.md remains installed."
    }
    if (-not [string]::IsNullOrWhiteSpace($OpenCodeHost)) {
        $installedWorkerConfig = Normalize-Text ([IO.File]::ReadAllText((Join-Path $codexHome 'opencode-worker.json')))
        if ($installedWorkerConfig -ne $desiredWorkerConfig) {
            throw "Final verification failed for opencode-worker.json"
        }
    }
    $installedAgentsText = Normalize-Text ([IO.File]::ReadAllText($globalAgents))
    $installedMatches = [regex]::Matches($installedAgentsText, $pattern)
    if ($installedMatches.Count -ne 1 -or (Normalize-Text $installedMatches[0].Value) -ne $managedBlock) {
        throw "Final verification failed for the managed AGENTS.md block."
    }
}

if ($script:Failures -gt 0) {
    Write-Error "Check failed: $($script:Failures) managed item(s) are missing or different."
    exit 1
}

if ($Check) {
    Write-Output "CHECK PASSED: 19 agent profiles, route-subagents, and AGENTS.md match $codexHome"
} else {
    Write-Output "INSTALL PASSED: $($script:Changed) managed item(s) updated in $codexHome"
    if ($null -ne $script:BackupRoot) { Write-Output "BACKUP: $script:BackupRoot" }
    Write-Output 'Restart Codex and start a new task to load the custom-agent types.'
}

if (-not [string]::IsNullOrWhiteSpace($OpenCodeHost)) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        throw 'Python is required for the OpenCode worker but was not found in PATH.'
    }
    & $python.Source (Join-Path $codexHome 'skills\route-subagents\scripts\opencode_worker.py') --config (Join-Path $codexHome 'opencode-worker.json') --healthcheck
    if ($LASTEXITCODE -ne 0) {
        throw 'OpenCode worker health check failed.'
    }

    if (-not $Check) {
        $codex = Get-Command codex -ErrorAction SilentlyContinue
        if ($null -eq $codex) {
            throw 'Codex CLI is required to register the local OpenCode MCP server.'
        }
        $configToml = Join-Path $codexHome 'config.toml'
        Backup-ExistingFile $configToml 'config.toml'
        $previousCodexHome = $env:CODEX_HOME
        try {
            $env:CODEX_HOME = $codexHome
            & $codex.Source mcp remove local_opencode_worker 2>$null
            & $codex.Source mcp add local_opencode_worker -- $python.Source (Join-Path $codexHome 'skills\route-subagents\scripts\opencode_mcp.py')
            if ($LASTEXITCODE -ne 0) { throw 'Could not register the local OpenCode MCP server.' }
            & $codex.Source mcp get local_opencode_worker --json | Out-Null
            if ($LASTEXITCODE -ne 0) { throw 'OpenCode MCP registration verification failed.' }
            Write-Output 'REGISTERED local_opencode_worker MCP server'
            if ($null -ne $script:BackupRoot) { Write-Output "BACKUP: $script:BackupRoot" }
        } finally {
            $env:CODEX_HOME = $previousCodexHome
        }
    }
}
