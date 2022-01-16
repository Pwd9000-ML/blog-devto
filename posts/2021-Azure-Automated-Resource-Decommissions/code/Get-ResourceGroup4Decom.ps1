<#
	.SYNOPSIS
    Function "Get-ResourceGroup4Decom" to retrieve resource Groups based on 'decommission' tag.

	.DESCRIPTION
    This function allows to retrieve information from Azure resource groups based on the presence of a 'decommission' tag and tag value in date format 'dd/MM/yyyy'.
    Results will return resource groups that have a date equal or earlier than the 'current date' by default. These results can then be piped into a decommission function.
    Results will return resource groups only with a date value greater than the 'current date' if the '-Future' parameter is used. These results can be used to see which
    resource groups will be decommissioned at a future date.  

	.EXAMPLE
    $subscriptionId = '11111111-2222-3333-4444-555555555555'
    $resourceGroupName = "test"
    Get-ResourceGroup4Decom -SubscriptionId $subscriptionId -ResourceGroupName $resourceGroupName
    ### Retrieves the given resource group ONLY if the tag key: 'Decommission' is present AND if the value is equal or earlier than the current date (dd/MM/yyyy) ###

	.EXAMPLE
    $subscriptionId = '11111111-2222-3333-4444-555555555555'
    $resourceGroupName = "test"
    Get-ResourceGroup4Decom -SubscriptionId $subscriptionId -ResourceGroupName $resourceGroupName -Future
    ### Retrieves the given resource group ONLY if the tag key: 'Decommission' is present AND if the value is later than the current date (dd/MM/yyyy) ###

	.EXAMPLE
    $scopes = @('00000000-1111-2222-3333-444444444444', '01010101-1234-2345-3456-555555555555')
    $MatchedResourceGroups = @()
    Foreach ($Scope in $scopes){
        Set-AzContext -Subscription $Scope
        $ResourceGroupNames = (Get-AzResourceGroup).ResourceGroupName
        Foreach ($rg in $ResourceGroupNames) {
            $MatchedResourceGroups += Get-ResourceGroup4Decom -SubscriptionId $Scope -ResourceGroupName $rg -Future
        }
    }
    $MatchedResourceGroups | Export-Csv -Path C:\temp\ResourceGroups_to_be_decommissioned_in_future.csv -NoTypeInformation
    ### This example will look at all resource groups within the provided scopes/subscriptions and create a CSV file inventory of all resource groups tagged with 'Decommission' ###
    ### The CSV can then be inspected to see what resource groups are maked for decommission and the date decommission will take place ###

	.EXAMPLE
    $subscriptionId = '00000000-1111-2222-3333-444444444444'
    Set-AzContext -Subscription $subscriptionId
    $ResourceGroupNames = (Get-AzResourceGroup).ResourceGroupName
    $MatchedResourceGroups = @()
    Foreach ($rg in $ResourceGroupNames) {
        $MatchedResourceGroups += (Get-ResourceGroup4Decom -SubscriptionId $subscriptionId -ResourceGroupName $rg)
    }
    $MatchedResources | foreach-object {
        Remove-AzResource -ResourceId "$_.ResourceId" -Force -Verbose
    }
    ### This example will look at all resources within the provided subscription and resources tagged with 'Decommission' where the date is the current date or ealier ###

    .PARAMETER SubscriptionId
    Mandatory Parameter.
    Specify the subscription Id. <String>

	.PARAMETER ResourceGroupName
    Mandatory Parameter.
    Specify a valid Resource Group Name to check tags. <String>

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
