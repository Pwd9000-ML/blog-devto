---
title: Tune GitHub Copilot Settings in VS Code
published: false
description: 'Review every GitHub Copilot and Copilot Chat setting in VS Code and grab a ready-to-use settings.json template.'
tags: 'vscode, copilot, tutorial, githubcopilot'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/VSCode-Copilot-Settings/assets/main.png'
canonical_url: null
id: 2995753
---

## Tune GitHub Copilot & Chat in VS Code

If you are rolling out GitHub Copilot across a team, the settings surface in VS Code can feel sprawling. This guide breaks the options into digestible groups, highlights what each toggle does, and finishes with a comprehensive `settings.json` you can paste into a workspace policy or user profile.

## Why It Matters

- Teams gain consistent Copilot behaviour across devices and projects.
- You can audit which preview or experimental capabilities are enabled before a rollout.
- Structured configuration keeps security-sensitive features (like tool auto-approve) under control.

## Key Concepts or Pillars

- Group Copilot settings by experience: editor completions, chat, agents, and workflow glue.
- Use workspace settings to enforce policy, user settings for personal preferences.
- Keep an annotated baseline JSON so teammates can diff intentional changes.

## Walk the Settings Groups

### General (chat / AI UI toggles)

- `chat.commandCenter.enabled`
- `workbench.settings.showAISearchToggle`
- `workbench.commandPalette.experimental.askChatLocation`
- `search.searchView.semanticSearchBehavior`
- `search.searchView.keywordSuggestions`

### Code Editing (completions & next edit suggestions)

- `github.copilot.editor.enableCodeActions`
- `github.copilot.renameSuggestions.triggerAutomatically`
- `github.copilot.enable`
- `github.copilot.nextEditSuggestions.enabled`
- `editor.inlineSuggest.edits.allowCodeShifting`
- `editor.inlineSuggest.edits.renderSideBySide`
- `github.copilot.nextEditSuggestions.fixes`
- `editor.inlineSuggest.minShowDelay`

### Chat (behaviour, fonts, context, terminals, models)

- `github.copilot.chat.localeOverride`
- `github.copilot.chat.useProjectTemplates`
- `github.copilot.chat.scopeSelection`
- `github.copilot.chat.terminalChatLocation`
- `chat.detectParticipant.enabled`
- `chat.checkpoints.enabled`
- `chat.checkpoints.showFileChanges`
- `chat.editRequests`
- `chat.editor.fontFamily`
- `chat.editor.fontSize`
- `chat.editor.fontWeight`
- `chat.editor.lineHeight`
- `chat.editor.wordWrap`
- `chat.editing.confirmEditRequestRemoval`
- `chat.editing.confirmEditRequestRetry`
- `chat.editing.autoAcceptDelay`
- `chat.fontFamily`
- `chat.fontSize`
- `chat.notifyWindowOnConfirmation`
- `chat.notifyWindowOnResponseReceived`
- `chat.tools.terminal.autoReplyToPrompts`
- `chat.tools.terminal.terminalProfile.<platform>`
- `chat.useAgentsMdFile`
- `chat.math.enabled`
- `github.copilot.chat.codesearch.enabled`
- `chat.emptyState.history.enabled`
- `chat.sendElementsToChat.enabled`
- `chat.useNestedAgentsMdFiles`
- `github.copilot.chat.customOAIModels`
- `github.copilot.chat.edits.suggestRelatedFilesFromGitHistory`

### Agent Mode (including MCP / auto-approve controls)

- `chat.agent.enabled`
- `chat.agent.maxRequests`
- `github.copilot.chat.agent.autoFix`
- `chat.mcp.access`
- `chat.mcp.discovery.enabled`
- `chat.mcp.gallery.enabled`
- `chat.tools.terminal.autoApprove`
- `chat.tools.global.autoApprove`
- `chat.agent.thinkingStyle`
- `chat.mcp.autoStart`
- `chat.agent.todoList.position`
- `github.copilot.chat.newWorkspaceCreation.enabled`
- `github.copilot.chat.agent.thinkingTool`
- `github.copilot.chat.virtualTools.threshold`

### Agent Sessions

- `chat.agentSessionsViewLocation`

### Inline Chat

- `inlineChat.finishOnType`
- `inlineChat.holdToSpeech`
- `editor.inlineSuggest.syntaxHighlightingEnabled`
- `inlineChat.lineEmptyHint`
- `inlineChat.lineNaturalLanguageHint`
- `github.copilot.chat.editor.temporalContext.enabled`

### Code Review

- `github.copilot.chat.reviewSelection.enabled`
- `github.copilot.chat.reviewSelection.instructions`

### Custom Instructions / Prompt Files / Chat Modes

- `github.copilot.chat.codeGeneration.useInstructionFiles`
- `chat.instructionsFilesLocations`
- `github.copilot.chat.commitMessageGeneration.instructions`
- `github.copilot.chat.pullRequestDescriptionGeneration.instructions`
- `chat.promptFiles`
- `chat.promptFilesLocations`
- `chat.modeFilesLocations`

> The VS Code Copilot customisation guide walks through instruction files, reusable prompts, and custom chat modes in depth. See "Customize chat to your workflow" on the Visual Studio Code docs.

### Debugging

- `github.copilot.chat.startDebugging.enabled`
- `github.copilot.chat.copilotDebugCommand.enabled`

### Testing

- `github.copilot.chat.generateTests.codeLens`
- `github.copilot.chat.setupTests.enabled`

### Notebooks

- `notebook.experimental.generate`
- `github.copilot.chat.edits.newNotebook.enabled`
- `github.copilot.chat.notebook.followCellExecution.enabled`

### Accessibility (chat-related)

- `inlineChat.accessibleDiffView`
- `accessibility.signals.chatRequestSent`
- `accessibility.signals.chatResponseReceived`
- `accessibility.signals.chatEditModifiedFile`
- `accessibility.signals.chatUserActionRequired`
- `accessibility.voice.keywordActivation`
- `accessibility.voice.autoSynthesize`
- `accessibility.voice.speechTimeout`

> Tip: To edit these values directly, open the Command Palette and run "Preferences: Open User Settings (JSON)" in VS Code. The full Copilot settings reference is available in the official documentation.

## Additional Insight or Use Case

Rolling Copilot out to a mixed environment? Keep a shared `settings.json` in `.vscode/` for regulated projects, then encourage developers to extend personal preferences in their user profile. This separation lets you lock down agent tooling (for example, disallowing destructive shell commands) while still letting individuals experiment with chat font sizing or inline suggestion delays.

## Practical Steps or How-To

1. Review the grouped settings above and mark which ones are mandatory for your team.
2. Copy the sample JSON below into `.vscode/settings.json` (workspace) or your user profile.
3. Trim the comments or keys you do not need, then commit the file so teammates inherit the same defaults.
4. Revisit the configuration quarterly; many Copilot features are still in preview and can change behaviour.

Prefer a ready-to-use file? [Download the JSON directly](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/VSCode-Copilot-Settings/assets/settings.json) and drop it into `.vscode/settings.json`.

```jsonc
{
  // ---------- General ----------
  "chat.commandCenter.enabled": true,
  "workbench.settings.showAISearchToggle": true,
  "workbench.commandPalette.experimental.askChatLocation": "chatView",
  "search.searchView.semanticSearchBehavior": "manual",
  "search.searchView.keywordSuggestions": false,

  // ---------- Code editing (Copilot completions / NES) ----------
  "github.copilot.editor.enableCodeActions": true,
  "github.copilot.renameSuggestions.triggerAutomatically": true,
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": false,
    "scminput": false,
  },
  "github.copilot.nextEditSuggestions.enabled": true,
  "editor.inlineSuggest.edits.allowCodeShifting": "always",
  "editor.inlineSuggest.edits.renderSideBySide": "auto",
  "github.copilot.nextEditSuggestions.fixes": true,
  "editor.inlineSuggest.minShowDelay": 0,

  // ---------- Chat ----------
  "github.copilot.chat.localeOverride": "auto",
  "github.copilot.chat.useProjectTemplates": true,
  "github.copilot.chat.scopeSelection": false,
  "github.copilot.chat.terminalChatLocation": "chatView",
  "chat.detectParticipant.enabled": true,
  "chat.checkpoints.enabled": true,
  "chat.checkpoints.showFileChanges": false,
  "chat.editRequests": "inline",
  "chat.editor.fontFamily": "default",
  "chat.editor.fontSize": 14,
  "chat.editor.fontWeight": "default",
  "chat.editor.lineHeight": 0,
  "chat.editor.wordWrap": "off",
  "chat.editing.confirmEditRequestRemoval": true,
  "chat.editing.confirmEditRequestRetry": true,
  "chat.editing.autoAcceptDelay": 0,
  "chat.fontFamily": "default",
  "chat.fontSize": 13,
  "chat.notifyWindowOnConfirmation": true,
  "chat.notifyWindowOnResponseReceived": true,
  "chat.tools.terminal.autoReplyToPrompts": false,
  "chat.tools.terminal.terminalProfile.windows": "",
  "chat.tools.terminal.terminalProfile.linux": "",
  "chat.tools.terminal.terminalProfile.osx": "",
  "chat.useAgentsMdFile": true,
  "chat.math.enabled": false,
  "github.copilot.chat.codesearch.enabled": false,
  "chat.emptyState.history.enabled": false,
  "chat.sendElementsToChat.enabled": true,
  "chat.useNestedAgentsMdFiles": false,
  "github.copilot.chat.customOAIModels": [],
  "github.copilot.chat.edits.suggestRelatedFilesFromGitHistory": true,

  // ---------- Agent mode (incl. MCP) ----------
  "chat.agent.enabled": true,
  "chat.agent.maxRequests": 25,
  "github.copilot.chat.agent.autoFix": true,
  "chat.mcp.access": true,
  "chat.mcp.discovery.enabled": false,
  "chat.mcp.gallery.enabled": false,
  "chat.tools.terminal.autoApprove": {
    "rm": false,
    "rmdir": false,
    "del": false,
    "kill": false,
    "curl": false,
    "wget": false,
    "eval": false,
    "chmod": false,
    "chown": false,
    "/^Remove-Item\\b/i": false,
  },
  "chat.tools.global.autoApprove": false,
  "chat.agent.thinkingStyle": "fixedScrolling",
  "chat.mcp.autoStart": "newAndOutdated",
  "chat.agent.todoList.position": "default",
  "github.copilot.chat.newWorkspaceCreation.enabled": true,
  "github.copilot.chat.agent.thinkingTool": false,
  "github.copilot.chat.virtualTools.threshold": 128,

  // ---------- Agent sessions ----------
  "chat.agentSessionsViewLocation": "disabled",

  // ---------- Inline chat ----------
  "inlineChat.finishOnType": false,
  "inlineChat.holdToSpeech": true,
  "editor.inlineSuggest.syntaxHighlightingEnabled": true,
  "inlineChat.lineEmptyHint": false,
  "inlineChat.lineNaturalLanguageHint": true,
  "github.copilot.chat.editor.temporalContext.enabled": false,

  // ---------- Code review ----------
  "github.copilot.chat.reviewSelection.enabled": true,
  "github.copilot.chat.reviewSelection.instructions": [],

  // ---------- Custom instructions / prompt files / chat modes ----------
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "chat.instructionsFilesLocations": { ".github/instructions": true },
  "github.copilot.chat.commitMessageGeneration.instructions": [],
  "github.copilot.chat.pullRequestDescriptionGeneration.instructions": [],
  "chat.promptFiles": true,
  "chat.promptFilesLocations": { ".github/prompts": true },
  "chat.modeFilesLocations": { ".github/chatmodes": true },

  // ---------- Debugging ----------
  "github.copilot.chat.startDebugging.enabled": true,
  "github.copilot.chat.copilotDebugCommand.enabled": true,

  // ---------- Testing ----------
  "github.copilot.chat.generateTests.codeLens": false,
  "github.copilot.chat.setupTests.enabled": true,

  // ---------- Notebooks ----------
  "notebook.experimental.generate": true,
  "github.copilot.chat.edits.newNotebook.enabled": true,
  "github.copilot.chat.notebook.followCellExecution.enabled": false,

  // ---------- Accessibility (chat-related) ----------
  "inlineChat.accessibleDiffView": "auto",
  "accessibility.signals.chatRequestSent": {
    "sound": "auto",
    "announcement": "auto",
  },
  "accessibility.signals.chatResponseReceived": { "sound": "auto" },
  "accessibility.signals.chatEditModifiedFile": { "sound": "auto" },
  "accessibility.signals.chatUserActionRequired": {
    "sound": "auto",
    "announcement": "auto",
  },
  "accessibility.voice.keywordActivation": "off",
  "accessibility.voice.autoSynthesize": "off",
  "accessibility.voice.speechTimeout": 1200,
}
```

## Tips, Tricks, or Best Practices

- Keep destructive shell commands marked as `false` in `chat.tools.terminal.autoApprove` to prevent unintended actions.
- Disable Copilot for filetypes like `markdown` or `plaintext` if you prefer to write prose unaided.
- Pair the `chat.instructionsFilesLocations` setting with a `.github/instructions` folder so all contributors see the same guidance.
- Re-enable `github.copilot.chat.codesearch.enabled` only after validating access controls for your repositories.

## Conclusion

With the settings grouped and a baseline JSON in hand, you can standardise Copilot across your workspace in minutes. Tailor the defaults for security, productivity, or experimentation, then iterate as the Copilot feature set evolves.

### _Author_

{% user pwd9000 %}

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-pwd9000//)

Date: 05-11-2025
