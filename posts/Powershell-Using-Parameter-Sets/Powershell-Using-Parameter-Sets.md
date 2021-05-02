---
title: PowerShell - Using Parameter Sets
published: true
description: Powershell - How to use parameter sets in PowerShell functions
tags: 'powershell, howtoposh, powershelltips'
cover_image: assets/PowerShellHowTo.png
canonical_url: null
id: 685386
date: '2021-05-02T12:29:00Z'
---

This article and demo function can also be found on [Github](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/Powershell-Using-Parameter-Sets/code).

## What are parameter sets in PowerShell and how to use them :bulb:

Have you ever wondered when you are writing a PowerShell function or commandlet how you can make only certain parameters be presented to the consumer of the function in certain scenarios? That's where parameter sets come in :smile:

We will look at the following test function on exactly how this functionality can be used.

```txt
// code/demo-function.ps1

Function Test-ParameterSets {
    [CmdletBinding(SupportsShouldProcess, DefaultParameterSetName="Default")]
    Param (
        [Parameter(Mandatory=$false)]
        [string]$DefaultParameter1,
        [Parameter(Mandatory=$false)]
        [string]$DefaultParameter2,
        [Parameter(Mandatory=$false, ParameterSetName="A")]
        [Switch]$A,
        [Parameter(Mandatory=$false, ParameterSetName="A")]
        [string]$AParameter1,
        [Parameter(Mandatory=$false, ParameterSetName="A")]
        [string]$AParameter2,
        [Parameter(Mandatory=$false, ParameterSetName="B")]
        [Switch]$B,
        [Parameter(Mandatory=$false, ParameterSetName="B")]
        [string]$BParameter1,
        [Parameter(Mandatory=$false, ParameterSetName="B")]
        [string]$BParameter2
    )
  
    If ($A) {
        Write-Output "Using Parameter Set A"
        Write-Output $DefaultParameter1
        Write-Output $DefaultParameter2
        Write-Output $AParameter1
        Write-Output $AParameter2
    }

    If ($B) {
        Write-Output "Using Parameter Set B"
        Write-Output $DefaultParameter1
        Write-Output $DefaultParameter2
        Write-Output $BParameter1
        Write-Output $BParameter2
    }
  }

# Function Tests #
Test-ParameterSets -DefaultParameter1 'defaultValue1' -DefaultParameter2 'defaultValue2' -A -AParameter1 'valueA1' -AParameter2 'valueA2'
Test-ParameterSets -DefaultParameter1 'defaultValue1' -DefaultParameter2 'defaultValue2' -B -BParameter1 'valueB1' -BParameter2 'valueB2'
```

The first step is to add a `DefaultParameterSetName`. We can set that in our `[CmdletBinding]()` as follow:

```txt
// code/demo-function.ps1#L2-L2

[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName="Default")]
```

By declaring a default parameter set name on our `CmdletBinding` will set all of our parameters defined under the `default` set. What we will do next is define which parameters needs to be presented if the parameter switch `$A` is used. We do not want to present parameters from switch `$B` in this case. We will do this by defining a new parameter set name and grouping the parameters we want to be part of that particular set.

```txt
// code/demo-function.ps1#L8-L13

[Parameter(Mandatory=$false, ParameterSetName="A")]
[Switch]$A,
[Parameter(Mandatory=$false, ParameterSetName="A")]
[string]$AParameter1,
[Parameter(Mandatory=$false, ParameterSetName="A")]
[string]$AParameter2,
```

We will also give parameter switch `$B` and it's corresponding parameters, it's own parameter set name.

```txt
// code/demo-function.ps1#L14-L19

[Parameter(Mandatory=$false, ParameterSetName="B")]
[Switch]$B,
[Parameter(Mandatory=$false, ParameterSetName="B")]
[string]$BParameter1,
[Parameter(Mandatory=$false, ParameterSetName="B")]
[string]$BParameter2
```

Now that we have defined our parameter sets and grouped the relevant parameters according to their sets our function/Cmdlet will now only present corresponding parameters based on which switch is used when calling the function/Cmdlet.

![testFunctionAnimation](./assets/TestFunctionAnimation.gif)

You can also find some very helpful documentation on parameter sets on [Microsoft Docs](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parameter_sets?view=powershell-7.1).
