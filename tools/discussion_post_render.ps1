param(
    [Parameter(Mandatory = $true)]
    [string]$Document,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [Parameter(Mandatory = $true)]
    [ValidateSet("pdf", "xps")]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$OwnershipFile
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$WdDoNotSaveChanges = 0
$WdFormatPDF = 17
$WdFormatXPS = 18
$word = $null
$opened = $null
$ownershipEstablished = $false

try {
    # New-Object creates the dedicated Word process required by ADR 0087. The
    # script never attaches to an interactive instance and never changes Visible.
    $priorWordIds = @(
        Get-Process -Name WINWORD -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Id
    )
    $word = New-Object -ComObject Word.Application
    $newWordIds = @(
        Get-Process -Name WINWORD -ErrorAction SilentlyContinue |
            Where-Object Id -NotIn $priorWordIds |
            Select-Object -ExpandProperty Id
    )
    if ($newWordIds.Count -ne 1) {
        throw "Word automation did not create exactly one owned process"
    }
    $ownedWordId = $newWordIds[0].ToString()
    [IO.File]::WriteAllText($OwnershipFile, "$ownedWordId|created")
    $ownershipEstablished = $true
    $word.DisplayAlerts = 0
    $opened = $word.Documents.Open($Document, $false, $true, $false)
    [IO.File]::WriteAllText($OwnershipFile, "$ownedWordId|opened")
    if ($Mode -eq "pdf") {
        $pdf = Join-Path $OutputDirectory "post.pdf"
        $opened.ExportAsFixedFormat2($pdf, $WdFormatPDF)
        [pscustomobject]@{ source = "word-pdf"; path = $pdf } |
            ConvertTo-Json -Compress
    }
    else {
        $xps = Join-Path $OutputDirectory "post.xps"
        $opened.SaveAs2($xps, $WdFormatXPS)
        [pscustomobject]@{ source = "word-xps"; path = $xps } |
            ConvertTo-Json -Compress
    }
}
finally {
    $cleanupFailure = $null
    if ($null -ne $opened) {
        try {
            $opened.Close($WdDoNotSaveChanges)
        }
        catch {
            $cleanupFailure = $_
        }
        finally {
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($opened)
        }
    }
    if ($null -ne $word -and $ownershipEstablished) {
        # This instance was created above; it is not a shared interactive process.
        try {
            $word.Quit()
        }
        catch {
            if ($null -eq $cleanupFailure) {
                $cleanupFailure = $_
            }
        }
        finally {
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
        }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    if ($null -ne $cleanupFailure) {
        throw $cleanupFailure
    }
}
