# Code Style Guide

## Context

Global code style rules for Agent OS projects.

## Automated Tooling & Linting

To ensure consistency and reduce the cognitive load of remembering every rule, we enforce our style guide automatically.

-   **Auto-formatting with Prettier:** All code should be formatted using Prettier with the project's shared configuration (`.prettierrc`). This handles rules like indentation, line length, quotes, and spacing automatically. Run `npm run format` before committing.
-   **Linting with ESLint:** We use ESLint to catch stylistic issues and potential bugs that Prettier doesn't handle. Rules are defined in the project's `.eslintrc` file. You should see linter errors directly in your editor.
-   **Commit Hooks:** A pre-commit hook is configured to run the formatter and linter on staged files, preventing code that violates our style from being committed.

## General Formatting

### Indentation
-   Use **2 spaces** for indentation. Never use tabs.
-   Configure your editor to use spaces for tabs to enforce this automatically.

### Line Length
-   Keep lines of code to a **maximum of 100 characters**.
-   This improves readability, especially on smaller screens or in split-view editors. Prettier will handle this automatically for most cases.

### Whitespace
-   Use single blank lines to separate logical blocks of code within functions or classes.
-   Avoid multiple consecutive blank lines.
-   Place a single space after commas in argument lists and around operators (`i = i + 1`, not `i=i+1`).

### Trailing Commas
-   Use trailing commas in multi-line arrays, objects, and parameter lists.
-   **Why?** This leads to cleaner Git diffs. When you add a new item, only one line is added, instead of one line being modified and one being added.
    -   **Bad:**
        ```javascript
        const user = {
          name: 'Alice',
          email: 'alice@example.com' // Line modified if a new property is added
        };
        ```
    -   **Good:**
        ```javascript
        const user = {
          name: 'Alice',
          email: 'alice@example.com', // No change here when adding a new property
        };
        ```

## Naming Conventions (for JavaScript/TypeScript)

-   **Methods and Variables**: Use **camelCase** (e.g., `userProfile`, `calculateTotal`).
    -   **Booleans** should be prefixed with `is`, `has`, or `should` (e.g., `isLoggedIn`, `hasPermission`).
-   **Functions**: Use **camelCase** for function names (e.g., `getUserProfile()`).
-   **Classes, Modules, and Components**: Use **PascalCase** (e.g., `UserProfile`, `PaymentProcessor`).
-   **Constants**: Use **UPPER_SNAKE_CASE** for top-level or exported constants that are truly immutable (e.g., `MAX_RETRY_COUNT`, `API_KEY`). For local, non-reassigned variables, use `const` with camelCase.

## String Formatting

-   Use **single quotes** (`'`) for all strings unless they contain a single quote.
-   Use **template literals** (backticks `` ` ``) for strings that require interpolation or are multi-line. Avoid string concatenation with the `+` operator.
    -   **Bad:** `'User ' + user.name + ' has logged in.'`
    -   **Good:** `\`User ${user.name} has logged in.\``

## Code Comments

-   Add brief comments above non-obvious business logic.
-   Document complex algorithms or calculations.
-   Explain the **"why"** behind implementation choices, not the "what."
-   **Avoid Commented-Out Code:** Delete dead code. Version control (Git) is our history; we don't need to keep old implementations commented out in the codebase.
-   **Use Standardized Tags:**
    -   `// TODO:` for tasks that need to be done later. Include a brief description.
    -   `// FIXME:` for code that is broken or needs to be fixed. Explain the issue.
-   Update comments when modifying the associated code to maintain accuracy.
-   Keep comments concise and relevant.

<conditional-block task-condition="html-css-tailwind" context-check="html-css-style">
IF current task involves writing or updating HTML, CSS, or TailwindCSS:
  IF html-style.md AND css-style.md already in context:
    SKIP: Re-reading these files
    NOTE: "Using HTML/CSS style guides already in context"
  ELSE:
    <context_fetcher_strategy>
      IF current agent is Claude Code AND context-fetcher agent exists:
        USE: @agent:context-fetcher
        REQUEST: "Get HTML formatting rules from code-style/html-style.md"
        REQUEST: "Get CSS and TailwindCSS rules from code-style/css-style.md"
        PROCESS: Returned style rules
      ELSE:
        READ the following style guides (only if not already in context):
        - @.agent-os/standards/code-style/html-style.md (if not in context)
        - @.agent-os/standards/code-style/css-style.md (if not in context)
    </context_fetcher_strategy>
ELSE:
  SKIP: HTML/CSS style guides not relevant to current task
</conditional-block>

<conditional-block task-condition="javascript" context-check="javascript-style">
IF current task involves writing or updating JavaScript:
  IF javascript-style.md already in context:
    SKIP: Re-reading this file
    NOTE: "Using JavaScript style guide already in context"
  ELSE:
    <context_fetcher_strategy>
      IF current agent is Claude Code AND context-fetcher agent exists:
        USE: @agent:context-fetcher
        REQUEST: "Get JavaScript style rules from code-style/javascript-style.md"
        PROCESS: Returned style rules
      ELSE:
        READ: @.agent-os/standards/code-style/javascript-style.md
    </context_fetcher_strategy>
ELSE:
  SKIP: JavaScript style guide not relevant to current task
</conditional-block>