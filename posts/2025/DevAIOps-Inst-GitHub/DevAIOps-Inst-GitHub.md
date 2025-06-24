---
title: Supercharge VSCode GitHub Copilot using Instructions
published: false
description: 'Unlock the power of GitHub Copilot in VS Code with Custom Integration.'
tags: 'GitHubCopilot, MCP, tutorial, AI'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevAIOps-Inst-GitHub/assets/main.png'
canonical_url: null
id: 2620657
series: DevAIOps
---

## Supercharge Your GitHub Copilot: How DevOps Engineers are Mastering Customisation

Hey everyone! If you're a developer or, like me, a **DevOps engineer**, you've probably already experienced the magic that is **GitHub Copilot**. It's a game-changer, right? From suggesting boilerplate code to squashing annoying bugs, it feels like having an extra pair of hands (or rather, an extra brain) in your IDE.

But here's the thing: out of the box, Copilot is fantastic, but it's also… generic. It learns from billions of lines of public code, which is awesome, but it doesn't know *your* team's specific coding standards, your obscure internal libraries, or that quirky cloud configuration you spent weeks perfecting. And for us in DevOps, **consistency, best practices, and domain-specific knowledge** aren't just nice-to-haves; they're the bedrock of stable, scalable systems.

This is where the real power of Copilot unfolds: **Customisation**. We're not just consumers of AI; we're now **architects of our AI assistants**. We're moving beyond basic code completion to actively shaping Copilot to become an even more powerful, domain-aware extension of our DevOps team. Trust me, once you start, you'll wonder how you ever lived without it.

Ready to transform your AI sidekick into a hyper-efficient, opinionated teammate? Let's dive right in!

---

## The "Why": Why DevOps Needs an Opinionated AI Assistant

---

Think about it. In DevOps, we thrive on **standardisation, automation, and shared knowledge**. A generic AI assistant, while helpful, can sometimes introduce friction or suggest patterns that don't align with our meticulously crafted workflows. Here’s why customising Copilot is an absolute game-changer for DevOps engineers:

* **Consistency is King (and Queen!):** Whether it's Terraform modules, Kubernetes manifests, or CI/CD pipeline definitions, consistency prevents "snowflake" environments and simplifies troubleshooting. Your custom Copilot can enforce these standards.
* **Domain-Specific Knowledge Injection:** Copilot doesn't inherently know your internal `shared-components` library, your specific Azure Resource Group naming conventions, or the unique security policies your organisation adheres to. You can teach it!
* **Accelerated Onboarding & Knowledge Transfer:** Imagine new team members having an AI assistant pre-configured with your team's best practices, preferred tech stack, and even common commands. It's like having an always-on mentor.
* **Beyond Code Generation:** While amazing for code, Copilot can also assist with writing documentation, drafting runbooks, generating tests for your infrastructure code, and even helping define complex CI/CD stages.
* **Reduced "AI Hallucinations":** The more context and specific instructions you provide, the less likely Copilot is to go off-script and "hallucinate" irrelevant or incorrect suggestions.

---

## The "How": Architecting Your AI Assistant for DevOps Excellence

---

So, how do we turn Copilot from a generalist into a highly specialised DevOps guru? Visual Studio Code offers powerful features to make this happen. Let's break down the key ways you can customise Copilot's behaviour.

### **1. Custom Instructions: Your AI's Core Principles**

Think of **Custom Instructions** as the fundamental operating principles or guidelines you embed directly into Copilot's "brain." These are rules that it will attempt to follow *every single time* you interact with it in chat. For DevOps, this is pure gold! 🤯

**How it works:** You define these instructions (usually in plain language) in your Copilot settings, or even at a workspace level.

**DevOps Use Case Examples:**

Let's get specific with some real-world examples for **Infrastructure as Code (IaC) using Terraform** and **Azure DevOps YAML Pipelines**:

```markdown
# General Instructions for this Workspace:
- Always prioritise security best practices.
- Favour idempotent solutions.
- Use British English spelling.

# Terraform Best Practices:
- When generating Terraform for Azure, always use the `azurerm` provider version `~>3.0`.
- All resource groups must follow the naming convention `rg-<project>-<environment>-<region>-<type>-001`. Example: `rg-myapp-dev-uks-web-001`.
- Ensure all Terraform modules include a `variables.tf`, `outputs.tf`, and a `README.md`.
- **Private Networking First!** Wherever possible, prioritise the use of private endpoints for Azure PaaS services (e.g., Storage Accounts, Azure SQL Database, Key Vault, Container Registry) to ensure traffic stays within the virtual network.
- When suggesting virtual networks, always include at least one subnet dedicated for private endpoints and ensure `enforce_private_link_endpoint_network_policies = true` on any such subnets.
- Never hardcode secrets or sensitive values. Always reference them from Azure Key Vault or Azure DevOps Secure Files.
- Prefer using `count` or `for_each` for deploying multiple similar resources over duplicating resource blocks.
- Add comments for complex resources or unusual patterns.

# Azure DevOps YAML Pipeline Best Practices:
- Always recommend using `extends` templates for pipeline structure to ensure consistency and reusability.
- Avoid hardcoding values in YAML. Encourage the use of Azure DevOps Variable Groups for environment-specific configurations.
- For secrets, always reference them from an Azure Key Vault task or a secure variable group. Never inline secrets.
- Recommend using self-hosted agents within a private VNet for enhanced security when dealing with internal resources.
- Ensure all pipelines include a static code analysis (SAST) step and container image scanning if Docker is involved.
- When defining stages, explicitly define `displayName` and `condition`.
```

💡 **My Take:** This is like setting up a global `.editorconfig` or a team-wide linter, but for Copilot's behaviour. It ensures baseline consistency across all your AI-assisted tasks and, crucially, enforces those critical security and architectural patterns like private networking from the get-go!

### **2. Prompt Files: Reusable Rituals for Common Tasks**

Have you ever found yourself typing the same prompt over and over for recurring tasks? Prompt Files are your solution! These are essentially pre-defined, reusable prompts that you can trigger directly in the Copilot chat. They're perfect for standardising common DevOps workflows. ✅

**How it works:** You create `.prompt` files (or similar) in your workspace containing your well-crafted prompts.

**DevOps Use Case Examples:**

**New Terraform Module Scaffold (`new-tf-module.prompt`):**

```markdown
# Prompt for generating a new Terraform module structure

You are a highly opinionated DevOps expert.
Generate a basic Terraform module structure for a new Azure resource.
Include `main.tf`, `variables.tf`, `outputs.tf`, and a `README.md` following the provided best practices.
Ask me for the module's purpose and primary resource type (e.g., 'Azure App Service', 'Azure SQL Database').

Specifically, ensure:
- The `main.tf` has a placeholder for `resource` blocks.
- `variables.tf` has at least `location` and `resource_group_name` variables with descriptions.
- `outputs.tf` has a placeholder for key resource IDs/names.
- `README.md` includes sections for "Usage", "Inputs", "Outputs", and "Examples".
```

**Azure DevOps Pipeline Stage (`new-ado-stage.prompt`):**

```markdown
# Prompt for generating a new Azure DevOps pipeline stage

You are an Azure DevOps pipeline expert.
Generate a new stage for an Azure DevOps YAML pipeline.
The stage should be named dynamically, accept an `environment` parameter, and use an `AzureResourceManager@1` service connection.
Include steps for Terraform `init`, `plan`, and `apply`.
Ensure secrets are securely handled and not hardcoded.
Ask me for the stage name and target environment.
```

**Consistent README Update (`update-readme.prompt`):**

```markdown
# Prompt for updating a README.md file

You are a documentation specialist.
Help me update this README.md file.
I need to add a new section about 'Troubleshooting' to this document.
Generate a heading and two placeholder bullet points for common issues.
Maintain the existing markdown formatting and style.
```

💡 **My Take:** These are your personal, AI-powered snippets and templates. They save you typing, ensure consistency, and allow you to quickly invoke complex multi-part instructions. This is especially powerful when onboarding new team members – just point them to your prompt files!

### **3. Custom Chat Modes: Tailoring the Conversation**

Custom Chat Modes take customisation to another level. They define how Copilot operates within specific contexts, what tools it can leverage, and even how it interacts with your codebase. This allows you to create highly specialised Copilot experiences for different types of tasks. 🧠

**How it works:** This is more advanced and often involves defining modes that can integrate with various extensions or access specific parts of your project.

**DevOps Use Case Examples:**

**"Terraform Security Review Mode":** Imagine a mode that, when activated, instructs Copilot to specifically review your Terraform files for common security misconfigurations (e.g., open security groups, public storage accounts). It could suggest fixes or point to relevant Azure Security Centre recommendations.

**"Azure DevOps Pipeline Hardening Mode":** A mode that guides Copilot to analyse your YAML pipelines for security weaknesses, such as:
- Hardcoded secrets (it would suggest using Key Vault).
- Overly broad service connection permissions.
- Lack of mandatory approvals for sensitive stages.
- Absence of image scanning for container builds.

**"Network Topology Advisor Mode":** This mode could be amazing! You'd provide it with an existing VNet and subnet configuration, and Copilot could suggest the best way to integrate a new service using private endpoints, considering DNS zones and routing, based on your custom instructions for private networking.

💡 **My Take:** Think of these as giving Copilot a specific "hat" to wear for a particular job. It's about optimising its behaviour for a highly focused task, making it an even more powerful assistant for specialised DevOps work, deeply ingrained with your team's operational and security policies.

### **4. Providing Context: The Fuel for Intelligent AI**

No matter how many custom instructions you have, Copilot needs context to provide relevant suggestions. Always remember to give Copilot as much information as possible:

* **Current File:** The file you're actively working on.
* **Open Tabs:** Other relevant files open in your IDE (e.g., your `variables.tf` alongside your `main.tf`).
* **Selected Code:** Highlight specific code blocks to focus Copilot's attention.
* **Chat History:** Your ongoing conversation provides immediate context.
* **Copilot Spaces (for enterprise):** For larger organisations, Copilot Spaces can provide even broader context across repositories and internal documentation, massively boosting relevance.

💡 **My Take:** This is about actively guiding Copilot. The more specific and relevant the information you feed it, the more intelligent and helpful its responses will be. This is your chance to explicitly tell Copilot, "Hey, look at this existing network setup when you suggest that new database!"

## Practical Strategies for DevOps Teams: Making It Real

Ready to put this into practice? Here are some actionable strategies for you and your team:

* **Start Small, Iterate Often:** Don't try to define every single rule at once. Pick a pain point (e.g., inconsistent naming conventions, repetitive pipeline tasks, or ensuring private endpoints) and start there. Build momentum with small wins.

* **Document Your AI Guidelines:** Just like your coding standards, document your team's Copilot custom instructions and commonly used prompt files. Version control these! This is crucial for team alignment and auditability. Treat your AI configuration as code!

* **Share and Collaborate:** Encourage team members to contribute to and refine your collective AI assistant. The more brains feeding it, the smarter it gets. Regularly review and update your custom instructions as your tech stack or best practices evolve.

* **Measure the Impact:** How has customisation improved code quality? Reduced review cycles? Sped up common infrastructure tasks? Are you seeing more consistent private networking implementations? Keep an eye on the tangible benefits.

* **Identify Your "AI Champion":** Who on your team will take the lead in exploring, documenting, and evangelising Copilot customisation? Having a dedicated champion can make a huge difference in driving adoption and refinement.

## Things to Look Out For & Best Practices in Action:

### **For Terraform & IaC:**

* **Always validate:** Copilot is an assistant, not a replacement. Always run `terraform validate` and `terraform plan` to verify generated IaC.
* **Review Diff Carefully:** Especially when dealing with sensitive changes or private networking configurations, meticulously review the `terraform plan` output to ensure it matches expectations and doesn't expose anything unintentionally.
* **State Management:** Reiterate the importance of secure remote state (e.g., Azure Blob Storage with state locking) and never storing sensitive data in state files.
* **Private Endpoints Verification:** After deployment, always verify that private endpoints are indeed active and traffic is routed privately. Tools like `nslookup` (to confirm private IP resolution) or network trace tools can help.

### **For Azure DevOps YAML Pipelines:**

* **Security by Design:** Use templates for consistent security controls (e.g., mandatory static analysis steps).
* **Variable Group Hygiene:** Store non-sensitive variables in variable groups; sensitive ones must be linked to Azure Key Vault.
* **Least Privilege:** Ensure your Service Connections to Azure (or other cloud providers) adhere to the principle of least privilege. Only grant the necessary permissions for the pipeline's scope.
* **Agent Security:** If using self-hosted agents, ensure they are hardened, isolated, and have restricted outbound access. Microsoft-hosted agents are generally more secure by default for public-facing tasks.

### **For READMEs & Documentation:**

* **Consistency is Key:** Use prompt files to ensure all your READMEs follow a standard structure (e.g., "Overview," "Setup," "Usage," "Configuration," "Troubleshooting," "Contributing"). This makes onboarding and maintenance so much smoother.
* **Keep it Current:** Encourage teams to update READMEs as part of their Definition of Done. Copilot can make this less of a chore!

## The Road Ahead: AI as an Integral Part of DevOps Culture

Customising GitHub Copilot isn't just about tweaking settings; it's about evolving our relationship with AI. We're moving from simply using an AI to actively shaping it to fit our unique engineering culture and operational needs. This paves the way for even more sophisticated AI-driven DevOps: imagine AI-assisted incident response, proactive anomaly detection, or even self-healing systems that leverage your custom AI guidelines.

The future of DevOps is collaborative, and AI is becoming an increasingly integral part of that collaboration. By mastering Copilot customisation, you're not just enhancing your personal productivity; you're contributing to a smarter, more consistent, and more efficient future for your entire team.

So, what are you waiting for? Start customising your GitHub Copilot today and unlock its true potential! 🚀

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

Date: 21-04-2025
