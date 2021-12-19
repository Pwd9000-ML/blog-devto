# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

#GET-RESOURCEGROUP4DECOM##
Function Get-ResourceGroup4Decom {
    [CmdletBinding(SupportsShouldProcess)]
    Param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$subscriptionId,

        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$ResourceGroupName,

		[Parameter(Mandatory=$false, ValueFromPipeline)]
        [ValidateSet('Decommission')]
        [String]$TagKey='Decommission',

		[Parameter()]
        [Switch]$Future
    )

    #Set context and Get date and format
    $null = Set-AzContext -Subscription $subscriptionId
    $date = get-date -format dd/MM/yyyy

    #Get Resource Object and Tags
    $objResourceGroup = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
    $objTags = $objResourceGroup.Tags

    #Get the matching key and value provided
    If(!$Future) {
        If ($objTags.Keys -contains $TagKey) {
            $tagValue = $objTags["$TagKey"]
            If (($tagValue -lt $date) -or ($tagValue -eq $date)) {
                $ResourceGroup = $objResourceGroup
            }
            return $ResourceGroup
        }
    }
    Else {
        If ($objTags.Keys -contains $TagKey) {
            $tagValue = $objTags["$TagKey"]
            If ($tagValue -gt $date) {
                $ResourceGroup = $objResourceGroup
            }
            return $ResourceGroup
        }
    }
}

#GET-RESOURCE4DECOM##
Function Get-Resource4Decom {
    [CmdletBinding(SupportsShouldProcess)]
    Param(	
        [Parameter(Mandatory, ValueFromPipeline)]
        [String]$ResourceId,

		[Parameter(Mandatory=$false, ValueFromPipeline)]
        [ValidateSet('Decommission')]
        [String]$TagKey='Decommission',

		[Parameter()]
        [Switch]$Future
    )

    #Determine resource Subscription and set context
    $subscription = $ResourceId.Split("/")[2]
    $date = get-date -format dd/MM/yyyy

    #Get Resource Object and Tags
    $objResource = Get-AzResource -ResourceId $ResourceId -ErrorAction SilentlyContinue
    $objTags = $ObjResource.Tags

    #Get the matching key and value provided
    If(!$Future) {
        If ($objTags.Keys -contains $TagKey) {
            $tagValue = $objTags["$TagKey"]
            If (($tagValue -lt $date) -or ($tagValue -eq $date)) {
                $Resource = [pscustomobject]@{Subscription = (Get-AzSubscription -SubscriptionId $subscription).Name; 
                    ResourceGroup = $ObjResource.ResourceGroupName; 
                    ResourceType = $ObjResource.ResourceType;
                    ResourceID = $ObjResource.ResourceId;
                    ResourceName = $ObjResource.Name;
                    DecommissonDate = $objTags["$TagKey"]
                    }
                return $Resource
            }
         }
    }
    Else {
        If ($objTags.Keys -contains $TagKey) {
            $tagValue = $objTags["$TagKey"]
            If ($tagValue -gt $date) {
                $Resource = [pscustomobject]@{Subscription = (Get-AzSubscription -SubscriptionId $subscription).Name; 
                    ResourceGroup = $ObjResource.ResourceGroupName; 
                    ResourceType = $ObjResource.ResourceType;
                    ResourceID = $ObjResource.ResourceId;
                    ResourceName = $ObjResource.Name;
                    DecommissionDate = $objTags["$TagKey"]
                    }
                return $Resource
            }
        }
    }
}

###Decom Section####
##Needed modules##
#Install-Module AzTable -force
Import-Module AzTable

# Set these environment variables up in Function App settings:
$scopes = $env:Function_Scopes.Split(', ') #SubscriptionIds to scan for decommissions
$resourceGroupName = $env:Function_RGName #Function RG name (for tracking)
$storageAccountName = $env:Function_SaActName #Function SA Acc Name (for tracking)
$trackingTableName = $env:Function_TableName #Table storage (Tracker)
$trackingTablePartition = $env:Function_TablePartition #Table partition (Decommissioned)

#Set Tracker context
$storageAccount = Get-AzStorageAccount -ResourceGroupName $resourceGroupName -Name $storageAccountName
$storageContext = $storageAccount.Context

#Get Resource Groups to Decom
$MatchedResourceGroups = @()
Foreach ($scope in $scopes){
    $null = Set-AzContext -Subscription $scope
    $ResourceGroupNames = (Get-AzResourceGroup).ResourceGroupName
    Foreach ($rg in $resourceGroupNames) {
        $MatchedResourceGroups += (Get-ResourceGroup4Decom -SubscriptionId $scope -ResourceGroupName $rg).ResourceId
    }
}
#Decom Resource Groups
Foreach ($rID in $MatchedResourceGroups | Where-Object {$_ -ne $null}) {
    Write-Host "Decommissioning: $rID"
    $Resource = $rID.Replace("/", ":")
    Remove-AzResource -ResourceId $rID -Force -ErrorAction Continue
    If($?){
        $cloudTable = (Get-AzStorageTable -Name $trackingTableName -Context $storageContext).CloudTable
        Add-AzTableRow -Table $cloudTable -PartitionKey $trackingTablePartition -RowKey $Resource
    } else {
        $failureMessage = $error[0].Exception.message.ToString()
        Write-Host $failureMessage
        $cloudTable = (Get-AzStorageTable -Name "Failed" -Context $storageContext).CloudTable
        Add-AzTableRow -Table $cloudTable -PartitionKey "Failed-Decommission" -RowKey $Resource
   }
}

#Get Resources to Decom
$ResourceIds = @()
Foreach ($Scope in $scopes){
    $null = Set-AzContext -Subscription $Scope
    $ResourceIds += Get-AzResource | Select-object ResourceId
}
$MatchedResources = @()
Foreach ($Id in $ResourceIds) {
    $MatchedResources += (Get-Resource4Decom -ResourceId $Id.ResourceId).ResourceID
}
#Decom Resources
Foreach ($rID in $MatchedResources | Where-Object {$_ -ne $null}) {
    Write-Host "Decommissioning: $rID"
    $Resource = $rID.Replace("/", ":")
    Remove-AzResource -ResourceId $rID -Force -ErrorAction Continue
    If($?){
        $cloudTable = (Get-AzStorageTable -Name $trackingTableName -Context $storageContext).CloudTable
        Add-AzTableRow -Table $cloudTable -PartitionKey $trackingTablePartition -RowKey $Resource
    } else {
        $failureMessage = $error[0].Exception.message.ToString()
        Write-Host $failureMessage
        $cloudTable = (Get-AzStorageTable -Name "Failed" -Context $storageContext).CloudTable
        Add-AzTableRow -Table $cloudTable -PartitionKey "Failed-Decommission" -RowKey $Resource
   }
}