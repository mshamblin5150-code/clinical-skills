param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [Parameter(Mandatory = $true)][string]$OutputPdf,
    [Parameter(Mandatory = $true)][string]$OwnershipFile
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
. (Join-Path $PSScriptRoot "office_process.ps1")
$powerpoint = $null
$presentation = $null
$ownedPid = $null
$ownershipEstablished = $false

try {
    $owned = New-OwnedOfficeApplication -ProcessName "POWERPNT" `
        -OwnershipFile $OwnershipFile `
        -Create { New-Object -ComObject PowerPoint.Application } `
        -FailureMessage "PowerPoint automation did not create exactly one owned process"
    $powerpoint = $owned.Application
    $ownedPid = $owned.ProcessId
    $ownershipEstablished = $true

    $presentation = $powerpoint.Presentations.Open($Pptx, $true, $true, $false)
    if ($ownershipEstablished) {
        Set-OwnedOfficeStage -OwnershipFile $OwnershipFile -ProcessId $ownedPid -Stage "opened"
    }
    $presentation.SaveAs($OutputPdf, 32)
    @{ source = "powerpoint-pdf"; path = $OutputPdf } | ConvertTo-Json -Compress
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
finally {
    if ($null -ne $presentation) {
        try { $presentation.Close() } catch {}
    }
    if ($null -ne $powerpoint -and $ownershipEstablished) {
        try { $powerpoint.Quit() } catch {}
    }
    if ($null -ne $presentation) {
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) } catch {}
    }
    if ($null -ne $powerpoint) {
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerpoint) } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
