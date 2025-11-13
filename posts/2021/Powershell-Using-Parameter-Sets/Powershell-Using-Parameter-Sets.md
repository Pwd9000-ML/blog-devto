---
title: PowerShell - Using Parameter Sets
published: true
description: Powershell - How to use parameter sets in PowerShell functions
tags: 'powershell, posh, tutorial, scripting'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Powershell-Using-Parameter-Sets/assets/PowerShellHowTo.png'
canonical_url: null
id: 685386
date: '2021-05-02T12:29:00Z'
---

## :bulb: What are parameter sets in PowerShell and how to use them

Have you ever wondered when you are writing a PowerShell function or commandlet how you can make only certain parameters be presented to the consumer of the function in certain scenarios? That's where parameter sets come in. :smile:

We will look at the following test function: `[Test-ParameterSets]` on exactly how this functionality can be used.

{% gist <https://gist.github.com/Pwd9000-ML/2e8e4c69299eca1f06547106b4686b17.js> %}

The first step is to add a `DefaultParameterSetName="Default"`. We can set that in our `[CmdletBinding()]` as follow:

```txt
// code/demo-function.ps1#L2-L2

[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName="Default")]
```

By declaring a default parameter set name on our `[CmdletBinding()]` will set all of our parameters defined under the `Default` set. What we will do next is define which parameters needs to be presented if the parameter switch `$A` is used. We do not want to present parameters from switch `$B` in this case. We will do this by defining a new parameter set name and grouping the parameters we want to be part of that particular set.

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

![testFunctionAnimation](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Powershell-Using-Parameter-Sets/assets/TestFunctionAnimation.gif)

You can also find some very helpful documentation on parameter sets on [Microsoft Docs](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parameter_sets?view=powershell-7.1/?wt.mc_id=DT-MVP-5004771).

I hope you have enjoyed this post and have learned something new. You can also find the code samples used in this blog post on my [GitHub](https://github.com/Pwd9000-ML/blog-devto/tree/main/posts/2021/Powershell-Using-Parameter-Sets/code) page. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
