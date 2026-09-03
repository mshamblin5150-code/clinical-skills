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
. (Join-Path $PSScriptRoot "office_process.ps1")

$WdDoNotSaveChanges = 0
$WdFormatPDF = 17
$WdFormatXPS = 18
$word = $null
$opened = $null
$ownershipEstablished = $false

try {
    # New-Object creates the dedicated Word process required by ADR 0087. The
    # script never attaches to an interactive instance and never changes Visible.
    $owned = New-OwnedOfficeApplication -ProcessName "WINWORD" `
        -OwnershipFile $OwnershipFile `
        -Create { New-Object -ComObject Word.Application } `
        -FailureMessage "Word automation did not create exactly one owned process"
    $word = $owned.Application
    $ownedWordId = $owned.ProcessId
    $ownershipEstablished = $true
    $word.DisplayAlerts = 0
    $opened = $word.Documents.Open($Document, $false, $true, $false)
    Set-OwnedOfficeStage -OwnershipFile $OwnershipFile -ProcessId $ownedWordId -Stage "opened"
    if ($Mode -eq "pdf") {
        $pdf = Join-Path $OutputDirectory "post.pdf"
        [void]$opened.GetType().InvokeMember(
            "ExportAsFixedFormat2", [Reflection.BindingFlags]::InvokeMethod,
            $null, $opened, [object[]]@([string]$pdf, [int32]$WdFormatPDF)
        )
        [pscustomobject]@{ source = "word-pdf"; path = $pdf } |
            ConvertTo-Json -Compress
    }
    else {
        $xps = Join-Path $OutputDirectory "post.xps"
        [void]$opened.GetType().InvokeMember(
            "SaveAs2", [Reflection.BindingFlags]::InvokeMethod,
            $null, $opened, [object[]]@([string]$xps, [int32]$WdFormatXPS)
        )
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
