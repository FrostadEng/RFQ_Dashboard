# JavaScript Style Guide

## Context

This document outlines the style guide and best practices for writing JavaScript and TypeScript in all Agent OS projects, including FactorySim. Our primary goal is to write code that is clear, consistent, and maintainable.

## 1. Tooling (The Golden Rule)

**Rule:** Let the tools do the work.

We enforce our style guide automatically. Do not argue with the linter or formatter; they are the source of truth.

-   **Formatting:** **Prettier** is configured to handle all stylistic formatting (indentation, spacing, quotes, line length, etc.). All committed code **must** be formatted by Prettier.
-   **Code Quality:** **ESLint** is configured to catch potential bugs, enforce best practices, and ensure framework-specific rules (like React hooks) are followed. You should not be able to commit code if it has ESLint errors.

## 2. Variables

**Rule:** Use `const` by default; use `let` only when a variable must be reassigned. Never use `var`.

-   **Why?** `const` ensures that a variable cannot be reassigned, which prevents a large class of bugs. This makes code easier to reason about. `var` has confusing scoping rules and should be avoided entirely.

```javascript
// Good
const user = { name: 'Alice' };
let retryCount = 0;
retryCount = 1;

// Bad
var user = { name: 'Alice' }; // Avoid `var`
const retryCount = 0;
retryCount = 1; // Error: Assignment to constant variable. Use `let` instead.
```

## 3. Functions

**Rule:** Prefer arrow functions (`=>`) for all functions, especially for callbacks and React components.

-   **Why?** Arrow functions have a more concise syntax and, crucially, do not have their own `this` context, which solves a common source of bugs in JavaScript, particularly within class components and callbacks.

```javascript
// Good: Concise and lexically scoped `this`
const getUserById = (id) => {
  return db.users.find(user => user.id === id);
};

// Also good for React components
const UserProfile = ({ user }) => (
  <div>
    <h1>{user.name}</h1>
  </div>
);

// Bad: More verbose
function getUserById(id) {
  return db.users.find(function(user) {
    // `this` would be different here if used
    return user.id === id;
  });
}
```

## 4. Destructuring and Spread Syntax

**Rule:** Use destructuring to access properties from objects and arrays. Use the spread syntax (`...`) for creating new objects/arrays immutably.

-   **Why?** Destructuring makes code more readable by reducing repetition and clearly stating what properties are being used. The spread syntax is the standard for immutable operations, which is critical for predictable state management in applications like React.

```javascript
// Good: Destructuring props
function UserProfile({ user, onSave }) {
  const { name, email } = user;
  // ...
}

// Good: Immutable updates with spread syntax
const updatedUser = { ...user, email: 'new.email@example.com' };
const newUsers = [...users, newUser];

// Bad: Repetitive and manual
function UserProfile(props) {
  const name = props.user.name;
  const email = props.user.email;
  // ...
}

// Bad: Direct mutation (can cause bugs in React)
user.email = 'new.email@example.com';
users.push(newUser);
```

## 5. Asynchronous Code

**Rule:** Always use `async/await` for handling promises.

-   **Why?** `async/await` provides a much cleaner, more readable syntax for asynchronous operations compared to chaining `.then()` and `.catch()`. It makes asynchronous code look and behave more like synchronous code, which is easier to follow.

```javascript
// Good: Clean, readable, and includes error handling
async function fetchUser(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    const user = await response.json();
    return user;
  } catch (error) {
    console.error('An error occurred:', error);
    // Handle the error appropriately
  }
}

// Bad: Nested and harder to read `.then()` chains
function fetchUser(userId) {
  return fetch(`/api/users/${userId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      return response.json();
    })
    .catch(error => {
      console.error('An error occurred:', error);
    });
}
```

## 6. Equality

**Rule:** Always use strict equality (`===` and `!==`).

-   **Why?** The strict equality operators do not perform type coercion. Using loose equality (`==` and `!=`) can lead to unpredictable results and bugs (e.g., `0 == false` is true).

```javascript
// Good
if (count === 10) {
  // ...
}

// Bad
if (count == '10') { // This is true, which is likely not intended
  // ...
}
```

## 7. Modules

**Rule:** Always use ES6 Modules (`import`/`export`). Do not use `require` or `module.exports`.

-   **Why?** ES6 Modules are the official standard in JavaScript and are supported by all modern browsers and tools. They allow for static analysis, which helps with optimizations like tree-shaking.
-   **Guideline:** Prefer named exports over default exports for clarity and consistency. Default exports are acceptable for the primary export of a file, such as a React component.

```javascript
// utils.js - Good: Named exports
export const formatDate = (date) => { /* ... */ };
export const formatCurrency = (amount) => { /* ... */ };

// MyComponent.js - Good: Importing
import { formatDate } from './utils.js';
import UserProfile from './UserProfile.jsx'; // Default import
```

## 8. React-Specific Rules

-   **Component Naming:** Component files and the components themselves must be named using `PascalCase` (e.g., `UserProfile.tsx`).
-   **Hooks:**
    -   All hooks must start with the word `use` (e.g., `useUserData`).
    -   Hooks must only be called at the top level of a component, not inside loops, conditions, or nested functions. The `eslint-plugin-react-hooks` linter rule enforces this.
-   **Props:** Use TypeScript to define the types for component props for excellent type safety and auto-completion.

```typescript
// Good: React component with typed props
import React from 'react';

type UserProfileProps = {
  userId: string;
};

const UserProfile = ({ userId }: UserProfileProps) => {
  // const { data, error } = useUserData(userId); // Good hook usage

  return (
    <div>
      {/* ... */}
    </div>
  );
};

export default UserProfile;
```