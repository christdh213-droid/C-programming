$ErrorActionPreference = 'Stop'
$reportRoot = $PSScriptRoot
$reportPath = Join-Path $reportRoot 'CSA02_1911260256_Assignment2_Report.docx'
$renderDir = Join-Path $reportRoot 'qa/render'
New-Item -ItemType Directory -Force -Path $renderDir | Out-Null
$pdfPath = Join-Path $renderDir 'report.pdf'
$wordInstance = New-Object -ComObject Word.Application
try {
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    $reportDocument = $wordInstance.Documents.Open($reportPath, $false, $true)
    try {
        $reportDocument.Repaginate()
        $reportDocument.ExportAsFixedFormat($pdfPath, 17)
        Write-Output "Exported Word PDF: $pdfPath"
        Write-Output "Word pages: $($reportDocument.ComputeStatistics(2))"
    } finally { $reportDocument.Close(0) }
} finally { $wordInstance.Quit() }
& pdftoppm -scale-to 1700 -png $pdfPath (Join-Path $renderDir 'page')
if ($LASTEXITCODE -ne 0) { throw 'PDF rasterization failed' }
