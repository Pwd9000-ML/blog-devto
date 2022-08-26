---
title: Automate Azure Role Based Access Control (RBAC) using Github
published: true
description: Github - Automate Azure RBAC
tags: 'automation, azure, DevSecOps, githubactions'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Github-Automate-Azure-RBAC/assets/github-azure.png'
canonical_url: null
id: 707024
date: '2021-05-24T16:04:03Z'
---

{% youtube Li9lSbZJCzo %}

## What are Azure Roles and Custom Definitions?

When you start working more and more with Azure permissions you will undoubtedly have used Azure RBAC (also known as IAM) and have most likely used some of the great [built-in roles](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles) that have been created and provided by Microsoft, but sometimes you may come across a requirement or a need to have a very specific role tailored with a set of permissions that are more granular than what comes out of the box in a standard Azure (RBAC) built-in role.

Luckily Azure offers a great deal of flexibility when it comes to defining your own custom roles vs built-in roles. This is where [Custom Role Definitions](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions) comes into play.

Today we will look at how we can utilize Github actions in creating and also maintaining our Azure (RBAC) custom role definitions from a Github repository through source control and automatically publishing those changes in Azure through a Github actions workflow without much effort. If you are still a bit unclear on what Azure RBAC is, or wanted more information have a look at the [Microsoft Docs](https://docs.microsoft.com/en-us/azure/role-based-access-control/overview).

### Protecting secrets in github

Before we start using Github actions in this tutorial we will need the ability to authenticate to Azure. We will first create an `'Azure AD App & Service Principal'` giving the identity we create the relevant permissions to maintain custom RBAC roles and then store this identity credential as an encrypted [Github Secret](https://docs.github.com/en/actions/reference/encrypted-secrets) called `'AZURE_CREDENTIALS'` to use in our actions workflow to authenticate to Azure.

### Create an Azure AD App & Service Principal

For this step I will be using Azure CLI using a powershell console. First we will log into Azure by running:

```powershell
az login
```

Next we will create our `Azure AD App & Service Principal` by running the following in a powershell console window:

```powershell
# variables
$subscriptionId=$(az account show --query id -o tsv)
$appName="Github-RBAC-Admin"

# Create AAD App and Service Principal and assign Management Group Reader Role on Subscription
az ad sp create-for-rbac --name $appName `
    --role "Management Group Reader" `
    --scopes /subscriptions/$subscriptionId `
    --sdk-auth

# Assign additional RBAC role to Service Principal - User Access Administrator on Subscription
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "User Access Administrator" `
        --subscription $subscriptionId
    }
```

The above command will output a JSON object with the role assignment credentials. Copy this JSON object for later when we configure our github repository. You will only need the sections with the `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

**NOTE:** The service principal we created has the RBAC/IAM roles: `'Management Group Reader'` and `'User Access Administrator'`, because we want our actions workflow script to be able to look at management groups and be able to change context as well as be able to create or amend role definitions at the scope/Subscription we want to maintain. In my case I only want to maintain RBAC for a single subscription. You can change the `--scopes` parameter to change the permission scope of the service principal to a `management group` instead if you want to use the actions workflow to maintain RBAC over multiple subscriptions.

### Configure our Github repository

Firstly we will need to have a Github repository where we can store our custom role definition JSON files. If you need more information on how to set up a new Github repository, have a look [here](https://docs.github.com/en/github/getting-started-with-github/quickstart/create-a-repo).

I called my repository `[Azure-Role-Definitions]`. In my repository I have created 3 main folder paths: ![rbac-repo-structure](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Github-Automate-Azure-RBAC/assets/rbac-repo-structure.png)

1. **.github/workflows:** Here we will define and create our Github actions yaml file.

2. **roleDefinitions:** Here we will keep all our Azure custom role definition JSON files. This is also where we will maintain our custom role definitions when we need to make changes or even create new definitions we want to publish to Azure.

3. **scripts:** Here we will keep a simple PowerShell script that will be used in our actions yaml file.

Clone this newly created or existing repository and let's get started to create our first role definition JSON file now. You can also use my repo as a template by going [HERE](https://github.com/Pwd9000-ML/Azure-Role-Definitions).

Remember in an earlier step we created an azure AD app & service principal and got a JSON object as output. We will now create a secret on our repository using the JSON object output, which our actions workflow will use to authenticate to Azure when it's triggered.

1. In [GitHub](https://github.com), browse your repository.

2. Select Settings > Secrets > New repository secret.

3. Paste the JSON object output from the Azure CLI command we ran earlier into the secret's value field. Give the secret the name `AZURE_CREDENTIALS`.

![githubAzureCredentials](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Github-Automate-Azure-RBAC/assets/githubAzureCredentials.png)

### Configure our first Custom Role Definition

We will create a simple role definition JSON that will only allow resource health read permissions, because we want to give someone the ability to look at resource health within a subscription in our tenant.  
We will use the following JSON template structure to build our definition:

```JSON
{
    "Name": "",
    "Id": "",
    "IsCustom": true,
    "Description": "",
    "Actions": [],
    "NotActions": [],
    "DataActions": [],
    "NotDataActions": [],
    "AssignableScopes": []
}
```

You can find more information on what each property in the JSON structure means [HERE](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions#role-definition).  
Our completed definition we will use in this tutorial will look something like below.  
**Note:** Change the `"AssignableScopes"` value with the subscription ID you want to publish and make this role available for use on.

```JSON
{
    "Name": "GH-CUSTOM-RESOURCEHEALTH-Reader",
    "Id": "",
    "IsCustom": true,
    "Description": "Users with rights to only view Azure resource/service/subscription health.",
    "Actions": [
        "Microsoft.ResourceHealth/*/read"
    ],
    "NotActions": [],
    "DataActions": [],
    "NotDataActions": [],
    "AssignableScopes": [
        "/subscriptions/<subscriptioId1>"
    ]
}
```

**Note:** We can add more subscriptions to our assignable scopes or even use management groups if required. But for the purpose of this tutorial we only want to make the role available to a single Azure subscription. You will also notice that `"Id": ""` is blank as our actions workflow script will take care of this value later on. Here are a few more valuable links for reference when creating custom role definitions:

- [Operations](https://docs.microsoft.com/en-us/azure/role-based-access-control/resource-provider-operations)
- [Operations format](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions#operations-format)
- [Assignable Scopes](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions#assignablescopes)

### Configure our Github actions workflow

The next thing we will do is create our Github actions workflow and script. Lets create the following `yaml` file in our repository.

1. Under `[.github/workflows]` create the following YAML file `[Rbac-Apply.yml]`:

   This is going to be our main actions workflow called: `[Rbac-Apply]`.  
   **Note:** The workflow will only trigger on changes made to the repository path `[roleDefinitions/*]`.

   ```YAML
    # '.github/workflows/Rbac-Apply.yml'
    name: RBAC-Apply
    on:
    push:
        paths:
        - 'roleDefinitions/*'

    jobs:
    publish:
        runs-on: windows-latest

        steps:
        - name: Check out repository
        uses: actions/checkout@v2
        with:
            fetch-depth: 0

        - name: Get changed files in .\roleDefinitions
        shell: powershell
        run: echo "CHANGED_FILES=$(git diff --name-only ${{ github.event.before }}..${{ github.event.after }})" | Out-File -FilePath $Env:GITHUB_ENV -Encoding utf8 -Append

        - name: Log into Azure using github secret AZURE_CREDENTIALS
        uses: Azure/login@v1
        with:
            creds: ${{ secrets.AZURE_CREDENTIALS }}
            enable-AzPSSession: true

        - name: 'Get changed role definitions'
        shell: powershell
        run: |
        $changedFiles = "${{ env.CHANGED_FILES }}"
        $changedFiles = $changedFiles.Split(' ')
        $buildSourcesDirectory = $env:GITHUB_WORKSPACE
        $resultArray = @()
        Foreach ($file in $changedFiles) {
            if ($file -like "roleDefinitions/*") {
            $filePath = "$buildSourcesDirectory\$file"
            $resultArray += $filePath
            }
        }
        Write-Output "The following role definitions have been created / changed:"
        Write-Output "$resultArray"
        #Create a useable github environment variable array to string that will be used in powershell script
        $psStringResult = @()
        $resultArray | ForEach-Object {
            $psStringResult += ('"' + $_.Split(',') + '"')
        }
        $psStringResult = "@(" + ($psStringResult -join ',') + ")"
        #Set github env variable to use in powershell script as input
        echo "ROLE_DEFINITIONS=$psStringResult" | Out-File -FilePath $Env:GITHUB_ENV -Encoding utf8 -Append
        Write-Output "Convert array to psString:"
        Write-Output $psStringResult

        - name: Create - Update role definitions
        uses: azure/powershell@v1
        with:
            inlineScript: |
            .\scripts\set-rbac.ps1 -RoleDefinitions ${{ env.ROLE_DEFINITIONS }}
            azPSVersion: 'latest'
   ```

Now under our repository folder path `[scripts]` we will create a PowerShell script called `[Set-Rbac.ps1]`.  
**Note:** This powershell script calls cmdlets from the AZ module, so if a [self-hosted Github actions runner](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners) is used instead of a `Github-hosted runner`, please ensure that the AZ module is installed and configured on your runner. The below script may be amended to suit your environment better if you use deeply nested management groups. What the script below does is read in each JSON role definition from our repo under the path `./roleDefinitions/*.json` and then sets the context to one of the subscriptions defined in the JSON file `'AssignableScopes'`. Once in the context of a subscription, the script will evaluate whether a Custom Role Definition already exists in the context of the subscription, if it does the script will update the role definition with any changes or if the role does not exist it will be created.

```powershell
# 'scripts/set-rbac.ps1'
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
```

That's it, now each time a new JSON definition is added or an existing definition is amended on our repository under the path `./roleDefinitions/` the changes when pushed to our repo will trigger our github actions workflow and will auto-magically create or update any existing RBAC roles in Azure and we can now use proper version control and automation around governing our Azure RBAC custom role definitions using Github Actions.

![run-output](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Github-Automate-Azure-RBAC/assets/run-output.png)

We can also confirm that our role is now published and usable in Azure. :smile:

![Azure-Role-Published](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Github-Automate-Azure-RBAC/assets/Azure-Role-Published.gif)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-Github-Automate-Azure-RBAC/code) page or you can even use my repo as a template [HERE](https://github.com/Pwd9000-ML/Azure-Role-Definitions) :heart:

If you wanted to see how to do this using DevOps yaml pipelines instead have a look at one of my other posts below: {% link <https://dev.to/pwd9000/automate-azure-role-based-access-control-rbac-with-devops-2ehf> %}

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
