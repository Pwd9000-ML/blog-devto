---
title: Build 2024 - Book Of News - DevOps Edition
published: true
description: Build 2024 - Book Of News - DevOps Edition
tags: 'ai, build2024, copilot, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2024/DevOps-Build-2024-Book-Of-News/assets/main1.png'
canonical_url: null
id: 1860712
date: '2024-05-21T16:54:03Z'
---

## Overview

In this DevOps Edition of the Build 2024 we will look at a few updates and announcements made at this years **[Build 2024](https://build.microsoft.com/en-US/home?wt.mc_id=DT-MVP-5004771)** containing a collection of the latest news and updates from the **DevOps** world. This edition covers a wide range of topics, including AI, Copilot, and more. Read on to learn about the latest trends and developments in the **Developer Tools** and **DevOps** space.

## Microsoft Learn Challenge

Before we start looking at some of the latest and greatest updates and announcements for the Dev Community, there is also a new Microsoft Learn Challenge 😁  
Why don't you immerse yourself in cutting-edge AI technology and earn a badge by completing one of these unique, AI-focused collections. Be quick, the challenge ends on June 21, 2024.

**[Microsoft Learn Challenge: Build Edition](https://www.microsoft.com/en-us/cloudskillschallenge/build/registration/2024?ocid=build24_csc_DT-MVP-5004771)**

## The Latest in Developer Tools and DevOps from Microsoft and Azure

### 1. .NET updates for developer community

The .NET framework, Microsoft's cornerstone for building modern applications, has received significant updates, which include the introduction of .NET Aspire and the preview of .NET 9. .NET Aspire, a new cloud-native stack, simplifies building cloud-native apps by abstracting the complexities of setup, configuration, and diagnostics. It aims to boost developer productivity by allowing them to focus on the logic that matters, using familiar tools within a less complex environment. Additionally, the .NET 9 Preview 4 brings enhancements aimed at optimising cloud-native app development and enhancing support for building generative AI apps.  

Check out the **[General Availability of .NET Aspire](https://devblogs.microsoft.com/dotnet/dotnet-aspire-general-availability?wt.mc_id=DT-MVP-5004771)** for more information.  

### 2. Empowering AI Development with Visual Studio Code

The AI Toolkit for Visual Studio Code, now in preview, integrates AI development tools and models to streamline the development and deployment of intelligent apps. This toolkit enables AI engineers to efficiently deploy their models to Microsoft Azure AI Studio, among other platforms, using container images. This addition underscores Microsoft's commitment to facilitating next-generation AI development, making it more accessible and efficient for developers.  

Check out the **[Visual Studio Code AI Toolkit](https://techcommunity.microsoft.com/t5/microsoft-developer-community/announcing-the-ai-toolkit-for-visual-studio-code/ba-p/4146473?wt.mc_id=DT-MVP-5004771)** for more information.  

### 3. Unleashing API and Generative AI Capabilities with Azure API Management

Azure API Management now includes new capabilities that significantly enhance the scalability and security of generative AI deployments. Features such as the Microsoft Azure OpenAI Service token limit policy, one-click import of Azure OpenAI Service endpoints, and a dedicated Load Balancer for efficient traffic distribution, position Azure as a leader in managing the rapid proliferation of APIs and AI solutions. These updates aim to streamline API sprawl and improve resource allocation and service protection.  

Check out the **[Azure API Center](https://techcommunity.microsoft.com/t5/azure-integration-services-blog/azure-api-center-your-comprehensive-api-inventory-and-governance/ba-p/4125146?wt.mc_id=DT-MVP-5004771)** for more information.  

## 4. Boosting Web App Performance and Security with Azure App Service

Microsoft Azure App Service, a cloud platform for quickly building, deploying, and running web apps and APIs, has been enhanced to offer better performance and security. These improvements allow developers to focus on innovation without worrying about the underlying infrastructure. The integration of WebJobs with Azure App Service is particularly noteworthy, as it enables cost savings and consistent performance by sharing compute resources.

### 5. Introducing Dynamic Sessions in Azure Container Apps

For AI app developers, the introduction of dynamic sessions in Microsoft Azure Container Apps is a game-changer. This feature allows for the on-demand, secure sandboxing of AI-generated code or the extension/customisation of SaaS apps. Dynamic sessions are designed to mitigate security risks, leverage serverless scaling, and reduce development and management overheads, highlighting Microsoft's focus on security and efficiency.

### 6. Expanding Flexibility with Azure Functions

Azure Functions is launching new features that offer more flexibility and extensibility to users. The introduction of an extension for the Microsoft Azure OpenAI Service and the availability of Visual Studio Code for the Web as a browser-based developer experience are notable highlights. These updates are aimed at enabling developers to easily infuse AI into their apps and get started with Azure Functions more conveniently, further emphasising Microsoft's investment in serverless architectures and AI-driven applications.

### 7. AKS Automatic: Simplifying Kubernetes Adoption

Azure Kubernetes Service (AKS) is introducing a new feature called Automatic, which is currently in preview. This feature is designed to simplify the adoption of Kubernetes for developers, DevOps teams, and platform engineers. Automatic will automate the setup and management of AKS clusters, incorporating best practice configurations to ensure security, performance, and dependability for applications.

By providing access to the Kubernetes APIs, Automatic retains the flexibility of Kubernetes, which is crucial for many customers. Additionally, Automatic introduces several new features aimed at improving security and ease of operation, including the deployment safeguards enforcement option, which applies policy best practices to AKS clusters and can automatically adjust resource settings to align with these best practices. These enhancements are part of Microsoft's efforts to make Kubernetes adoption easier and more efficient for users.

### 8. Enhancing Messaging with Azure Service Bus

The Azure Service Bus is enhancing its messaging system with several updates now in preview, focusing on robustness, efficiency, and resilience. Key features include Geo-disaster recovery for regional resilience, Durable terminus for maintaining message state across network disruptions, Batch delete for efficient message management, and Peek by state for selective message viewing. These improvements are designed to support uninterrupted and secure communication for enterprise operations.

### 9. Azure Static Web Apps: Introducing a Dedicated Pricing Plan

Azure Static Web Apps is introducing a dedicated pricing plan, now in preview, designed to support enterprise-grade features for enhanced networking and data storage. This new plan utilises dedicated compute capacity, providing network isolation to enhance security, and enhanced quotas for more custom domains within an app service plan. Furthermore, it includes "always-on" functionality for Azure Static Web Apps managed functions, offering built-in API endpoints to connect to backend services. These features aim to deliver more advanced capabilities to customers, ensuring their web apps are both scalable and secure.

### 10. Microsoft Dev Box: New Features for Developer Productivity and Enterprise Management

Microsoft Dev Box has been updated with new features aimed at improving developer productivity and offering enhanced enterprise management capabilities. These updates include team customisations and images, now in private preview, and project-based catalogs, in preview, enabling developer leads and platform engineers to create customised development environments for their teams.

An improved connection experience is available in the Windows App, in preview, offering quick access to Dev Box in the taskbar and seamless transition between Dev Box and Windows devices. For enterprise management, Dev Box connection telemetry is now generally available through Azure Monitor, providing insights into performance and system events.

Additionally, a hibernation feature on disconnect helps optimise costs by letting dev boxes hibernate when there is no active remote desktop protocol session. The updates also introduce the ability for developer tool vendors to create and publish Dev Box-compatible custom images via the "Windows client for developers" image in the Azure Marketplace, and new deployment regions have been added to improve connectivity performance and latency.

### 11. Azure Deployment Environments: Extending Support for Pulumi

Microsoft Azure Deployment Environments are enhancing their extensibility model to include support for Pulumi, alongside existing support for Arm, Bicep, and Terraform. This update allows customers to perform deployments using Pulumi, a popular Infrastructure as Code (IaC) framework, enabling more flexible and efficient infrastructure management.

Customers can either build their own container image following published guidance or directly utilise a sample container image published for Pulumi. Additionally, a quick-start template is available for platform engineers to deploy and configure Azure Deployment Environments with a single-click deployment, streamlining the setup process and promoting a more seamless experience for leveraging IaC frameworks within Azure.

### 12. GitHub Copilot Extensions: Enhancing Developer Experience with Azure

My Personal favourite announcements is GitHub is launching the first set of GitHub Copilot extensions in private preview, developed by Microsoft and third-party partners. These extensions allow developers and organisations to tailor their GitHub Copilot experience with their preferred services, such as Azure, Docker, Sentry, and more, directly within GitHub Copilot Chat.

Specifically, the GitHub Copilot for Azure extension enables developers to build, troubleshoot, and deploy applications on Azure more efficiently. This showcases the potential of building in natural language and demonstrates how a broader range of capabilities can significantly accelerate development velocity.

### 13. Azure Event Grid: New Capabilities for IoT and Event Integration

The Azure Event Grid has introduced new capabilities tailored to enhance support for Internet of Things (IoT) solutions and the integration of various event sources. These updates bolster the platform's MQTT broker capabilities, streamline the transition to Event Grid namespaces for both push and pull delivery of messages, and facilitate the integration of new sources like Microsoft Entra ID and Microsoft Outlook through the support of the Microsoft Graph API.

By leveraging these enhancements, customers can now utilise Event Grid namespace capabilities, such as the MQTT broker, without the need to reconstruct existing workflows, and harness Event Grid for new use cases like processing information when a new employee is hired or a new email is received, thereby enabling further action in other applications.

### 14. Azure Load Testing: New Enhancements and Integrations

Azure Load Testing is receiving new enhancements and integrations designed to simplify the process of running high-scale load tests, providing deeper insights into test results and optimising application performance. These updates include the ability to simulate load from multiple regions simultaneously in a single test run, support for Locust, a Python-based open-source load testing framework, and integrations with Azure App Service and Azure Functions. These features aim to offer a more comprehensive testing environment that mimics real-world traffic, fosters better collaboration, and allows for cost versus performance optimisation.

### 15. Azure Spring Batch Support for Azure Spring Apps Enterprise

Spring Batch support for Azure Spring Apps Enterprise, now in preview, enables users to run Spring Batch apps cost-efficiently in the cloud. Spring Batch is a comprehensive framework for handling large-scale data processing, providing features like logging, tracing, transaction management, and job processing statistics.

This integration offers several benefits, including cost-effective cloud execution where customers pay only for compute resources during the actual execution period, and a fully managed Service Registry for service discovery among apps. This preview aims to simplify the development process by minimising code modifications and leveraging ready-to-use components, making it easier for customers to focus on business logic.

### 16. Azure Logic Apps: Enhanced Developer Experience and Functionality

Updates to Azure Logic Apps aim to enhance the developer experience and expand functionality for automated workflows with minimal coding. Key updates include an improved onboarding experience in Microsoft Visual Studio Code, simplifying extension installation and enhancing the project start and debugging process.

Additionally, deployment scripting tools have been introduced in Visual Studio Code to aid in setting up continuous integration/continuous delivery (CI/CD) processes for Logic Apps Standard. Support for Zero Downtime deployment scenarios has been added, along with expanded functionality such as .NET Custom Code Support and connectors for IBM mainframe and midranges. These updates also include enhancements to Azure Integration accounts and a monitoring dashboard for Logic Apps, all designed to streamline project management and development processes.

### 17. GitHub Copilot Integration with Microsoft Visual Studio

Microsoft Visual Studio 17.10 has introduced a significant update by integrating GitHub Copilot directly into the integrated development environment (IDE). This integration marks a notable leap in coding productivity, transforming the way developers code, debug, and manage projects. By providing smarter, context-aware coding assistance and intuitive interfaces, the GitHub Copilot integration enhances the development workflow, making it more efficient and streamlined for developers working on various projects.

### 18. Microsoft Visual Studio Code for Education

Microsoft Visual Studio Code for Education, now generally available, is a free, online computer science education platform providing an integrated curriculum and sandbox coding environment. It requires no setup or installation, making it accessible to anyone interested in learning to code. This platform emphasises future-ready skills by offering courses such as Introduction to Python, aligning with the high demand for Python skills in the workplace.

Visual Studio Code for Education is designed to be inclusive and accessible across multiple devices, platforms, and browsers, simplifying the learning process with a streamlined code editing experience optimised for education. Its one-click-to-code functionality allows students to start coding immediately, making coding more accessible and learning code a realistic goal for all learners.

## Conclusion

These updates and new features from Microsoft and Azure represent significant strides in supporting the developer and DevOps communities. By simplifying cloud-native development, enhancing AI integration, securing and streamlining API management, and providing flexible, efficient tools for app development and deployment, Microsoft continues to empower developers to innovate and build the future of technology. Stay tuned for more updates and continue exploring these tools to unleash your full potential as a developer or DevOps professional.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
