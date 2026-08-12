[CmdletBinding()]
param(
    [switch]$Check,
    [string]$TargetDir
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

$skillFiles = @(Get-ChildItem -LiteralPath $sourceSkill -File -Recurse | Sort-Object FullName)
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
