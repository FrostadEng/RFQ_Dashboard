# HTML Style Guide

## Automated Formatting with Prettier

To ensure consistent formatting without manual effort, all HTML code (including in JSX/TSX files) must be formatted using **Prettier**. Our project's shared configuration (`.prettierrc`) is set up to enforce the rules outlined in this document.

-   **How it works:** Prettier automatically handles indentation, attribute wrapping, and line length. The "one attribute per line" rule for complex tags is a natural outcome of setting a reasonable `printWidth` (e.g., 100 characters) in the Prettier config.
-   **Enforcement:** A pre-commit hook will run Prettier on staged files, ensuring that no unformatted code is committed to the repository.

## Semantic HTML & Best Practices

Writing semantic HTML means using tags for their correct purpose, not just for their appearance. This is non-negotiable.

-   **Use Structural Elements:** Structure your pages with landmark elements. This helps screen readers and search engines understand the layout.
    -   `<header>`: For introductory content or navigational links.
    -   `<nav>`: For major navigation blocks.
    -   `<main>`: For the primary, unique content of the page. There should only be one per page.
    -   `<footer>`: For the footer of a page or section.
    -   `<section>`: For grouping related content. Should typically have a heading.
    -   `<article>`: For self-contained content (e.g., a blog post, a product card).

-   **Buttons vs. Links:**
    -   `<a>`: Use for **navigation** (going to a new page or a different part of the current page).
    -   `<button>`: Use for **actions** (e.g., submitting a form, opening a modal, triggering a script).

-   **Headings:** Use headings (`<h1>` through `<h6>`) to create a logical outline of the page. Do not skip levels. There should be only one `<h1>` per page.

## Accessibility (A11y)

All HTML must be written to be accessible to users with disabilities.

-   **Image `alt` Text:** All `<img>` tags **must** have an `alt` attribute.
    -   If the image is decorative, use an empty `alt=""`.
    -   If the image conveys information, the `alt` text should describe its content or function.

-   **Form Labels:** All form inputs (`<input>`, `<textarea>`, `<select>`) **must** have a corresponding `<label>` tag. The `for` attribute of the label should match the `id` of the input.

-   **ARIA Roles:** Use ARIA attributes for dynamic components (like modals or tabs), but always prefer using a native semantic HTML element when one exists.

## Formatting Example

The following example demonstrates our formatting and semantic principles. Prettier will automatically format complex elements this way.

```html
<main class="container">
  <header
    class="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-4"
  >
    <h1 class="text-primary dark:text-primary-300">
      Page Title
    </h1>
    <nav
      aria-label="Main navigation"
      class="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-4"
    >
      <a href="/" class="btn-ghost">
        Home
      </a>
      <a
        href="/about"
        class="btn-ghost"
      >
        About
      </a>
    </nav>
  </header>

  <section aria-labelledby="section-heading">
    <h2 id="section-heading">Content Section</h2>
    <p>This is a paragraph inside a semantic section element.</p>
  </section>
</main>
```