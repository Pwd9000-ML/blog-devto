---
title: Automate password rotation with GitHub and Azure (Part 1)
published: true
description: Automate VM password rotation using GitHub and Azure key vault
tags: 'githubactions, devsecops, github, azure'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/maincover1.png'
canonical_url: null
id: 698968
series: Automate password rotation
date: '2021-05-17T16:13:19Z'
---

## :bulb: How to rotate VM passwords using GitHub workflows with Azure Key Vault

{% youtube nSSQtOvwVzA %}

### Overview

Today we are going to look at how we can implement a zero-touch fully automated solution under 15 minutes to rotate all our virtual machines local administrator passwords on a schedule by using a single GitHub workflow and a centrally managed Azure key vault. (The technique/concept used in this tutorial is not limited to only Virtual machines. The same concept can be used and applied to almost anything that requires secret rotation)

In our use case we want to be able to rotate the local administrator password of all virtual machines hosted in an Azure subscription, trigger the rotation manually or on a schedule, ensure each VM has a randomized unique password, and access/store the rotated admin password for each virtual machine inside of the key vault we have hosted in Azure.

In this tutorial we will create a new Azure key vault and a single github workflow as well as a service principal / Azure identity to fully automate everything. We will then populate our key vault with secrets, where the `secret key` will be the `VM hostname` and the `secret value` of the corresponding key will be the `VM password`. (Don't worry about setting an actual password just yet, because out github workflow will update this value for us when we create the github workflow and trigger it later in the tutorial). What's important is that the `secret key` is named the same as what the `VM hostname` is named.

When our github workflow is triggered the workflow will connect to our key vault to retrieve all the `secret keys` (in our case these keys will reflect the names of our `VM hostnames`). The workflow will then generate a unique randomized password and update the corresponding `secret value` for the VM as well as update the VM itself with the newly generated password.

This means that whenever we need to connect to a VM in our subscription using the VMs `local admin account` we would go to our centrally managed key vault and look up the VM name `key` and get it's password `value` to be able to connect to our server, as this password will change automatically on a regular basis by our automation. The virtual machine in this case will be defined in our key vault and have its corresponding password in the key value. This gives us the ability to centrally store, access and maintain all our Azure virtual machines local admin passwords from a central key vault in Azure and our passwords will also be automatically rotated on a regular basis without any manual work. We only need to ensure that the VMs that we want to rotate passwords on have corresponding keys in the key vault, we do also not have to add all our VM names as keys if we do not want to rotate every single VM password and only add the servers in our key vault we do want the passwords to rotate. In fact I would recommend not having domain controller names in the key vault as we would not want to rotate the local admin passwords for servers of this kind.

**Note:** Maintaining all VM password rotation using an Azure key vault is particularly useful for security or ops teams who maintain secrets management and need to ensure that local admin passwords must rotate on a regular basis.

### Protecting secrets in github

Before we start, a quick word on secrets management in GitHub. When using GitHub workflows you need the ability to authenticate to Azure, you may also need to sometimes use passwords, secrets, API keys or connection strings in your source code in order to pass through some configuration of a deployment which needs to be set during the deployment. So how do we protect these sensitive pieces of information that our deployment needs and ensure that they are not in our source control when we start our deployment?

There are a few ways to handle this. One way is to use [GitHub Secrets](https://docs.github.com/en/actions/reference/encrypted-secrets). This is a great way that will allow you to store sensitive information in your organization, repository, or repository environments. In fact we will set up a github secret later in this tutorial to authenticate to Azure to connect to our key vault, retrieve server names and set/change passwords. Even though this is a great feature to be able to have secrets management in GitHub, you may be looking after many repositories all with different secrets, this can become an administrative overhead when secrets or keys need to be rotated on a regular basis for best security practice.

This is where [Azure key vault](https://docs.microsoft.com/en-gb/azure/key-vault/general/overview/?wt.mc_id=DT-MVP-5004771) can be utilized as a central source for all our secret management in our GitHub workflows.

**Note:** Azure key vaults are also particularly useful for security or ops teams who maintain secrets management, instead of giving other teams access to our deployment repositories in GitHub, teams who look after deployments no longer have to worry about giving access to other teams in order to manage secrets as secrets management will be done from an Azure key vault which nicely separates roles of responsibility when spread across different teams.

### Let's get started. What do we need to start rotating our virtual machine local admin passwords?

1. **Azure key vault:** This will be where we centrally store, access and manage all our virtual machine local admin passwords.
2. **Azure AD App & Service Principal:** This is what we will use to authenticate to Azure from our github workflow.
3. **GitHub repository:** This is where we will keep our source control and GitHub workflow / automation.

**Note:** For Steps 1 and 2 above, you can also run the [PreReqs.ps1](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/code/PreReqs.ps1) script, but lets take a look at what that script does in detail below.

### 1. Create an Azure Key Vault

For this step I will be using Azure CLI using a powershell console. First we will log into Azure by running:

```powershell
az login
```

Next we will create a `resource group` and `key vault` by running:

```powershell
az group create --name "GitHub-Assets" -l "UKSouth"
az keyvault create --name "github-secrets-vault3" --resource-group "GitHub-Assets" --location "UKSouth" --enable-rbac-authorization
```

As you see above we use the option `--enable-rbac-authorization`. The reason for this is because our service principal we will create in the next step will access this key vault using the RBAC permission model. You can also create an Azure key vault by using the Azure portal. For information on using the portal see this [link](https://docs.microsoft.com/en-us/azure/key-vault/general/quick-create-portal/?wt.mc_id=DT-MVP-5004771).

Another nice benefit of using the RBAC model is that if anyone wanted to access certain secrets in our key vault, we will be able to give granular access to individual secrets at the secrets object layer rather than the entire key vault.

### Create an Azure AD App & Service Principal

Next we will create our `Azure AD App & Service Principal` by running the following in a powershell console window:

```powershell
# variables
$subscriptionId=$(az account show --query id -o tsv)
$appName="GitHubSecretsUser"
$resourceGroup="GitHub-Assets"
$keyVaultName="github-secrets-vault3"

# Create AAD App and Service Principal and assign to RBAC Role on Key Vault
az ad sp create-for-rbac --name $appName `
    --role "Key Vault Secrets Officer" `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.KeyVault/vaults/$keyVaultName `
    --sdk-auth
```

The above command will create an AAD app & service principal and set the correct `Role Based Access Control (RBAC)` permissions on our key vault we created earlier. We will give our principal the RBAC/IAM role: [Key Vault Secrets Officer](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#key-vault-secrets-officer/?wt.mc_id=DT-MVP-5004771) because we want our workflow to be able to retrieve `secret keys` and also set each `key value`.

The above command will also output a JSON object containing the credentials of the service principal that will provide access to the key vault. Copy this JSON object for later. You will only need the sections with the `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` values:

```JSON
{
  "clientId": "<GUID>",
  "clientSecret": "<PrincipalSecret>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>"
}
```

We also want to give our service principal `clientId` permissions on our subscription in order to look up VMs as well as set/change VM passwords. We will grant our service principal identity the following RBAC role: [Virtual Machine Contributor](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#virtual-machine-contributor/?wt.mc_id=DT-MVP-5004771). Run the following command:

```powershell
# Assign additional RBAC role to Service Principal Subscription to manage Virtual machines
az ad sp list --display-name $appName --query [].appId -o tsv | ForEach-Object {
    az role assignment create --assignee "$_" `
        --role "Virtual Machine Contributor" `
        --subscription $subscriptionId # SubscriptionId where key vault and Vms are hosted
    }
```

We will also give our signed in user the same key vault access to be able to create secrets later on as we will create secrets representing each of our servers a bit later on in this tutorial.

```powershell
# Authorize the operation to create a few secrets - Signed in User (Key Vault Secrets Officer)
az ad signed-in-user show --query id -o tsv | foreach-object {
    az role assignment create `
        --role "Key Vault Secrets Officer" `
        --assignee "$_" `
        --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.KeyVault/vaults/$keyVaultName"
    }
```

### Configure our GitHub repository

Next we will configure our GitHub repository and GitHub workflow. My GitHub repository is called `Azure-VM-Password-Management`. You can also take a look or even use my github repository as a template [HERE](https://github.com/Pwd9000-ML/Azure-VM-Password-Management).

Remember at the beginning of this post I mentioned that we will create a github secret, we will now create this secret on our repository which will be used to authenticate our GitHub workflow to Azure when it's triggered.

1. In [GitHub](https://github.com), browse your repository.

2. Select Settings > Secrets > New repository secret.

3. Paste the JSON object output from the Azure CLI command we ran earlier into the secret's value field. Give the secret the name `AZURE_CREDENTIALS`.

![githubAzureCredentials](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/githubAzureCredentials1.png)

### Configure our GitHub workflow

Now create a folder in the repository called `.github` and underneath another folder called `workflows`. In the workflows folder we will create a YAML file called `rotate-vm-passwords.yaml`. The YAML file can also be accessed [HERE](https://github.com/Pwd9000-ML/blog-devto/blob/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/code/rotate-vm-passwords.yaml).

```yaml
name: Update Azure VM passwords
on:
  workflow_dispatch:
  schedule:
    - cron: '0 9 * * 1'

jobs:
  publish:
    runs-on: windows-latest
    env:
      KEY_VAULT_NAME: github-secrets-vault3
      PASSWORD_LENGTH: 24

    steps:
      - name: Check out repository
        uses: actions/checkout@v3.6.0

      - name: Log into Azure using github secret AZURE_CREDENTIALS
        uses: Azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
          enable-AzPSSession: true

      - name: Rotate VM administrator passwords
        uses: azure/powershell@v1
        with:
          inlineScript: |
            #Generate Randomized Character Set
            #---------------------------------
            $null = Add-Type -AssemblyName System.Web
            $charSet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{]+-[*=@:)}$^%;(_!&#?>/|.'.ToCharArray()
            $crypt = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
            $bytes = New-Object 'System.Array[]'(128)
            For ($i = 0; $i -lt $bytes.Count ; $i++)
            {
                $bytes[$i] = New-Object byte[](2)
            }

            $charSetRandom = New-Object char[](128)
            For ($i = 0 ; $i -lt 128 ; $i++) {
                Do {
                    $crypt.GetBytes($bytes[$i])
                    $num = [System.BitConverter]::ToUInt16($bytes[$i],0)
                } While ($num -gt ([uint16]::MaxValue - ([uint16]::MaxValue % $CharSet.Length) -1))
                $charSetRandom[$i] = $charSet[$num % $charSet.Length]
            }
            $charSetRandom = $charSetRandom -join ''
            #---------------------------------

            #Vm Password rotate Key Vault from Randomized Character Set
            #----------------------------------------------------------
            [int]$length = ${{ env.PASSWORD_LENGTH }}
            $keyVaultName = "${{ env.KEY_VAULT_NAME }}"
            Write-Output "Creating array of all VM names in key vault: [$keyVaultName]."
            $keys = (Get-AzKeyVaultSecret -VaultName $keyVaultName).Name
            Write-Output "Looping through each VM key and changing the local admin password"
            Foreach ($key in $keys) {
              $vmName = $key
              If (Get-AzVm -Name $vmName -ErrorAction SilentlyContinue) {
                $resourceGroup = (Get-AzVm -Name $vmName).ResourceGroupName
                $location = (Get-AzVm -Name $vmName).Location
                Write-Output "Server found: [$vmName]... Checking if VM is in a running state"
                $vmObj = Get-AzVm -ResourceGroupName $resourceGroup -Name $vmName -Status
                [String]$vmStatusDetail = "deallocated"
                Foreach ($vmStatus in $vmObj.Statuses) {
                  If ($vmStatus.Code -eq "PowerState/running") {
                    [String]$vmStatusDetail = $vmStatus.Code.Split("/")[1]
                  }
                }
                If ($vmStatusDetail -ne "running") {
                  Write-Warning "VM is NOT in a [running] state... Skipping"
                  Write-Output "--------------------------"
                }
                Else {
                  Write-output "VM is in a [running] state... Generating new secure Password for: [$vmName]"
                  $passwordGen = (($charSetRandom)[0..64] | Get-Random -Count $length) -join ''
                  $secretPassword = ConvertTo-SecureString -String $passwordGen -AsPlainText -Force
                  Write-Output "Updating key vault: [$keyVaultName] with new random secure password for virtual machine: [$vmName]"
                  $Date = (Get-Date).tostring("dd-MM-yyyy")
                  $Tags = @{ "Automation" = "GitHub-Workflow";  "Password-Rotated" = "true"; "Password-Rotated-On" = "$Date"}
                  $null = Set-AzKeyVaultSecret -VaultName $keyVaultName -Name "$vmName" -SecretValue $secretPassword -Tags $Tags
                  Write-Output "Updating VM with new password..."
                  $adminUser = (Get-AzVm -Name $vmName | Select-Object -ExpandProperty OSProfile).AdminUsername
                  $Cred = New-Object System.Management.Automation.PSCredential ($adminUser, $secretPassword)
                  $null = Set-AzVMAccessExtension -ResourceGroupName $resourceGroup -Location $location -VMName $vmName -Credential $Cred -typeHandlerVersion "2.0" -Name VMAccessAgent
                  Write-Output "Vm password changed successfully."
                  Write-Output "--------------------------"
                }
              }
              Else {
               Write-Warning "VM NOT found: [$vmName]."
               Write-Output "--------------------------"
              }
            }
            #----------------------------------------------------------
          azPSVersion: 'latest'
```

The above YAML workflow is set to trigger automatically every monday at 9am UTC. Which means our workflow will connect to our Azure key vault and get all the VM names we defined, populate the secret values with newly generated passwords and rotate the VMs local admin password with the newly generated password.

**Note:** If you need to change or use a different key vault or change the password length you can change these lines on the yaml file with the name of the key vault you are using:

```txt
// code/rotate-vm-passwords.yaml#L11-L12

KEY_VAULT_NAME: github-secrets-vault3
PASSWORD_LENGTH: 24
```

The current schedule is set to run on every monday at 9am UTC. If you need to change the cron schedule you can amend this line:

```txt
// code/rotate-vm-passwords.yaml#L5-L5

- cron:  '0 9 * * 1'
```

### Populate our key vault with VM names

The last step we now need to do is populate our key vault with some servers. Navigate to the key vault and create a new secret giving the VM name as the secret key:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/addvm.png)

You can just create dummy secrets in the `value` field as these will be overwritten when our workflow is triggered:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/populate.png)

**Note:** Only add servers that you want to rotate passwords on, I would recommend **NOT** adding any servers or VMs such as **Domain Controllers** to the key vault. Also as you may recall when we created our key vault, we set the key vault to use the RBAC access model, so if someone requests access to a specific secret we can now allow access on the object level meaning we can give access to a specific secret (and not any other secrets). if we used the `Vault Access Policy` model access can only be given to the entire vault.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/vaultiam.png)

As you can see I have 3 vms defined. When our workflow is triggered it will automatically populate our VM keys with randomly generated passwords and rotate them on a weekly basis at 9am on a monday, if a VM key exists in the key vault but the VM does not exist in the Azure subscription or our principal does not have access to the VM, it will be skipped. Similarly if a VM is de-allocated and the power state is OFF it will also be skipped. The rotation will only happen on VMs that exist and are powered ON. Let's give it a go and see what happens when we trigger our workflow manually.

We can trigger our workflow manually by going to our github repository (The trigger will also happen automatically based on our cron schedule):

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/trigger.png)

Let's take a look at the results of the workflow:

![results](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/results.png)

As you can see I have 3 VMs defined in my key vault `pwd9000vm01` was powered on and so it's password was rotated. `pwd9000vm02` was found, but was de-allocated so was skipped. `pwd9000vm03` is a VM which no longer exists in my subscription so I can safely remove the server key from my key vault.

Now lets see if I can log into my server which have had its password rotated:

![login](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/GitHub-Automate-VM-Password-Rotation-Part1/assets/login.gif)

I hope you have enjoyed this post and have learned something new.  
Using the same techniques I have shown in this post, you can pretty much use this process to rotate secrets for almost anything you can think of, whether that be SQL connection strings or even API keys for your applications.  
You can also find and use this [github repository](https://github.com/Pwd9000-ML/Azure-VM-Password-Management) I used in this post as a template in your own github account to start rotating your VM passwords on a schedule today. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
