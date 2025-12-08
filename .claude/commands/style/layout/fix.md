---
description: fix layout problems whilst considering knock-on effects
argument-hint: [semicolon separated list of layout issues]
# allowed-tools:
model: claude-sonnet-4-5-20250929
---

<overview>
    1. Here is semicolon-separated list of layout-based problems: $ARGUMENTS
    2. We are going to create a plan to fix these issues
    3. Once approved by the user, you will then execute that plan.
</overview>
<steps>
    <step-1>
        Ask for clarity regarding any issues for which you do not have enough detail
    </step-1>
    <step-2>
        Think about the probable causes of these issues
    </step-2>
    <step-3>
        Think about how to solve these issues in a logical order
    </step-3>
    <step-4>
        Give a brief summary of each of the plan's steps and ask for permission to execute it
    </step-4>
</steps>
<rules>
    1. If editing multiple files, check for permission before each file is edited.
    2. Proceed in a logical order (for example, fixing a parent container before a child container)
    3. Ensure your solutions use the same styling approach used in the rest of the project
    4. All other things being equal, prioritise solutions that edit the CSS file, editing other
</rules>
