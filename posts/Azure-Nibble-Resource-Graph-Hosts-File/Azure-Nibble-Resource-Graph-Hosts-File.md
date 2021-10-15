---
title: Azure Nibble - Hosts File Generator using KQL for App Services
published: true
description: Azure - Nibble - Hosts File Generator using KQL for App Services in Resource Graph
tags: 'tutorial, azure, productivity, learning'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/assets/main.png'
canonical_url: null
id: 817556
date: '2021-09-08T15:29:44Z'
---

## Azure Resource Graph

[Azure Resource Graph](https://docs.microsoft.com/en-gb/azure/governance/resource-graph/overview) allows us to quickly and efficiently query across Azure subscriptions. Analyse cloud inventory using complex queries launched programmatically or from the Azure portal. The query language used is known as **[Kusto Query Lanuage (KQL)](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query)**.

## Hosts File Generator

Recently I was looking into a mechanism to generate a hosts file to add a very large number of Azure App services that have been private endpoint enabled for both the default as well as the scm hosts of each app, so that these apps could be tested without/outside of DNS, by using a hosts file instead. This has led me to write a short KQL query that will do just this. I will share this query with you today.

In the Azure portal search for **Resource Graph Explorer**:

![rge](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/assets/rge.png)

In the query editor add the following lines of code:

```KQL
Resources
| where type =~ "microsoft.web/sites"
| mvexpand pe = properties.privateEndpointConnections
| extend peip = tostring(pe.properties.ipAddresses[0])
| mvexpand hosts = properties.hostNameSslStates
| project peip, hosts=tostring(hosts.name)
| order by peip asc
```

You can also select the scope at which you want to run the query:

![scope](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/assets/scope.png)

Then select **Run query**:

![run](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/assets/run.png)

That is it, you can now export the results to a CSV and copy the results over into a hosts txt file. In addition you can also save the query for future re-use to run it again if any private IP addresses of your App services private endpoints change to get an updated hosts file formatted result.

You can also select whether you want to save the query as a **private query** or a **shared query**. The later allows you to save the query as an object in a resource group that others can also access and run.

![save](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/assets/save.png)

The **Kusto Query Language** is truly a powerful query tool that can be utilized in many different scenarios and is the main query language used in Azure Data Explorer and Azure Monitor. To learn more about KQL have a look at the following [sample queries](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/tutorial?pivots=azuremonitor) that can be used in Azure Monitor.

I hope you have enjoyed this post and have learned something new. You can also find the query code sample for this tutorial on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/code) page. :heart:

### _Author_

{% user pwd9000 %}

Like, share, follow and connect with me on:

:octopus: [GitHub](https://github.com/Pwd9000-ML)  
:penguin: [Twitter](https://twitter.com/pwd9000)  
:space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)  
