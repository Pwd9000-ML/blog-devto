---
title: Access internal APIM securely with Private Link Service
published: false
description: Azure - internal APIM + Private Link Service
tags: 'tutorial, azure, productivity, security'
cover_image: assets/PLSMain.png
canonical_url: null
id: 756521
---


Add any tags if required and then create the private link service.  

Now that our Private Link Service is created I will navigate to my other subscription I created separately. There I will create and link a **Private Endpoint** on an external non-peered VNET which resides in the **EAST US** region. You can do the same by creating a new VNET in a different region and leaving it un-peered.

In the Azure portal go to `Private Link` and select `+ Add` under `Private endpoints`.

![addpe01](./assets/addpe01.png)

Under the **Basics** blade, select the subscription, and region where the external VNET resides (in my case this is in EAST US):

| Name            | Value               |
| --------------- | ------------------- |
| Resource Group  | APIM                |
| Name            | APIM-PE             |
| Region          | East US             |

![basicspe1](./assets/basicspe1.png)

Under the **Resource** blade, you can connect to the PLS service we created by it's `resource ID` or by selecting the following:

| Name            | Value                                 |
| --------------- | ------------------------------------- |
| Subscription    | [Subscription hosting PLS]            |
| Resource Type   | Microsoft.Network/privateLinkservices |
| Resource        | APIM-PLS                              |

![resourcepe](./assets/resourcepe.png)

Under the **Configuration** blade, select the external virtual network (in my case this is hosted in EAST US and my VNET is called `External`):

| Name            | Value                  |
| --------------- | ---------------------- |
| Virtual Network | [external VNET name]   |
| Subnet          | [External VNET subnet] |

![configpe](./assets/configpe.png)

Add any tags if required and then create the private endpoint.  

And that is it, we have now successfully created a secure entry point to access our private APIM service from a non-peered external VNET hosted in EAST US. I have a VM running in my EAST US external VNET in which we can test our connectivity via the private endpoint we just created. In my case the private endpoint IP allocated to APIM-PE is: `192.168.0.6`.

![peip](./assets/peip.png)

My test VM running in my external VNET has an IP of: `192.168.0.4`.

![testvmip1](./assets/testvmip1.png)

To test connectivity to my APIM I will require my APIM endpoints and for this test I will just configure my endpoints on my test machine using the local HOSTS file, but point my APIM endpoints to the APIM-PE (private endpoint we created).

![apimend1](./assets/apimend1.png)

Let's see if our connectivity is working:

![tst1](./assets/tst1.png)

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/Azure-Private-Link-Service-Internal-APIM/code). :heart:

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
