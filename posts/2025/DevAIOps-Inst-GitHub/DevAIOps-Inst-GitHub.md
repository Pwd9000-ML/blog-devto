---
title: Instructions and Prompt Files to supercharge VS Code with GitHub Copilot
published: true
description: Unlock the power of GitHub Copilot in VS Code with Custom Instructions and Prompt Files.
tags: 'GitHubCopilot, MCP, tutorial, AI'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevAIOps-Inst-GitHub/assets/main.png'
canonical_url: null
id: 2620657
series: GitHubCopilot
date: '2025-06-24T13:07:57Z'
---

## Supercharge Your GitHub Copilot: How DevOps Engineers are Mastering Customisation

Hey everyone! If you're a developer or, like me, a **DevOps engineer**, you've probably already experienced the magic that is **GitHub Copilot**. It's a game-changer, right? From suggesting boilerplate code to squashing annoying bugs, it feels like having an extra pair of hands (or rather, an extra brain) in your IDE.

But here's the thing: out of the box, Copilot is fantastic, but it's also generic. It learns from billions of lines of public code, which is awesome, but it doesn't know _your_ team's specific coding standards, your obscure internal libraries, or that quirky cloud configuration you spent weeks perfecting. And for us in DevOps, **consistency, best practices, and domain-specific knowledge** aren't just nice-to-haves, they're the bedrock of stable, scalable systems.

This is where the real power of Copilot unfolds: **Customisation**. We're moving beyond basic code completion to actively shaping Copilot to become an even more powerful, domain-aware extension of our DevOps team.

We will look at two distinct ways of customising Copilot: **Custom Instructions** and **Prompt Files**. These features allow you to define how Copilot behaves, what it prioritises, and how it interacts with your codebase. This is not just about making Copilot "smarter", it's about making it _smarter for you_.

## Why DevOps Needs an Opinionated AI Assistant

Before we take a look at how to set this up in VSCode let's talk about why we want to do this. In DevOps, we thrive on **standardisation, automation, and shared knowledge**. A generic AI assistant, while helpful, can sometimes introduce friction or suggest patterns that don't align with our meticulously crafted workflows. Things to keep in mind to make successful use of Copilot in DevOps:

- **Consistency is King (and Queen!):** Whether it's Terraform modules, Kubernetes manifests, or CI/CD pipeline definitions, consistency prevents "snowflake" environments to conform to a standard, and simplifies troubleshooting. Your custom Copilot can enforce these standards.
- **Domain-Specific Knowledge Injection:** Copilot doesn't inherently know your internal `shared-components` library, your specific Azure Resource Group naming conventions, or the unique security policies your organisation adheres to. You can teach it!
- **Accelerated Onboarding & Knowledge Transfer:** Imagine new team members having an AI assistant pre-configured with your team's best practices, preferred tech stack, and even common commands. It's like having an always-on mentor.
- **Beyond Code Generation:** While amazing for code, Copilot can also assist with writing documentation, drafting runbooks, generating tests for your infrastructure code, and even helping define complex CI/CD stages.
- **Reduced "AI Hallucinations":** The more context and specific instructions you provide, the less likely Copilot is to go off-script and "hallucinate" irrelevant or incorrect suggestions.

So let's dive right in and see how we can customise GitHub Copilot to become your DevOps super assistant using **Custom Instructions** and **Prompt Files**.

## Architecting Your AI Assistant for DevOps Excellence

So, how do we turn Copilot from a generalist into a highly specialised DevOps guru? Visual Studio Code offers powerful features to make this happen. Let's break down the key ways you can customise Copilot's behaviour.

Before we dive into the specifics, it's important to understand the difference between **Custom Instructions** and **Prompt Files**:

**1. Custom Instructions:** Establish overarching principles and standards for various activities such as guardrails around how code should be generated, how code reviews should be done, or commit message creation. These instructions define the operational framework and methodology that guides the AI's behaviour (**how** a task should be executed).

Think of **Custom Instructions** as the fundamental operating principles or guidelines you embed directly into Copilot's "brain." These are rules that it will attempt to follow _every single time_ you interact with it in chat. For DevOps, this is pure gold!

```markdown
---
applyTo: '**'
---

# Project general coding standards

Apply the [general coding guidelines](./general-coding.instructions.md) to all code.

## General Instructions for this Workspace:

- Always prioritise security best practices.
- Favour idempotent solutions.
- Use British English spelling.

## Naming Conventions

- Use terraform formatting for all Terraform files (like terraform fmt)
- Whenever `resource` or `data` blocks are generated, ensure they follow the naming convention of the provider e.g `resource "azurerm_storage_account" "meaningful_context_name"` or `data "azurerm_storage_account" "meaningful_context_name"`.
- Whenever `output` blocks are generated, ensure they follow the naming convention of the provider e.g `output "meaningful_context_name"`.
- Ensure that naming of resources complies to the [Azure Resource Naming Rules](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming). e.g., resource groups should be named `rg-<project>-<environment>-<region>-<type>-<3digitnumber>` (e.g., `rg-myapp-dev-uks-web-001`).
- Always use lowercase for resource names, and separate words with hyphens (e.g., `my-app-service`). use terraform functions like `lower()` when input is not guaranteed to be lowercase.

## Terraform Best Practices:

- When generating Terraform for Azure, always use the `azurerm` provider version `~>3.0`.
- Ensure all Terraform modules include a `variables.tf`, `outputs.tf`, and a `README.md`.
- **Private Networking First!** Wherever possible, prioritise the use of private endpoints for Azure PaaS services (e.g., Storage Accounts, Azure SQL Database, Key Vault, Container Registry) to ensure traffic stays within the virtual network.
- When suggesting virtual networks, always include at least one subnet dedicated for private endpoints and ensure `enforce_private_link_endpoint_network_policies = true` on any such subnets.
- Never hardcode secrets or sensitive values. Always reference them from Azure Key Vault, GitHub Secrets or Azure DevOps Secure Files.
- Prefer using `for_each` over `count` for deploying multiple similar resources over duplicating resource blocks.
- Avoid excessive use of `data` blocks and prefer using `locals` for static values by computed values based on the provider.
- Add comments to explain complex resources or unusual patterns.
```

**How to set up Custom Instructions in VSCode:**

**Workspace:** You can store custom instructions in your workspace or repository in a `.github/copilot-instructions.md` file and describe your coding practices, preferred technologies, and project requirements by using Markdown. These instructions only apply to the workspace where the file is located. (Set the `github.copilot.chat.codeGeneration.useInstructionFiles` setting in VSCode to `true`)

You can also set up multiple instruction files using `.instructions.md` or even within VS Code's settings stored in the workspace or your user profile. Check out how to here: [Types of custom instructions](https://code.visualstudio.com/docs/copilot/copilot-customization#_types-of-custom_instructions)

💡 **My Take:** This is like setting up a global standard for Copilot's behaviour. It ensures baseline consistency across all your AI-assisted tasks and, crucially, enforces those critical security and architectural patterns like private networking, security and naming from the get-go!

**2 Prompt Files:** Create targeted, reusable prompts for specific activities like code generation or conducting code reviews. These are self-contained prompts that can be executed directly within the chat interface. They specify the particular task to be accomplished (**what** needs to be done). You may optionally incorporate task-specific guidance on execution methodology, or reference your established custom instructions within the prompt file.

These are essentially pre-defined, reusable prompts that you can trigger directly in the Copilot chat. They're perfect for standardising common DevOps workflows e.g:

### Prompt for generating a new Terraform module structure

```markdown
---
mode: 'agent'
tools: ['githubRepo', 'codebase']
description: 'Generate a new Terraform module structure for an Azure resource.    '
---

Your goal is to generate a new Terraform module structure for an Azure resource based on the templates in #githubRepo contoso/terraform-templates.

Ask for the module name and any specific requirements if not provided.

Requirements for the module:

You are a highly opinionated DevOps expert. Generate a basic Terraform module structure for a new Azure resource. Include `main.tf`, `variables.tf`, `outputs.tf`, and a `README.md` following the provided best practices. Ask me for the module's purpose and primary resource type (e.g., 'Azure App Service', 'Azure SQL Database').

Specifically, ensure:

- Use design patterns are followed: [design-system/patterns.md](../docs/design-system/patterns.md)
- The `main.tf` has a placeholder for `resource` blocks.
- `variables.tf` has at least `location` and `resource_group_name` variables with meaningful descriptions.
- `outputs.tf` has a placeholder for key resource IDs/names.
- `README.md` includes sections for "Usage", "Inputs", "Outputs", and "Examples".
```

### Prompt for checking Terraform code for security best practices

```markdown
---
mode: 'edit'
description: 'Perform a Terraform security and code quality review on the provided code.'
tools: ['tflint', 'tfsec', 'codebase']
---

Perform a Terraform security and code quality review:

- Check the provided Terraform code for security best practices.
- Ensure it adheres to the team's custom instructions.
- Use tools like `tflint` and `tfsec` to identify potential issues.
- Provide a summary of findings and suggestions for improvement.
- If you find any issues, suggest specific changes to the code.
- Validate all user inputs and sanitize data.
```

### Prompt for Consistent README Update

```markdown
---
mode: 'agent'
tools: ['markdownlint', 'codebase']
description: 'Update the documentation README.md file with new changes.'
---

You are a documentation specialist.

Requirements for the README update:

- Use the existing README structure as a guide.
- Ensure the new section is consistent with the current style and formatting.
- Update the README.md file with the new changes.
- Use markdownlint to ensure the updated README.md file is properly formatted.
```

**How to set up Prompt Files in VSCode:**

VS Code supports two types of scopes for prompt files:

**Workspace prompt files:** Are only available within the workspace and are stored in the `.github/prompts` folder of the workspace. **User prompt files:** Are available across multiple workspaces and are stored in [VSCode Profiles](https://code.visualstudio.com/docs/configure/profiles).

By default, prompt files are located in the `.github/prompts` directory of your workspace. You can specify additional prompt file locations with the `chat.promptFilesLocations` setting.

To use and initiate a specific prompt file, you can use the Copilot chat interface in VSCode. Just type `/prompt` followed by the name of the prompt file (e.g., `/generate-terraform-module`) to execute it.

Check out more ways to set up and use prompt files in VSCode here: [Types of prompt files](https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-file-examples)

💡 **My Take:** These are your personal, AI-powered snippets and templates. They save you typing, ensure consistency, and allow you to quickly invoke complex multi-part instructions. This is especially powerful when onboarding new team members – just point them to your prompt files!

## What is the goal of 'Custom Instructions' and 'Prompt Files'

Let's take a look at the practical goals of using Custom Instructions and Prompt Files in your DevOps workflow:

**DevOps Use Case Examples:**

**"Terraform Security Review Mode":** Imagine a mode that, when activated, instructs Copilot to specifically review your Terraform files for common security misconfigurations (e.g., open security groups, public storage accounts). It could suggest fixes or point to relevant Azure Security Centre recommendations.

**"Azure DevOps Pipeline Hardening Mode":** A mode that guides Copilot to analyse your YAML pipelines for security weaknesses, such as:

- Hardcoded secrets (it would suggest using Key Vault).
- Overly broad service connection permissions.
- Lack of mandatory approvals for sensitive stages.
- Absence of image scanning for container builds.

**"Network Topology Advisor Mode":** This mode could be amazing! You'd provide it with an existing VNet and subnet configuration, and Copilot could suggest the best way to integrate a new service using private endpoints, considering DNS zones and routing, based on your custom instructions for private networking.

💡 **My Take:** Think of these as giving Copilot a specific "hat" to wear for a particular job. It's about optimising its behaviour for a highly focused task, making it an even more powerful assistant for specialised DevOps work, deeply ingrained with your team's operational and security policies.

## Tips and Tricks for Effective Customisation

### Providing Context

No matter how many custom instructions you have, Copilot needs context to provide relevant suggestions. Always remember to give Copilot as much information as possible:

- **Current File:** The file you're actively working on.
- **Open Tabs:** Other relevant files open in your IDE (e.g., your `variables.tf` alongside your `main.tf`).
- **Selected Code:** Highlight specific code blocks to focus Copilot's attention.
- **Chat History:** Your ongoing conversation provides immediate context.
- **Copilot Spaces (for enterprise):** For larger organisations, Copilot Spaces can provide even broader context across repositories and internal documentation, massively boosting relevance.

### Practical Strategies for DevOps Teams

- **Start Small, Iterate Often:** Don't try to define every single rule at once. Pick a pain point (e.g., inconsistent naming conventions, repetitive pipeline tasks, or ensuring private endpoints) and start there. Build momentum with small wins.
- **Document Your AI Guidelines:** Just like your coding standards, document your team's Copilot custom instructions and commonly used prompt files. Version control these! This is crucial for team alignment and auditability. Treat your AI configuration as code!
- **Share and Collaborate:** Encourage team members to contribute to and refine your collective AI assistant. The more brains feeding it, the smarter it gets. Regularly review and update your custom instructions as your tech stack or best practices evolve.
- **Measure the Impact:** How has customisation improved code quality? Reduced review cycles? Sped up common infrastructure tasks? Are you seeing more consistent private networking implementations? Keep an eye on the tangible benefits.
- **Identify Your "AI Champion":** Who on your team will take the lead in exploring, documenting, and evangelising Copilot customisation? Having a dedicated champion can make a huge difference in driving adoption and refinement.

## Conclusion

Customising GitHub Copilot isn't just about tweaking settings, it's about evolving our relationship with AI. We're moving from simply using an AI to actively shaping it to fit our unique engineering culture and operational needs. This paves the way for even more sophisticated AI-driven DevOps: imagine AI-assisted incident response, proactive anomaly detection, or even self-healing systems that leverage your custom AI guidelines.

The future of DevOps is collaborative, and AI is becoming an increasingly integral part of that collaboration. By mastering Copilot customisation, you're not just enhancing your personal productivity, you're contributing to a smarter, more consistent, and more efficient future for your entire team.

So, what are you waiting for? Start customising your GitHub Copilot today and unlock its true potential!

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

Date: 21-04-2025
