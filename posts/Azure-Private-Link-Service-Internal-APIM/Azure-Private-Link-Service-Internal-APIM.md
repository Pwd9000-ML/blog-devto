---
title: Access internal APIM securely with Private Link Service
published: false
description: Azure - internal APIM + Private Link Service
tags: 'tutorial, azure, productivity, security'
cover_image: assets/main.png
canonical_url: null
id: 755878
---

## What is Azure Private Link Service?

[Azure Private Link service](https://docs.microsoft.com/en-us/azure/private-link/private-link-service-overview) is the reference to your own service that is powered by Azure Private Link. Your service that is running behind Azure Standard Load Balancer can be enabled for Private Link access so that consumers to your service can access it privately from their own VNets. Your customers can create a private endpoint inside their VNet and map it to this service.

![privateLinkService](./assets/privateLinkService.png)

### Access internal API Management Service securely with Private Link Service from an external non-peered VNET

In todays tutorial we will look into a use case for this service

### _Author_

Marcel.L - pwd9000@hotmail.co.uk
