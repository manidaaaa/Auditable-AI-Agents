---
name: paradigm-checker
description: Analyzes files to ensure code follows functional programming boundaries instead of object-oriented mutability.
triggers: ["/check-paradigm", "review architecture", "check design pattern"]
---

# Paradigm Checker Instructions

When this skill is invoked, evaluate the selected code or active file against the following paradigm constraints:

1. **No Shared Mutable State**: Ensure all variables use read-only primitives (`const` in TypeScript). Flag any instances of `let` or object property mutations.
2. **Pure Functions**: Check that functions accept inputs and return outputs explicitly. Flag functions relying on global state, network conditions, or side effects.
3. **No Classes**: Ensure code relies entirely on pure functions and algebraic data structures. Flag any usage of the `class` keyword.

## Output Format
Provide a direct breakdown of any violations:
- **File & Line**: Where the issue resides.
- **Violation**: Why it breaches our core paradigm.
- **Proposed Refactor**: A blocks-of-code comparison showing the correct paradigm implementation.
