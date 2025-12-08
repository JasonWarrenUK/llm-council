---
description: Suggest the next logical task based on an analysis of the codebase
# argument-hint: null
# allowed-tools:
model: claude-sonnet-4-5-20250929
disable-model-invocation: true
---

<overview>
    Analyse the current state of the codebase, then compare it to the project documentation. Once done, suggest the next logical task I can complete.
</overview>
<rules>
    1. If the task will take longer than 45 minutes, subdivide it into subtasks and suggest the first of these.
    2. Conserve tokens by being selective in which files you read
    3. Where possible, use the dev scripts in @./package.json & @./scripts to retrieve information rather than passing file content into your context window
</rules>
