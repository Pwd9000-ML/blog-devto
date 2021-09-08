---
title: Azure Nibble - Hosts File Generator using KQL for App Services
published: false
description: Azure - Nibble - Hosts File Generator using KQL for App Services in Resource Graph
tags: 'tutorial, azure, productivity, learning'
cover_image: https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/assets/main.png
canonical_url: null
id: 817556
---

## Azure Resource Graph

[Azure Resource Graph](https://docs.microsoft.com/en-gb/azure/governance/resource-graph/overview) allows us to quickly and efficiently query across Azure subscriptions. Analyse cloud inventory using complex queries launched programmatically or from the Azure portal. The query language used is known as **[Kusto Query Lanuage (KQL)](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query)**.

## Hosts File Generator

Very recently I was looking into a mechanism to generate a hosts file to add a very large number of Azure App services that have been private endpoint enabled for both the default as well as the scm hosts of each app, so that these apps could be tested without DNS and by using a hosts file instead. This has led me to write a short KQL query that will do just this and will share with you today.  

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

![run]()

That is it, you can now export the results to a CSV and copy the results over into a hosts txt file. In addition you can also save the query to run it again if for any reason the IP addresses for our App services private endpoints ever change to get an updated hosts file formatted result.

I hope you have enjoyed this post and have learned something new. You can also find the query code sample for this tutorial on my [Github](https://github.com/Pwd9000-ML/blog-devto/tree/master/posts/Azure-Nibble-Resource-Graph-Hosts-File/code) page. :heart:

### _Author_

{% user pwd9000 %}
