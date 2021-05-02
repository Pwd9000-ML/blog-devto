Function Test-ParameterSets {
    [CmdletBinding(SupportsShouldProcess)]
    Param (
        [Parameter()]
        [Switch]$A,
        [Parameter()]
        [Switch]$B,
        [Parameter()]
        [String]$C
    )
  
    If ($A) {
        Write-output ""
    }
  }