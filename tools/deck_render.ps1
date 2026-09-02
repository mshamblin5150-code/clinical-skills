param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [Parameter(Mandatory = $true)][string]$OutputPdf,
    [Parameter(Mandatory = $true)][string]$OwnershipFile
)

$ErrorActionPreference = "Stop"
$powerpoint = $null
$presentation = $null
$ownedPid = $null
$ownershipEstablished = $false
$before = @(Get-Process -Name POWERPNT -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })

try {
    $powerpoint = New-Object -ComObject PowerPoint.Application
    $after = @(Get-Process -Name POWERPNT -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $created = @($after | Where-Object { $before -notcontains $_ })
    if ($created.Count -ne 1) {
        throw "PowerPoint automation did not create exactly one owned process"
    }
    $ownedPid = $created[0]
    Set-Content -LiteralPath $OwnershipFile -Value "$ownedPid|created" -Encoding Ascii -NoNewline
    $ownershipEstablished = $true

    $presentation = $powerpoint.Presentations.Open($Pptx, $true, $true, $false)
    if ($ownershipEstablished) {
        Set-Content -LiteralPath $OwnershipFile -Value "$ownedPid|opened" -Encoding Ascii -NoNewline
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
