---
title: Upload files to Azure Virtual Machines with Azure Bastion in tunnel mode
published: false
description: Upload files to an Azure Linux VM using Azure Bastion on Windows using the SSH native Client
tags: 'azure, bastion, cloudnetworking, tunnel'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/main1.png'
canonical_url: null
id: 1093908
---

## Overview

**Note:** The topics shown in this blog post is currently in **Public Preview** as of February 2022 and has potential to change.

In todays tutorial we will take a look at a cool new feature that is available to us in [Azure Bastion](https://docs.microsoft.com/en-us/azure/bastion/bastion-overview) whereby we can upload and download files to a VM using a native client. You can read more about [this feature](https://docs.microsoft.com/en-us/azure/bastion/vm-upload-download-native) on Microsoft Docs.

Today we will look specifically at how we can upload files from a **Windows OS** based local machine using **WinSCP** to a Linux Azure VM using Azure Bastion in **Tunnel Mode**.

There are a few important notes and limitations I would like to cover off first before we start:

- File transfers are supported using the **native client** only. You can't upload or download files using PowerShell or via the Azure portal.
- To both **upload** and **download** files, you must use the **Windows** native client and **RDP**.
- You can upload files to a VM using the native client of your choice and either **RDP** or **SSH**.
- This feature requires the **Standard SKU**. The Basic SKU doesn't support using the native client.

In this demonstration, since our target VM is running a Linux OS we will be using Azure Bastion in **tunnel mode**, we will only be able to upload files and downloading files is **NOT** supported yet.

If you want to see how you can **Upload** and **Download** files using the native Windows RDP client, please see: [Upload and download files - RDP](https://docs.microsoft.com/en-us/azure/bastion/vm-upload-download-native#rdp)

## Pre-requisites

To get started you'll need a few things, firstly:

- An Azure Subscription
- An Azure Bastion (Standard SKU)
- Azure CLI (Version 2.32 or later)
- WinSCP (Version 5.19.6 or later)
- The Resource ID of the VM to which you want to upload files to. (In my case it will be a Linux VM hosted in Azure).

## Setting up an Azure Bastion (Standard SKU)

**Note:** Before we can set up an Azure Bastion host we need an Azure Virtual Network with a **/26** subnet called **AzureBastionSubnet**. I already have a VNET and subnet set up in my environment:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/vnet.png)

Next I will be using **Azure CLI** in a [PowerShell Script](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-Azure-Bastion-File-Transfers/code/Bastion_Setup.ps1) to set up the Bastion Host:  

```powershell
#### Ensure VNET and AzureBastionSubnet with /26 CIDR is available before creation of Bastion Host ####
#Login to Azure
az login
az account set --subscription "Your-Subscription-Id"

#Set Variables
$location = "uksouth"
$bastionName = "Pwd9000-EB-Bastion"
$bastionPip = "Pwd9000-EB-Bastion-Pip"
$bastionRG = "Pwd9000-EB-Network"
$bastionVNET = "UKS-EB-VNET"

#Deploy Public IP for Bastion
az network public-ip create --resource-group $bastionRG `
    --name $bastionPip `
    --location $location `
    --sku "Standard"
    
#Deploy Bastion
az network bastion create --name $bastionName `
    --public-ip-address $bastionPip `
    --resource-group $bastionRG `
    --vnet-name $bastionVNET `
    --location $location `
    --sku "Standard"
```

The script created a Public IP and Bastion host as follow:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/resources.png)

Next we will enable native client support. Navigate to the **Bastion Configuration** as shown below and enable `Native client support`:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/config.png)

**Note:** If you are running the **Basic SKU** of Azure Bastion, you can also use this area to upgrade the SKU to **Standard**. Once you upgrade, you can't revert back to the Basic SKU without deleting and reconfiguring Bastion. Currently, this setting can be configured in the Azure portal only.

## Opening a Bastion Tunnel

Now with our Azure Bastion set up and configured we will open a secure tunnel through Azure Bastion to our Azure hosted Linux VM, which we can then connect to using WinSCP to start uploading files to our VM.  

Navigate to the Linux VM in the Azure portal and go to **Properties** and mak a not eof the **Resource ID** as we will need this value when we open the Bastion tunnel.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/rid.png)

Next, open PowerShell and run the below [Open_Tunnel.ps1](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-Azure-Bastion-File-Transfers/code/Open_Tunnel.ps1) script using your environments variables to open a tunnel on port `50022`:  

```powershell
#Login to Azure
az login
az account set --subscription "Your-Subscription-Id"

#Set Variables
$bastionName = "Pwd9000-EB-Bastion"
$bastionRG = "Pwd9000-EB-Network"
$targetVmResourceId = "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Linux-Vms/providers/Microsoft.Compute/virtualMachines/mylinuxvm9000"

az network bastion tunnel --name $bastionName `
    --resource-group $bastionRG `
    --target-resource-id $targetVmResourceId `
    --resource-port "22" `
    --port "50022"
```

As you can see we now have a tunnel open on port: `50022` on out local Windows machine.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/tunnel.png)

**Note:** Do not close this shell window as it will close the tunnel, leave the session open.  

## Connect WinSCP to the running Bastion Tunnel

Next we will open WinSCP and connect to our localhost (127.0.0.1) to the open port: `50022` on the tunnel that is running:

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/winscp1.png)

**Note:** The file protocol is `SCP` and the **UserName** and **Password** is that of our target VM.

However in my case I will connect with a private key instead of a UserName and Password. To do so, in WinSCP on the screen above click on **Advanced** and select the private key you want to use.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/winscp3.png)

**Note:** If you are using a `PEM` private key, WinSCP will automatically create a converted copy of the `PEM` in PPK format. If you select **OK** in the following screen it will ask you where to save the converted `PPK` formatted key:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/winscp2.png)

Now select **Login**. You will then see a warning about connecting to an unknown server, click **Yes** to continue:  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/winscp4.png)

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/winscp5.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-Azure-Bastion-File-Transfers/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
