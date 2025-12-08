---
description: Provide a detailed high-level overview of this codebase
argument-hint: [focus of analysis]
# allowed-tools:
model: claude-sonnet-4-5-20250929
# disable-model-invocation: true
---

<overview>
    Provide an overview of this codebase aimed at a newly-joined member of the development team.
</overview>
<role>
    1. You are an experienced developer.
    2. You are particularly skilled at...
        - Explaining complex code
        - Familiarity with this tech stack
</role>
<steps>
    <step-1>
        Analyse the codebase. Use the same process that a human developer would employ when reading unfamiliar code.
    </step-1>
    <step-2>
        Check whether `<inputs>` contains any content. If it does, think about how that content is demonstrated within this codebase.
    </step-2>
    <step-3>
        Provide a practical, detailed and coherent overview of the codebase.
    </step-3>
</steps>
<inputs>
    $ARGUMENTS
</inputs>
<guidance>
    <explanation-audience>
        1. The user started learning to code 3 years ago.
        2. The user is very experienced with...
            - CSS
            - git (common operations)
            - Github
            - HTML
            - Javascript
            - React
            - Typescript (common features)
        3. The user has some experience with...
            - Neo4j
            - n8n
            - Supabase
            - Svelte
            - Tailwind
            - Typescript (advanced features)
        4. The user has vague familiarity with...
            - C#
            - Docker
            - git (advanced concepts)
            - MongoDB
            - Python
    </explanation-audience>
</guidance>
