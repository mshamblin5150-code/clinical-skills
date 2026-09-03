function New-OwnedOfficeApplication {
    param(
        [Parameter(Mandatory = $true)][string]$ProcessName,
        [Parameter(Mandatory = $true)][string]$OwnershipFile,
        [Parameter(Mandatory = $true)][scriptblock]$Create,
        [Parameter(Mandatory = $true)][string]$FailureMessage
    )

    $before = @(
        Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Id
    )
    $application = & $Create
    $after = @(
        Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Id
    )
    $created = @($after | Where-Object { $_ -notin $before })
    if ($created.Count -ne 1) {
        try { $application.Quit() } catch {}
        try {
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($application)
        }
        catch {}
        throw $FailureMessage
    }
    $ownedPid = $created[0].ToString()
    [IO.File]::WriteAllText($OwnershipFile, "$ownedPid|created")
    [pscustomobject]@{ Application = $application; ProcessId = $ownedPid }
}

function Set-OwnedOfficeStage {
    param(
        [Parameter(Mandatory = $true)][string]$OwnershipFile,
        [Parameter(Mandatory = $true)][string]$ProcessId,
        [Parameter(Mandatory = $true)][string]$Stage
    )

    [IO.File]::WriteAllText($OwnershipFile, "$ProcessId|$Stage")
}
