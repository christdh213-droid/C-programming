param([Parameter(Mandatory=$true)][int]$Number)
$ErrorActionPreference='Stop'
$assignmentPath=Join-Path (Split-Path $PSScriptRoot) "Assignment$Number-CO$Number"
$docPath=Join-Path $assignmentPath "CSA02_1911260256_Assignment${Number}_Report.docx"
$renderPath=Join-Path $assignmentPath 'qa/render'
New-Item -ItemType Directory -Force -Path $renderPath | Out-Null
$word=New-Object -ComObject Word.Application
try {
    $word.Visible=$false
    $word.DisplayAlerts=0
    $doc=$word.Documents.Open($docPath,$false,$true)
    try { $doc.Repaginate();$doc.ExportAsFixedFormat((Join-Path $renderPath 'report.pdf'),17);Write-Output "Assignment ${Number}: $($doc.ComputeStatistics(2)) pages" } finally { $doc.Close(0) }
} finally { $word.Quit() }
& pdftoppm -scale-to 1500 -png (Join-Path $renderPath 'report.pdf') (Join-Path $renderPath 'page')
if($LASTEXITCODE -ne 0) { throw 'Rasterization failed' }
