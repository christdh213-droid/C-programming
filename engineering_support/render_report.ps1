#requires -Version 7.0
param([Parameter(Mandatory=$true)][int]$Number)
$ErrorActionPreference='Stop'
$assignmentPath=Join-Path (Split-Path $PSScriptRoot) "Assignment$Number-CO$Number"
$docPath=Join-Path $assignmentPath "CSA02_1911260256_Assignment${Number}_Report.docx"
$renderPath=Join-Path $assignmentPath 'qa/render'
New-Item -ItemType Directory -Force -Path $renderPath | Out-Null
$stagedPath=Join-Path $renderPath 'render_source.docx'
Copy-Item -LiteralPath $docPath -Destination $stagedPath -Force
$pdfPath=Join-Path $renderPath 'rendered.pdf'
$word=New-Object -ComObject Word.Application
try {
    $word.Visible=$false
    $word.DisplayAlerts=0
    Write-Output "Opening Assignment ${Number} report"
    $doc=$word.Documents.Open($stagedPath,$false,$true)
    try { Write-Output 'Exporting PDF';$doc.ExportAsFixedFormat($pdfPath,17);Write-Output "Assignment ${Number}: $($doc.ComputeStatistics(2)) pages" } finally { $doc.Close(0) }
} finally { $word.Quit() }
Copy-Item -LiteralPath $pdfPath -Destination (Join-Path $renderPath 'report.pdf') -Force
& pdftoppm -scale-to 1500 -png (Join-Path $renderPath 'report.pdf') (Join-Path $renderPath 'page')
if($LASTEXITCODE -ne 0) { throw 'Rasterization failed' }
