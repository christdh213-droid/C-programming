$ErrorActionPreference = 'Stop'
$reportRoot = $PSScriptRoot
$wordInstance = New-Object -ComObject Word.Application
try {
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    foreach ($assignmentNumber in @(2,3)) {
        $coNumber = if ($assignmentNumber -eq 2) { 2 } else { 3 }
        $assignmentDir = Join-Path $reportRoot "Assignment$assignmentNumber-CO$coNumber"
        $reportPath = Join-Path $assignmentDir "CSA02_1911260256_Assignment${assignmentNumber}_Report.docx"
        $renderDir = Join-Path $assignmentDir 'qa/render'
        New-Item -ItemType Directory -Force -Path $renderDir | Out-Null
        $pdfPath = Join-Path $renderDir 'report.pdf'
        $reportDocument = $wordInstance.Documents.Open($reportPath, $false, $true)
        try {
            $reportDocument.Repaginate()
            $reportDocument.ExportAsFixedFormat($pdfPath,17)
            Write-Output "Assignment ${assignmentNumber}: $($reportDocument.ComputeStatistics(2)) pages exported"
        } finally { $reportDocument.Close(0) }
        & pdftoppm -scale-to 1600 -png $pdfPath (Join-Path $renderDir 'page')
        if ($LASTEXITCODE -ne 0) { throw 'PDF rasterization failed' }
    }
} finally { $wordInstance.Quit() }
