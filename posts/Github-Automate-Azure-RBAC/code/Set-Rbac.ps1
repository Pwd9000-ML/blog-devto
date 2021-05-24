# 'scrips/set_rbac.ps1'
#Parameters from github actions
Param (
 [Parameter(Mandatory)]
 [array]$RoleDefinitions
)

#Directory in use.
Write-host "Current Scripting directory: [$PSScriptRoot]"

#checked out build sources path
$BuildSourcesDirectory = "$(Resolve-Path -Path $PSScriptRoot\..)"
Write-host "Current checked out build sources directory: [$BuildSourcesDirectory]"

Foreach ($file in $RoleDefinitions) {
    $Obj = Get-Content -Path $file| ConvertFrom-Json
    $scope = $Obj.AssignableScopes[0]

    If ($scope -like "*managementGroups*") {
        $managementGroupSubs = ((Get-AzManagementGroup -GroupId ($scope | Split-Path -leaf) -Expand -Recurse).Children)
        If ($managementGroupSubs.Type -like "*managementGroups") {
            Set-AzContext -SubscriptionId $managementGroupSubs.children[0].Name
        }
        If ($managementGroupSubs.Type -like "*subscriptions") {
            Set-AzContext -SubscriptionId $managementGroupSubs.Name[0]
        }

        #Test if roledef exists
        $roleDef = Get-AzRoleDefinition $Obj.Name
        If ($roleDef) {
            Write-Output "Role Definition [$($Obj.name)] already exists:"
            Write-Output "----------------------------------------------"
            $roleDef
            Write-Output "----------------------------------------------"
            Write-Output "Updating Azure Role definition"

            $Obj.Id = $roleDef.Id
            Set-AzRoleDefinition -Role $Obj
        }
        Else {
            Write-Output "Role Definition does not exist:"
            Write-Output "Creating new Azure Role definition"

            New-AzRoleDefinition -InputFile $file
        }
    }

    If ($scope -like "*subscriptions*") {
        Set-AzContext -SubscriptionId ($scope | Split-Path -leaf)

        #Test if roledef exists
        $roleDef = Get-AzRoleDefinition $Obj.Name
        If ($roleDef) {
            Write-Output "Role Definition [$($Obj.name)] already exists:"
            Write-Output "----------------------------------------------"
            $roleDef
            Write-Output "----------------------------------------------"
            Write-Output "Updating Azure Role definition"
            
            $Obj.Id = $roleDef.Id
            Set-AzRoleDefinition -Role $Obj
        }
        Else {
            Write-Output "Role Definition does not exist:"
            Write-Output "Creating new Azure Role definition"

            New-AzRoleDefinition -InputFile $file
        }
    }
}