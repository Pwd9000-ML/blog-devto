---
title: Azure Verified Modules using Terraform
published: false
description: DevOps - Terraform - Azure Verified Modules - Learn how to use Azure Verified Modules in Terraform to deploy resources in Azure.
tags: 'terraform, azure, iac, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Terraform-AVM/assets/main.png'
canonical_url: null
id: 1824654
---

## Overview

---

Microsoft Azure Verified Modules (AVM) are a curated set of infrastructure-as-code (IaC) modules that are compliant with the Azure Well-Architected Framework and is actively maintained, tested and verified by Microsoft. These modules are designed to help you build secure, scalable, and resilient cloud environments on Azure. The usage of Azure Verified Modules (AVM) in a Terraform configuration where configuration options are uniform and consistent across multiple modules, in terms of best practices and security. Implantation of uniform and consistent configuration options across multiple modules is a key feature of Azure Verified Modules (AVM). This is achieved by having the same configuration options across all modules in the same pattern and features, which makes it easier to use and understand the modules and attain a consistent configuration across all modules. With Infrastructure as Code (IAC) there are a few challenges. One of the biggest is the effort required to write and maintain modules, especially in a fast-paced environment like Azure where innovation is constant. Many Microsoft partners, developers and community supporter develop their own modules, but the level of maintenance and support can vary widely. Relying on community-shared modules can be risky due to uncertainty about their upkeep. That’s where Microsoft saw the opportunity to invest time, people, and resources to address this challenge, Microsoft introduced Azure Verified Modules (AVM). AVM provides modules that are: • Supported by Microsoft FTEs directly. • Modules undergo thorough testing to ensure functionality. • Modules follow consistent design patterns and features which improve usability and maintainability. AVM is a Microsoft project to unify and regulate Infrastructure-as-Code modules, using both internal and external communities. These modules act as modular components for deploying Azure resources and extensions in a uniform way. Azure verified module’s – consistency in features AVM modules have consistent configuration features. It is necessary to understand these features regardless of if you use or write AVM modules. Resource modules support below optional features/extension resources, as specified, if it is supported by the primary resource. The top-level variable/parameter are also named the same. So, we have the same names in every module. AVM interfaces acts as a shim over the existing API, ensuring consistent naming conventions. This consistency extends from the AVM modules to the underlying API, facilitating seamless integration and usage. This is a great benefit. AVM is worrying about providing the right data passed in the underlying api. Examples of Consistent features to name a few: • Diagnostic Settings • Role Assignments • Resource Locks • Tags • Managed Identities • Private Endpoints • Customer Managed Keys • Azure Monitor Alerts Take a look at my talk and session recording look at this in action:

here: [Global Azure 2024 - Azure Verified Modules](https://www.youtube.com/live/5dtRWBfj4xY?si=wZkmdcckCw4f2S2X&t=4222)

Also check out these amazing labs Lab Environment (https://learn.microsoft.com/en-us/samples/azure-samples/avm-bicep-labs/avm-bicep-labs?wt.mc_id=DT-MVP-5004771) With the labs you can try it self. (https://learn.microsoft.com/en-us/samples/azure-samples/avm-terraform-labs/avm-terraform-labs?wt.mc_id=DT-MVP-5004771)

extra https://azure.github.io/Azure-Verified-Modules/specs/shared/#id-rmfr4---category-composition---avm-consistent-feature--extension-resources-value-add

## Conclusion

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
