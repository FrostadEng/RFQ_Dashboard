# CSS Style Guide

## 1. Guiding Principles & Tooling

We use the latest version of TailwindCSS as a utility-first framework to build our user interface. Our primary goal is to create a consistent, scalable, and maintainable styling system.

### Automated Formatting

To ensure consistency, all code is automatically formatted on commit using **Prettier** with the `prettier-plugin-tailwindcss`. This plugin enforces a canonical sort order for all utility classes.

**Our multi-line formatting style (see Section 2) is a convention for developer readability *while writing code*. However, the automated formatter is the final source of truth for the committed code to ensure consistency and prevent manual formatting debates.**

### Component Abstraction Philosophy

-   **Prefer Component Props over `@apply`:** Instead of using `@apply` to create custom CSS classes for component variants, we prefer to build logic into our components (e.g., React, Vue components) that conditionally apply Tailwind classes based on props. This keeps styling concerns co-located with the component's markup and logic.

    -   **Bad (using `@apply`):**
        ```css
        .btn-primary {
          @apply bg-blue-600 text-white font-bold py-2 px-4 rounded;
        }
        .btn-secondary {
          @apply bg-gray-500 text-white font-bold py-2 px-4 rounded;
        }
        ```

    -   **Good (using component logic):**
        ```jsx
        // Inside a Button.jsx component
        const baseClasses = "font-bold py-2 px-4 rounded";
        const variantClasses = {
          primary: "bg-blue-600 text-white",
          secondary: "bg-gray-500 text-white",
        };
        const className = `${baseClasses} ${variantClasses[variant]}`;
        // <button className={className}>...</button>
        ```

## 2. Class Formatting in Markup

When writing Tailwind classes in HTML/JSX, we use a unique multi-line formatting style to improve readability for complex, responsive components.

-   Classes are grouped by responsive breakpoint, with each breakpoint on its own line.
-   The order is mobile-first: the top line has no prefix, followed by `xs:`, `sm:`, `md:`, and so on.
-   State modifiers like `hover:` and `focus:` should be on their own dedicated lines following the base styles.
-   All lines of utility classes should be vertically aligned.
-   Any custom, non-Tailwind CSS classes must be placed at the start of the very first line.

**Example:**

```html
<div class="custom-cta bg-gray-50 dark:bg-gray-900 p-4 rounded cursor-pointer w-full
            hover:bg-gray-100 dark:hover:bg-gray-800
            xs:p-6
            sm:p-8 sm:font-medium
            md:p-10 md:text-lg
            lg:p-12 lg:text-xl lg:font-semibold lg:w-3/5
            xl:p-14 xl:text-2xl
            2xl:p-16 2xl:text-3xl 2xl:font-bold 2xl:w-3/4">
  I'm a call-to-action!
</div>
```

## 3. Configuration and Customization

### Custom Breakpoints

-   We implement one additional responsive breakpoint, `xs`, which represents `400px`.
-   This must be configured in the `tailwind.config.js` file to be available.

**`tailwind.config.js` configuration:**

```js
// tailwind.config.js
const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  theme: {
    screens: {
      'xs': '400px',
      ...defaultTheme.screens,
    },
    // ... other theme extensions
  },
  // ...
};
```

### Using Theme Values vs. Arbitrary Values

-   **Always prefer theme values** (e.g., `p-4`, `bg-blue-500`) over arbitrary, "magic number" values (e.g., `p-[17px]`).
-   If a specific value (color, spacing, font size) is needed in more than one place, add it to the `tailwind.config.js` theme extension. This ensures consistency and makes future design updates easier.

    -   **Bad:** `top-[13px]`
    -   **Good (if `13px` is a standard offset):** Add `spacing: { 'nav-offset': '13px' }` to the config and use `top-nav-offset`.

## 4. Custom CSS Rules

-   Avoid writing custom CSS whenever possible. Strive to accomplish styling goals with Tailwind's utility classes and theme configuration.
-   When custom CSS is unavoidable (e.g., for complex animations or third-party library overrides), place it in a dedicated `.css` file within the component's directory.
-   Use a linter like **Stylelint** to maintain consistency in any handwritten CSS files.