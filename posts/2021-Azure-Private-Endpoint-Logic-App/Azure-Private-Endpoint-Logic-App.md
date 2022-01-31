---
title: Securing Azure Logic apps with Private Endpoints
published: true
description: Azure - Private Endpoint Azure Logic apps
tags: 'logicapps, azure, cloudsecurity, cloudnetworking'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/main-cover-logicapp.png'
canonical_url: null
id: 732865
date: '2021-06-19T15:11:43Z'
---

## What is an Azure Logic app?

[Azure Logic Apps](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-overview) is a cloud-based platform for creating and running automated workflows that integrate your apps, data, services, and systems. With this platform, you can quickly develop highly scalable integration solutions for your enterprise and business-to-business (B2B) scenarios. As a member of Azure Integration Services, Logic Apps simplifies the way that you connect legacy, modern, and cutting-edge systems across cloud, on premises, and hybrid environments.

## What is Azure Private Link (Private Endpoint)?

[Azure Private Link](https://docs.microsoft.com/en-us/azure/private-link/private-link-overview) (Private Endpoint) allows you to access Azure PaaS services over a Private IP address within the VNet. The PaaS resource gets a new private IP via a virtual network interface (NIC) on your Virtual Network (VNET) attached to the PaaS resource or service, making the resource truly an internal **private** resource to your virtual network. When you send traffic to the resource that has been private endpointed, it will always ensure traffic stays within your VNet boundary.

![private-link](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/private-link.png)

## What's new in Azure Logic apps?

There has been some major architectural changes and improvements made in recent days to Azure Logic apps (multi-tenant implementation), especially the new logic apps runtime which is a re-hostable containerised, single-tenant runtime, which is built on top of the **Azure Functions runtime**, adding some excellent new features that we can now utilise in our logic apps. Such as enabling [managed service identity (MSI)](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview), cross-platform support, local development and testing using VSCode, enabling new advanced networking features such as **private endpoints** which we will focus on in todays tutorial or even running our logic apps in a dedicated compute resource in Azure, Docker or Kubernetes environments.

## What do we need?

1. **Azure Virtual Network:** We will need either a new or an existing VNET in which we can attach our logic app private endpoint interface.
2. **Azure Private DNS Zone:** For this tutorial we will also create a Private DNS zone to host our [private endpoint DNS Configuration](https://docs.microsoft.com/en-us/azure/private-link/private-endpoint-dns#azure-services-dns-zone-configuration).
3. **Azure Logic App:** We will need to create the new **single-tenant** logic app as described above.
4. **Private Endpoint:** We will use a private endpoint to connect our logic app to our VNET.

## Creating an Azure Virtual Network (VNET)?

For this section I will be using Azure CLI in a powershell console. First we will log into Azure by running:

```powershell
az login
```

Next we will create a **resource group**, and a **VNET** by running:

```powershell
# variables.
$resourceGroupName = "MyLogicAppRG"
$vnetName = "LogicAppNet"
$subnetName = "LogicAppSub"
$region = "uksouth"

# Create a resource resourceGroupName
az group create --name "$resourceGroupName" --location "$region"

# Create a new Vnet
az network vnet create `
  --name "$vnetName" `
  --resource-group "$resourceGroupName" `
  --address-prefixes 10.2.0.0/16 `
  --subnet-name "$subnetName" `
  --subnet-prefixes 10.2.0.0/24
```

## Creating an Azure Private DNS Zone?

We will need to register our private endpoint in DNS so for this step we will create a Private DNS Zone and link the **Azure services DNS Zone configuration** for **azurewebsites.net** because our new logic app runtime is within an **App Service Plan (ASP)** we will configure the zone as `privatelink.azurewebsites.net`.

To see more detailed information on DNS configurations for private endpoints please see [DNS Integration Scenarios](https://github.com/dmauser/PrivateLink/tree/main/DNS-Integration-Scenarios) for additional information, as well as [Private link DNS Zone configuration](https://docs.microsoft.com/en-us/azure/private-link/private-endpoint-dns#azure-services-dns-zone-configuration)

Next we will run:

```powershell
# Create Private DNS Zone
az network private-dns zone create `
    --resource-group "$resourceGroupName" `
    --name "privatelink.azurewebsites.net"

# Link Private DNS Zone with VNET
az network private-dns link vnet create `
    --resource-group "$resourceGroupName" `
    --name "$vnetName-DNS-Link" `
    --zone-name "privatelink.azurewebsites.net" `
    --virtual-network "$vnetName" `
    --registration-enabled "true"
```

![private-dns](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/private-dns.png)

## Creating an Azure Logic app (Single-tenant)?

Now that we have everything in place we will create our logic app. Navigate to the Azure portal and go to the resource group we created and create a new **Logic app (Standard)** resource.

![CreateLogicApp](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/CreateLogicApp.png)

Under the **Basics** blade, add the following **Instance Details:**

| Name           | Value              |
| -------------- | ------------------ |
| Type           | Standard (Preview) |
| Logic App name | {Name}             |
| Publish        | Workflow           |
| Region         | {Region}           |

![CreateLogicAppBasics](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/CreateLogicAppBasics.png)

Under the **Hosting** blade, add the following **Plan:**

| Name         | Value                    |
| ------------ | ------------------------ |
| Plan type    | Workflow Standard        |
| Windows Plan | {ASP - App Service Plan} |
| Sku and size | {SKU}                    |

![CreateLogicAppHosting](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/CreateLogicAppHosting.png)

Move to the next blade **Monitoring** and enable/disable **Application Insights** and then add any **Tags**. Click on **Review + create** and create the new logic app.

## Creating the Private Endpoint?

Before we continue to our last step, also note that our newly created Logic App has already been enabled with a `system assigned managed identity`. Pretty neat!

![MSI](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/msi.png)

Next we will create our private endpoint. Select the **Networking** blade and click on **Private endpoints**.

![bladeprivateendpoint](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/bladeprivateendpoint.png)

**Note:** You will see that our inbound address to access our logic app is currently configured using a `public endpoint` (Public IP address).

![pubip](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/pubip.png)

Under the **Private Endpoint connections** blade, click **+ Add** and add the following:

| Name                            | Value                   |
| ------------------------------- | ----------------------- |
| Name                            | {Name private endpoint} |
| Subscription                    | {Subscription}          |
| Virtual Network                 | {Virtual Network Name}  |
| Subnet                          | {Subnet Name}           |
| Integrate with private DNS Zone | Yes                     |

![peconfig](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/peconfig.png)

**Note:** You will now see that our inbound address to access our logic app has changed and is configured to use our `private endpoint` (Private IP address from our VNET).

![privip](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/privip.png)

Make a note of the **private IP** and navigate to the Azure Private DNS zone we created earlier. Click on **+ Record set** and add the following:

| Name       | Value                             |
| ---------- | --------------------------------- |
| Name       | {Name of Logic App}               |
| Type       | A                                 |
| TTL        | 1 Hour                            |
| IP address | {Private Inbound IP of Logic App} |

![privipconfig](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/privipconfig.png)

That is it! We have now secured our logic app to be a completely internal resource keeping it within our network boundaries as if it was an internally hosted resource inside of our Virtual Network.

![secdiag](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/secdiag.png)

## Testing our Logic App?

Let's test out our Logic App and see what happens if we try to access it from an external source vs. a source from our VNET such as a Virtual machine running inside of our VNET.

HTTP POST Url from an external source:

![external](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/external.png)

HTTP POST Url from an internal Virtual Machine running inside of our VNET:

![internal](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021-Azure-Private-Endpoint-Logic-App/assets/internal.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021-Azure-Private-Endpoint-Logic-App/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
