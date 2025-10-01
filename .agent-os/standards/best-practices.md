Of course. Here is the updated "Development Best Practices" document with the requested edits and additions integrated.

***

# Development Best Practices

## Context

Global development guidelines for Agent OS projects.

## Core Principles

### Keep It Simple
- **Strive for conciseness without sacrificing clarity.** The goal isn't just the "fewest lines of code," but the least complex solution that is easy to understand and maintain.
- **Avoid premature abstraction.** Don't build a complex, abstract solution for a problem you *might* have in the future. Solve the immediate problem simply. Refactor for abstraction later when a clear pattern of repetition has emerged.
- **Choose straightforward approaches over "clever" one-liners.** If you have to stare at a line of code for 30 seconds to understand what it does, it's probably too clever.

### Optimize for Readability
- **Prioritize code clarity over micro-optimizations.** In most cases, developer time is more expensive than CPU cycles. Only optimize performance when a real bottleneck has been identified through profiling.
- **Write self-documenting code with clear, descriptive names.**
  - **Bad:** `let d = new Date(); // get date`
  - **Good:** `const elapsedTimeInDays = ...`
- **Add comments for "why," not "what."** The code itself should explain *what* it is doing. Comments should explain the business reason or the trade-offs.
  - **Bad:** `// Increment the counter`
    `i++;`
  - **Good:** `// The API returns a header record we need to skip, so we start at the second item.`
    `i = 1;`

### DRY (Don't Repeat Yourself)
- **The Rule of Three:** When you find yourself copy-pasting the same piece of logic for the third time, it's a clear signal that it's time to abstract it into a reusable function, method, or component.
- **Beware of Hasty Abstractions.** Sometimes, repeating a small amount of code is better than creating a confusing or incorrect abstraction. The cost of a bad abstraction is often higher than the cost of some duplication.
- Extract repeated business logic to private methods or dedicated **service classes/modules**.
- Extract repeated UI markup to reusable **components with a clear props API**.
- Create utility functions for common, pure operations (e.g., `formatDate`, `calculateDiscount`).

### File Structure
- **Keep files focused on a single responsibility (Single Responsibility Principle).** A file for a component should only contain that component's logic. A file for API services should only contain API-related code.
- **Group related functionality together.** Choose a project-wide strategy and stick to it. Common patterns include:
  - **Grouping by type:** `/components`, `/services`, `/hooks`
  - **Grouping by feature:** `/user-profile`, `/dashboard`, `/settings` (Each feature folder contains its own components, services, etc.)
- **Use consistent naming conventions for files and directories.** For example: `UserProfile.tsx` for a component, `user.service.ts` for a service, and `useUserAuth.ts` for a hook.

## Code Review & Pull Requests

### Creating Pull Requests
- **Keep PRs Small and Focused:** A PR should address a single concern. If it fixes a bug and adds a new feature, it should be two separate PRs. This makes reviews faster and more effective.
- **Write a Clear Description:** The PR description is your chance to provide context. Explain *why* the change is being made (link to a ticket/issue), *what* the change is, and *how* you tested it. Use screenshots or GIFs for UI changes.
- **Self-Review First:** Before requesting a review, read through your own code changes. You'll often catch simple mistakes. Run the linter, tests, and build process locally to ensure everything passes.

### Reviewing Pull Requests
- **Be Kind and Constructive:** The goal is to improve the code, not to criticize the author. Phrase suggestions as questions ("What do you think about extracting this to a helper function?") rather than demands.
- **Test the Changes:** If possible, pull the branch down and test the changes locally, especially for complex logic or UI work.
- **Balance "Perfect" and "Good Enough":** The goal is high-quality, maintainable code, not unattainable perfection. Distinguish between essential changes (bugs, architectural issues) and minor stylistic preferences.

## Testing Principles

### The "Why" of Testing
- **Confidence:** A solid test suite allows us to refactor and add new features with confidence, knowing we haven't broken existing functionality.
- **Documentation:** Well-written tests serve as living documentation for how a piece of code is intended to be used.

### What to Test
- **Unit Tests:** Test the smallest units of your code (e.g., a single function or component) in isolation. Focus on business logic, edge cases, and utility functions. Aim for high code coverage in critical logic areas.
- **Integration Tests:** Test how multiple units work together. For example, does a form component correctly call the API service when submitted?
- **End-to-End (E2E) Tests:** Test critical user flows from start to finish in a browser-like environment. These are slow and brittle, so reserve them for your most important "happy path" scenarios (e.g., user login, checkout process).

## Dependencies

### Choose Libraries Wisely
When adding third-party dependencies, you are adopting their code (and their bugs) as your own. Perform due diligence.

- Select the most popular and **actively maintained** option that fits your use case.
- **Check the library's health:**
  - **Recent Commits:** Is the project still alive? (GitHub)
  - **Open Issues/PRs:** Are issues being actively addressed? A high number of old, open issues is a red flag. (GitHub)
  - **Bundle Size:** How much will this library add to the application's final size? Use tools like `bundlephobia.com` to check the impact.
  - **Security Vulnerabilities:** Run `npm audit` or use tools like Snyk to check for known vulnerabilities in the library or its dependencies.
  - **License:** Ensure the library has a permissive license (e.g., MIT, Apache 2.0) that is compatible with our project's license. Avoid GPL or other copyleft licenses unless explicitly approved.
  - **TypeScript Support:** For TS projects, does the library have built-in types or a high-quality package on `@types`? Poor or missing types can negate many of TypeScript's benefits.
  - **Clear Documentation:** Does the library have a website with clear documentation and examples?