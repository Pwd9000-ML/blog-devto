Function Test-ParameterSets {
    [CmdletBinding(SupportsShouldProcess, DefaultParameterSetName="Default")]
    Param (
        [Parameter(Mandatory=$false)]
        [string]$DefaultParameter1,
        [Parameter(Mandatory=$false)]
        [string]$DefaultParameter2,
        [Parameter(Mandatory=$false, ParameterSetName="A")]
        [Switch]$A,
        [Parameter(Mandatory=$false, ParameterSetName="A")]
        [string]$AParameter1,
        [Parameter(Mandatory=$false, ParameterSetName="A")]
        [string]$AParameter2,
        [Parameter(Mandatory=$false, ParameterSetName="B")]
        [Switch]$B,
        [Parameter(Mandatory=$false, ParameterSetName="B")]
        [string]$BParameter1,
        [Parameter(Mandatory=$false, ParameterSetName="B")]
        [string]$BParameter2
    )
  
    If ($A) {
        Write-Output "Using Parameter Set A"
        Write-Output $DefaultParameter1
        Write-Output $DefaultParameter2
        Write-Output $AParameter1
        Write-Output $AParameter2
    }

    If ($B) {
        Write-Output "Using Parameter Set B"
        Write-Output $DefaultParameter1
        Write-Output $DefaultParameter2
        Write-Output $BParameter1
        Write-Output $BParameter2
    }
  }

# Function Tests #
Test-ParameterSets -DefaultParameter1 'defaultValue1' -DefaultParameter2 'defaultValue2' -A -AParameter1 'valueA1' -AParameter2 'valueA2'
Test-ParameterSets -DefaultParameter1 'defaultValue1' -DefaultParameter2 'defaultValue2' -B -BParameter1 'valueB1' -BParameter2 'valueB2'