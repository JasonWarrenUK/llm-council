---
description: Suggest the next logical task based on an examination of the codebase & user input
argument-hint: [suggested focus]
# allowed-tools:
model: claude-sonnet-4-5-20250929
disable-model-invocation: false
---

<overview>
    Analyse the current state of the codebase, then compare it to the project documentation. Once done, suggest the next logical task I can complete.
</overview>
<rules>
    1. If the task will take longer than 45 minutes, subdivide it into subtasks and suggest the first of these.
    2. If `<inputs>` contains text content, give me a task that focusses on that area
    3. Conserve tokens by being selective in which files you read
    4. Where possible, use the dev scripts in @./package.json & @./scripts to retrieve information rather than passing file content into your context window
</rules>
<inputs>
    $ARGUMENTS
</inputs>
