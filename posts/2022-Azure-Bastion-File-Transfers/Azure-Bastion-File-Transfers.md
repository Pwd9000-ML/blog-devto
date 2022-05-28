---
title: Upload files to Azure Virtual Machines with Azure Bastion in tunnel mode.
published: false
description: Upload files to an Azure Linux VM using Azure Bastion on Windows using the SSH native Client
tags: 'azure, bastion, cloudnetworking, tunnel'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2022-Azure-Bastion-File-Transfers/assets/main.png'
canonical_url: null
id: 1093908
---

## Overview

**NOTE:** The topics shown in this blog post is currently in **Public Preview** as of February 2022 and has potential to change.

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
- The Resource ID for the VM to which you want to upload files to. (In our case it will be our Linux VM hosted in Azure).

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my published [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2022-Azure-Bastion-File-Transfers/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
