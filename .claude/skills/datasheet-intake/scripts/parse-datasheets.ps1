# Converts datasheet PDFs to markdown with Docling, in parallel.
# Default: every PDF in datasheets/new/  ->  info/raw/<same name>.md
#
# Speed-ups (all on by default):
#   1. No OCR on the first pass (datasheets are digital PDFs). Any PDF whose output is
#      suspiciously short (likely a scan) is automatically re-parsed WITH OCR.
#   2. Parallel workers (-Workers, default 2 x 4 threads = 8 CPU threads).
#   3. One Docling call per worker for its whole share of PDFs (models load once per worker).
#
# Usage (from the vault root):
#   powershell -ExecutionPolicy Bypass -File .claude\skills\datasheet-intake\scripts\parse-datasheets.ps1
#   ... -InputDir "notes\hardware\materials\datasheets\AI"   parse another folder
#   ... -Workers 3 -Threads 2     tune parallelism (Workers x Threads ~= CPU threads)
#   ... -Force                    re-parse even if the markdown already exists
#   ... -Ocr                      force OCR on every PDF (slow; for scanned batches)

param(
    [string]$InputDir  = 'notes\hardware\materials\datasheets\new',
    [string]$OutputDir = 'notes\hardware\materials\info\raw',
    [int]$Workers = 2,
    [int]$Threads = 4,
    [int]$MinChars = 400,        # output shorter than this (non-whitespace) => retry with OCR
    [switch]$Force,
    [switch]$Ocr
)

$ErrorActionPreference = 'Stop'
$vault = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')
if (-not [IO.Path]::IsPathRooted($InputDir))  { $InputDir  = Join-Path $vault $InputDir }
if (-not [IO.Path]::IsPathRooted($OutputDir)) { $OutputDir = Join-Path $vault $OutputDir }

$docling = (Get-Command docling -ErrorAction SilentlyContinue).Source
if (-not $docling) { $docling = Join-Path $env:USERPROFILE '.local\bin\docling.exe' }
if (-not (Test-Path $docling)) { throw "Docling not found. Install it with: uv tool install docling --python 3.12" }
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'

New-Item -ItemType Directory -Force $OutputDir | Out-Null
$logDir = Join-Path $env:TEMP 'datasheet-intake-logs'
New-Item -ItemType Directory -Force $logDir | Out-Null

$all  = Get-ChildItem $InputDir -File | Where-Object { $_.Extension -ieq '.pdf' }
$todo = $all | Where-Object { $Force -or -not (Test-Path (Join-Path $OutputDir ($_.BaseName + '.md'))) }
$skipped = @($all | Where-Object { $todo -notcontains $_ } | ForEach-Object Name)
if (-not $todo) { Write-Output "Nothing to parse ($($skipped.Count) already parsed)."; exit 0 }

function Quote([string]$s) { '"' + $s + '"' }

# Runs Docling on groups of PDFs in parallel; waits for all workers.
function Invoke-Parallel($files, [bool]$useOcr, [string]$tag) {
    $n = [Math]::Max(1, [Math]::Min($Workers, @($files).Count))
    $groups = @{}; $i = 0
    foreach ($f in $files) { $k = $i % $n; if (-not $groups[$k]) { $groups[$k] = @() }; $groups[$k] += $f; $i++ }
    $procs = foreach ($k in $groups.Keys) {
        $argList = @($groups[$k] | ForEach-Object { Quote $_.FullName }) +
                   @('--to', 'md', '--output', (Quote $OutputDir), '--image-export-mode', 'placeholder',
                     '--num-threads', $Threads)
        $argList += $(if ($useOcr) { '--ocr' } else { '--no-ocr' })
        Start-Process -FilePath $docling -ArgumentList ($argList -join ' ') -NoNewWindow -PassThru `
            -RedirectStandardError (Join-Path $logDir "$tag-$k.err") -RedirectStandardOutput (Join-Path $logDir "$tag-$k.out")
    }
    $procs | ForEach-Object { $_.WaitForExit() }
}

function Get-Short($files) {
    @($files | Where-Object {
        $md = Join-Path $OutputDir ($_.BaseName + '.md')
        -not (Test-Path $md) -or (((Get-Content $md -Raw) -replace '\s|<!-- image -->', '').Length -lt $MinChars)
    })
}

$sw = [Diagnostics.Stopwatch]::StartNew()
Write-Output "Parsing $(@($todo).Count) PDF(s) with $Workers worker(s) x $Threads thread(s), OCR: $(if ($Ocr) {'on'} else {'off, auto-retry on short output'}) ..."
Invoke-Parallel $todo ([bool]$Ocr) 'pass1'

$retried = @()
if (-not $Ocr) {
    $short = Get-Short $todo
    if ($short) {
        $retried = @($short | ForEach-Object Name)
        Write-Output "Re-parsing with OCR (short/empty output, likely scanned): $($retried -join ', ')"
        Invoke-Parallel $short $true 'pass2'
    }
}

$failed = @(Get-Short $todo | ForEach-Object Name)
$done   = @($todo | Where-Object { $failed -notcontains $_.Name } | ForEach-Object Name)
Write-Output ""
Write-Output ("Time:    {0:N0} s" -f $sw.Elapsed.TotalSeconds)
Write-Output "Parsed:  $($done.Count)   $($done -join ', ')"
Write-Output "OCR retry: $($retried.Count)   $($retried -join ', ')"
Write-Output "Skipped: $($skipped.Count) (already parsed)"
Write-Output "Failed or still near-empty: $($failed.Count)   $($failed -join ', ')   (logs: $logDir)"
if ($failed) { exit 1 }
