# Tech Stack - FactorySim Core SDK

## Context

This document outlines the technology stack for **FactorySim Core**, a Python-native SDK for designing and running high-fidelity manufacturing simulations. This stack is designed for a local, engineer-focused tool, prioritizing performance, ease of use, and code quality over web or multi-user infrastructure.

---

## 1. Core Engine & Language

This is the foundation of the SDK, responsible for all simulation and rendering.

-   **Primary Language:** **Python 3.12+**
    -   *Why:* The required language for the Genesis engine and the standard for data analysis and scripting in the engineering world.
-   **Core Simulation & Rendering Engine:** **Genesis-Embodied-AI/Genesis**
    -   *Why:* This is the heart of the tool. It provides the GPU-accelerated physics, collision detection, and photorealistic rendering that makes high-fidelity simulation possible. The SDK acts as a high-level command layer on top of Genesis.

## 2. Data & Configuration Formats

This defines how users will configure simulations and consume the results. There is no database.

-   **Configuration Format:** **YAML**
    -   *Why:* Human-readable and perfect for defining the hierarchical structure of a manufacturing cell (robots, fixtures, parts). It's easy to edit and can be version-controlled with Git.
    -   *Key Dependency:* `PyYAML`
-   **Data Output Format:** **Pandas DataFrames** (exported to **Parquet** or **CSV**)
    -   *Why:* Pandas is the standard for data analysis in Python. Exporting results (cycle times, wait times, etc.) to Parquet is highly efficient for large datasets, while CSV provides easy interoperability.
    -   *Key Dependencies:* `pandas`, `pyarrow`

## 3. Python Development & Quality Assurance

This defines the standards and tools used to build a robust, high-quality Python library.

-   **Virtual Environment:** **venv**
-   **Package Manager:** **pip** with `requirements.txt` or `pyproject.toml`
-   **Code Formatting:** **Black**
    -   *Why:* Enforces a single, consistent code style, eliminating all arguments about formatting.
-   **Import Sorting:** **isort** (or handled by Ruff)
-   **Type Checking:** **mypy**
    -   *Why:* Catches a huge class of bugs before runtime and provides excellent auto-completion for users of the SDK.
-   **Testing Framework:** **pytest**
    -   *Why:* The standard for writing clean, scalable tests in Python. Essential for validating the simulation logic.
-   **Linting:** **Ruff**
    -   *Why:* An extremely fast, all-in-one linter that enforces best practices and helps write clean, idiomatic Python.

## 4. Development Environment & CI/CD

This defines how we ensure the tool is easy to install and consistently tested.

-   **Development Environment:** **Docker**
    -   *Why:* This is critical. Genesis has complex dependencies (CUDA, specific drivers, etc.). Docker allows us to package the entire simulation environment into a container, ensuring that any engineer can get up and running with a single command, eliminating "it works on my machine" problems.
-   **CI/CD (Continuous Integration):** **GitHub Actions**
    -   *Why:* Automates the process of running tests, linting, and type-checking on every code change. This is our guarantee of quality and stability for the SDK.