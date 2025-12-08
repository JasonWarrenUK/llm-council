---
description: edit the styling of a component to make it fit the rest of the project
argument-hint: [component to edit]
# allowed-tools:
model: claude-sonnet-4-5-20250929
disable-model-invocation: false
---

<overview>
    1. Analyse the styling of this component (and its children): $ARGUMENTS
    2. We will then make edits based on your analysis
</overview>
<steps>
    <step-1>
        Provide an analysis of how well the approach used is consistent with the rest of the codebase.
    </step-1>
    <step-2>
        Provide a list of suggestions for how to maintain the exact same styling outcomes in this component whilst using the codebase' established approach.
    </step-2>
    <step-3>
        Once you receive approval, apply the changes to the component and its children.
    </step-3>
</steps>
<rules>
    1. If editing multiple components, check for permission before each file is edited.
    2. Start with `*.css` files
    3. Then proceed through child components
    4. Finally, end with the parent component
</rules>
<guidance>
    1. Always consider whether a layout issue is best addressed by directly editing the component or making changes to its parent
</guidance>
