<#
	.SYNOPSIS
    Function "Get-Resource4Decom" to retrieve resources based on 'decommission' tag.

	.DESCRIPTION
    This function allows to retrieve information from Azure resources based on the presence of a 'decommission' tag and tag value in date format 'dd/MM/yyyy'.
    Results will return resources that have a date equal or earlier than the 'current date' by default. These results can then be piped into a decommission function.
    Results will return resources only with a date value greater than the 'current date' if the '-Future' parameter is used. These results can be used to see which
    resources will be decommissioned at a future date.  

	.EXAMPLE
    $resourceId = "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/RG-xxx/providers/Microsoft.Compute/disks/AZEUNPRDxxx-DISK1"
    Get-Resource4Decom -ResourceId $resourceId
    ### Retrieves the given resource ONLY if the tag key: 'Decommission' is present AND if the value is equal or earlier than the current date (dd/MM/yyyy) ###

	.EXAMPLE
    $resourceId = "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/RG-xxx/providers/Microsoft.Compute/disks/AZEUNPRDxxx-DISK1"
    Get-Resource4Decom -ResourceId $resourceId -Future
    ### Retrieves the given resource ONLY if the tag key: 'Decommission' is present AND if the value is later than the current date (dd/MM/yyyy) ###

	.EXAMPLE
    $scopes = @('00000000-1111-2222-3333-444444444444', '01010101-1234-2345-3456-555555555555')
    $ResourceIds = @()
    Foreach ($Scope in $scopes){
        Set-AzContext -Subscription $Scope
        $ResourceIds += Get-AzResource | Select-object ResourceId
    }
    $MatchedResources = @()
    Foreach ($Id in $ResourceIds) {
        $MatchedResources += Get-Resource4Decom -ResourceId $Id.ResourceId -Future
    }
    $MatchedResources | Export-Csv -Path C:\temp\Resources_to_be_decommissioned_in_future.csv -NoTypeInformation
    ### This example will look at all resources within the provided scopes/subscriptions and create a CSV file inventory of all resources tagged with 'Decommission' ###
    ### The CSV can then be inspected to see what resources are maked for decommission and the date decommission will take place ###

	.EXAMPLE
    $subscriptionId = '00000000-1111-2222-3333-444444444444'
    Set-AzContext -Subscription $subscriptionId
    $ResourceIds = Get-AzResource | Select-object ResourceId
    $MatchedResources = @()
    Foreach ($Id in $ResourceIds) {
        $MatchedResources += (Get-Resource4Decom -ResourceId $Id.ResourceId).ResourceID
    }
    $MatchedResources | foreach-object {
        Remove-AzResource -ResourceId "$_" -Force -Verbose
    }
    ### This example will look at all resources within the provided subscription and resources tagged with 'Decommission' where the date is the current date or ealier ###

	.PARAMETER ResourceId
    Mandatory Parameter.
    Specify a valid ResourceId to check tags. <String>

	.PARAMETER TagKey
    Optional Parameter.
    Specify a validated tag key to search on provided resourceId. Default and Validated value 'Decommission' <String>

	.PARAMETER Future
    Switch Parameter.
    Specify this switch to see if a resource is marked for decommission at a later date <Switch>

	.NOTES
    Author: pwd9000@hotmail.co.uk
    PSVersion: 7.2.0
    Date Created: 14/12/2021.
    Verbose output is displayed using verbose parameter. (-Verbose)
#>

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
