---
name: create-plan
description: Create a an implementation plan based on user input and project context
argument-hint: [desired outcome]
# allowed-tools:
model: claude-sonnet-4-5-20250929
disable-model-invocation: false
---

<overview>
    Convert `<inputs>` into a detailed implementation plan.
</overview
<inputs>
    $ARGUMENTS
</inputs>
<instructions>
    <role>
        You are an experienced developer on the current project.
    </role>
    <steps>
        1. Determine the project root by looking for common indicators (.git, package.json, etc.)
        2. Parse the command arguments to determine the desired result
        3. Locate and analyse existing relevant files
        4. Think about the constituent subtasks that need to be achieved
        5. Think about the correct order in which to execute these tasks
    </steps>
</instructions>
<rules>
    1. Align your approach with existing project implementations
</rules>
