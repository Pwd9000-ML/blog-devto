---
title: Supercharge VS Code Copilot with MCP for GitHub
published: false
description: 'Unlock the power of GitHub Copilot in VS Code with the Model Context Protocol (MCP) for seamless GitHub integration.'
tags: 'GitHubCopilot, MCP, tutorial, AI, DevOps'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevAIOps-MCP-GitHub/assets/main.png'
canonical_url: null
id: 2420334
series: DevAIOps
---

## Introduction

GitHub Copilot has revolutionised the way developers write code, providing intelligent suggestions and automating repetitive tasks. With the introduction of **Copilot Chat**, users can now interact with Copilot in a conversational manner, asking questions and getting contextual help. But what if you could take this a step further? What if you could enable Copilot to perform actions directly on your GitHub repositories, like creating issues or searching for code snippets?

Enter the **Model Context Protocol (MCP)**. MCP is an open standard that allows AI applications like Copilot Agent Mode to securely connect with external tools and data sources, enabling a more integrated experience.

In this guide, we'll walk you through the process of setting up the **GitHub MCP server** in **VSCode** using **Node.js** (specifically npx), allowing you to supercharge your Copilot experience in Agent Mode. This setup will enable Copilot to interact directly with the GitHub API, allowing you to perform various actions like summarising or even creating issues, reading files, and searching code repositories directly from the chat interface.

We will also cover the prerequisites, configuration steps, tips to ensure a smooth setup, and troubleshooting advice

## Prerequisites

Before we start, make sure you have the following installed and set up:

- **Visual Studio Code**: The latest stable or insiders release.
- **GitHub Copilot & Copilot Chat Extensions**: Installed and enabled in VS Code.
- **Node.js and npm/npx**: Node.js (version 23 or higher recommended) and its package manager npm (which includes npx) must be installed. You can download them from [nodejs.org](https://nodejs.org).
- **GitHub Account**: You'll need a GitHub account.
- **GitHub Personal Access Token (PAT)**: A token to authenticate the MCP server with GitHub.

Go to your GitHub Settings. Navigate to Developer settings > Personal access tokens > Tokens (classic).   Click Generate new token and choose Generate new token (classic).   Give your token a descriptive Note (e.g., "VSCode-MCP-Server-Token"). Set an Expiration date. Select the necessary scopes (permissions). For general use (reading repos, managing issues), the repo scope might be sufficient. For public repositories only, public_repo could work. Important: Grant only the permissions you need (principle of least privilege).   Click Generate token.   Crucial: Copy the generated token immediately and save it somewhere secure (like a password manager). GitHub will not show it again. Treat this token like a password.   Step 2: Ensure Node.js and npx are Ready Verify your Node.js and npx installation by opening your terminal or command prompt and running:

Bash

node -v npx -v If these commands return version numbers, you're good to go. If not, install Node.js from nodejs.org.

Step 3: Configure the GitHub MCP Server in VS Code Now, let's tell VS Code how to run the GitHub MCP server using npx. You can configure this per-project (recommended for collaboration) or globally in your user settings.

Option A: Workspace Configuration (Recommended)

Open your project folder in VS Code.

Create a file named mcp.json inside the .vscode directory (i.e., .vscode/mcp.json).  

Paste the following JSON configuration into the mcp.json file:

JSON

{ "servers": { "github-mcp-server": { "command": "npx", "args": [ "-y", "@modelcontextprotocol/server-github" ], "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "PASTE_YOUR_GITHUB_PAT_HERE" } } } } Replace "PASTE_YOUR_GITHUB_PAT_HERE" with the actual GitHub PAT you generated in Step 1.

Security Warning: The .vscode folder is often committed to version control. Do not commit your PAT directly in this file if you share your repository. Consider using environment variable placeholders or VS Code input variables for shared configurations , although direct pasting is the simplest method for personal use.  

Option B: User Settings Configuration (Global)

Open the VS Code Command Palette (Ctrl+Shift+P or Cmd+Shift+P).

Type "Preferences: Open User Settings (JSON)" and select it.

Find the "mcp" key in your settings.json file. If it doesn't exist, add it.

Add the server configuration under the servers object within "mcp":

JSON

{ //... other settings... "mcp": { "servers": { "github-mcp-server": { "command": "npx", "args": [ "-y", "@modelcontextprotocol/server-github" ], "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "PASTE_YOUR_GITHUB_PAT_HERE" } } //... potentially other global servers... } } //... other settings... } Replace "PASTE_YOUR_GITHUB_PAT_HERE" with your PAT.

Configuration Explained:

"github-mcp-server": A unique name you give to this server configuration. "command": "npx": Specifies that we'll use npx to run the server.   "args": ["-y", "@modelcontextprotocol/server-github"]: These are the arguments passed to npx. -y skips confirmation prompts, and @modelcontextprotocol/server-github is the official npm package for the GitHub MCP server.   "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "..." }: This sets the necessary environment variable within the server's process, providing it with your PAT for authentication.   Step 4: Verify the Setup Let's make sure VS Code recognizes and can run the server:

Restart VS Code: It's often good practice to restart VS Code after changing configurations like this. Check MCP Server Status: Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P). Type "MCP: List Servers" and select it.   You should see "github-mcp-server" listed. You can select it to view its status, start/stop it manually, or view its output logs. Check the logs for any error messages if it fails to start.   Check Copilot Agent Mode Tools: Open the Copilot Chat view (Ctrl+Alt+I or Cmd+Opt+I). Select "Agent" mode from the dropdown in the chat input area.   Click the "Tools" icon (often looks like a plug or puzzle piece) next to the input box.   You should see tools related to GitHub (e.g., create_issue, get_file_contents, search_repositories) listed, provided by github-mcp-server.   Step 5: Using GitHub Tools in Copilot Agent Mode With the server running and recognized, you can now ask Copilot Agent Mode to perform GitHub tasks:

Make sure you are in Agent Mode in the Chat view.   Ensure the relevant GitHub tools are enabled in the Tools menu.   Try prompts like: "List open issues in the owner/repo repository." "What are the latest commits in owner/repo?"   "Get the contents of the README.md file in owner/repo."   "Create a new issue in owner/repo titled 'Update documentation' with the body 'Need to add details about MCP setup'."   "Search for repositories about 'model context protocol'."   Approval: For actions that modify things (like creating issues or files), Copilot will show you the tool it intends to use and its parameters. You'll need to approve the action before it runs. You can often choose to approve just once, for the session, or always for that specific tool.   Troubleshooting Tips PAT Errors: Double-check that the PAT is copied correctly and hasn't expired. Ensure it has the necessary scopes (repo) for the actions you're attempting.   command not found: npx or ENOENT errors: Your Node.js installation might not be correctly added to your system's PATH. Try using the full path to npx in the "command" field. You can find the path by running which npx (Linux/macOS) or where npx (Windows) in your terminal.   Node Version Issues: Some MCP servers require specific Node.js versions. While the GitHub server is generally compatible, if you encounter strange errors, consider using a Node Version Manager (like nvm or nvs) to switch to a different Node.js version and update the command/args in your configuration accordingly.   Server Not Starting: Check the server logs via "MCP: List Servers" > "Show Output" for specific error messages.   Conclusion You've now successfully configured the GitHub MCP server in VS Code using npx! This setup empowers GitHub Copilot Agent Mode to act as a more integrated development assistant, capable of directly interacting with your repositories based on your chat prompts. Explore the available tools, experiment with different prompts, and enjoy a more streamlined GitHub workflow directly within your editor.  
