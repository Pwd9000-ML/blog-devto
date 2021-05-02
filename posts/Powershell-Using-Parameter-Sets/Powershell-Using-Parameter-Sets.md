---
title: PowerShell - Using Parameter Sets
published: false
description: Powershell - How to use parameter sets in PowerShell functions
tags: 'powershell, howtoposh'
cover_image: assets/PowerShellHowTo.png
canonical_url: null
id: 685263
---

This article and demo function can also be found on [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Powershell-Using-Parameter-Sets/code).

## What are parameter sets in PowerShell and how to use them :bulb:

Have you ever wondered when you are writing a PowerShell function or commandlet how you can make only certain parameters be presented to the consumer of the function in certain scenarios? That's where parameter sets come in :smile:  

We will look at the following test function on exactly how this can be used.  

```txt
// code/demo-function.ps1
```

The first step is to add a `DefaultParameterSetName`. We can set that in our `[CmdletBinding]()` as follow:  

```txt
// code/demo-function.ps1#L2
```

![testFunction](./assets/TestFunction.gif)

You can also find some very helpful documentation on parameter sets on [Microsoft Docs](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parameter_sets?view=powershell-7.1).
