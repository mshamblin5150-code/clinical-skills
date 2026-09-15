param(
    [string]$Destination = (Join-Path $PSScriptRoot "testdata/deck-scan-smartart-chart.pptx"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$resolvedDestination = [System.IO.Path]::GetFullPath($Destination)
if ((Test-Path -LiteralPath $resolvedDestination) -and -not $Force) {
    throw "Refusing to replace existing fixture without -Force: $resolvedDestination"
}

$parent = Split-Path -Parent $resolvedDestination
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent | Out-Null
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Write-ZipVariant {
    param(
        [string]$Source,
        [string]$Output,
        [string]$OmitEntry = "",
        [string]$ReplaceEntry = "",
        [string]$Before = "",
        [string]$After = "",
        [switch]$Overwrite
    )

    if ((Test-Path -LiteralPath $Output) -and -not $Overwrite) {
        throw "Refusing to replace existing fixture without -Force: $Output"
    }
    $mode = if ($Overwrite) {
        [System.IO.FileMode]::Create
    }
    else {
        [System.IO.FileMode]::CreateNew
    }
    $sourceArchive = [System.IO.Compression.ZipFile]::OpenRead($Source)
    $outputStream = [System.IO.File]::Open($Output, $mode)
    $outputArchive = [System.IO.Compression.ZipArchive]::new(
        $outputStream,
        [System.IO.Compression.ZipArchiveMode]::Create,
        $false
    )
    try {
        foreach ($entry in $sourceArchive.Entries) {
            if ($entry.FullName -eq $OmitEntry) {
                continue
            }
            $inputStream = $entry.Open()
            $memory = New-Object System.IO.MemoryStream
            try {
                $inputStream.CopyTo($memory)
                $payload = $memory.ToArray()
            }
            finally {
                $memory.Dispose()
                $inputStream.Dispose()
            }
            if ($entry.FullName -eq $ReplaceEntry) {
                $content = [System.Text.Encoding]::UTF8.GetString($payload)
                $index = $content.IndexOf($Before, [System.StringComparison]::Ordinal)
                if ($index -lt 0) {
                    throw "Fixture entry $ReplaceEntry does not contain the expected text"
                }
                $content = $content.Remove($index, $Before.Length).Insert($index, $After)
                $payload = [System.Text.Encoding]::UTF8.GetBytes($content)
            }
            $newEntry = $outputArchive.CreateEntry(
                $entry.FullName,
                [System.IO.Compression.CompressionLevel]::Optimal
            )
            $entryStream = $newEntry.Open()
            try {
                $entryStream.Write($payload, 0, $payload.Length)
            }
            finally {
                $entryStream.Dispose()
            }
        }
    }
    finally {
        $outputArchive.Dispose()
        $outputStream.Dispose()
        $sourceArchive.Dispose()
    }
}

$powerPoint = New-Object -ComObject PowerPoint.Application
$presentation = $null

try {
    $presentation = $powerPoint.Presentations.Add()

    $ordinarySlide = $presentation.Slides.Add(1, 12)
    $ordinary = $ordinarySlide.Shapes.AddTextbox(1, 20, 20, 650, 60)
    $ordinary.TextFrame2.TextRange.Text = "PowerPoint-authored synthetic control"
    $ordinary.TextFrame2.TextRange.Font.Size = 28

    $objectSlide = $presentation.Slides.Add(2, 12)
    $layout = @($powerPoint.SmartArtLayouts) |
        Where-Object { $_.Name -eq "Basic Block List" } |
        Select-Object -First 1
    if ($null -eq $layout) {
        throw "PowerPoint did not expose the Basic Block List SmartArt layout"
    }
    $smartArtShape = $objectSlide.Shapes.AddSmartArt($layout, 20, 40, 340, 240)
    $nodes = @($smartArtShape.SmartArt.AllNodes)
    $nodes[0].TextFrame2.TextRange.Text =
        "Build-out costs `$99,000 across nine separate synthetic budget lines here"

    $chartShape = $objectSlide.Shapes.AddChart2(-1, 51, 380, 40, 320, 240)
    $chart = $chartShape.Chart
    while ($chart.SeriesCollection().Count -gt 1) {
        $chart.SeriesCollection($chart.SeriesCollection().Count).Delete()
    }
    $chart.HasTitle = $true
    $chart.ChartTitle.Text = "Synthetic households"
    $series = $chart.SeriesCollection(1)
    $series.Name = "Program total"
    $series.XValues = @("Households", "Participation")
    $series.Values = @(325, 0.42)
    $series.ApplyDataLabels()
    $series.DataLabels(1).NumberFormat = "General"
    $series.DataLabels(2).NumberFormat = "0%"

    $presentation.SaveAs($resolvedDestination, 24)
}
finally {
    if ($null -ne $presentation) {
        $presentation.Close()
    }
    $powerPoint.Quit()
}

$missingDiagram = Join-Path $parent "deck-scan-smartart-chart-missing-diagram.pptx"
$currencyFormat = Join-Path $parent "deck-scan-smartart-chart-currency-format.pptx"
Write-ZipVariant `
    -Source $resolvedDestination `
    -Output $missingDiagram `
    -OmitEntry "ppt/diagrams/data1.xml" `
    -Overwrite:$Force
Write-ZipVariant `
    -Source $resolvedDestination `
    -Output $currencyFormat `
    -ReplaceEntry "ppt/charts/chart1.xml" `
    -Before 'formatCode="General"' `
    -After 'formatCode="$0"' `
    -Overwrite:$Force

Write-Output $resolvedDestination
