# Chanina

**Chanina** is a Python application to automate and orchestrate Playwright sessions using a **Celery-based task system**. It provides a workflow manager, a shared context between tasks, and utilities to interact programmatically with web pages. A **CLI** is also available to run workflows or tasks from the terminal.

---

## Features

- **Playwright session management**: `WorkerSession` shares the Playwright context, pages, and utility tools among all tasks within the same worker.  
- **Celery task system**: create, register, and execute reusable tasks using the `@feature` decorator.  
- **Complex workflows**: support for chains and groups of tasks, with sequences managed automatically.  
- **DOM navigation and manipulation**: navigate pages, wait for elements, interact with forms, or accept cookies.  
- **CLI**: run workflows or tasks from the terminal.  
- **Isolated browser profiles**: manage profiles to prevent conflicts between workers.  

---

## Installation

```bash
git clone <REPO_URL>
cd <REPO_NAME>
poetry install
```

---

## Running Celery Workers

```bash
celery -A chanina_app.celery_app worker --loglevel=info
```

---

## Usage

### Register tasks with Celery  

```python
@app.feature("my_task")
def do_something(session):
    # session is the shared WorkerSession containing the current page and utilities
    page = session.new_page()
    session.goto(page, "https://example.com")
    session.close_page(page)
```

### Create and manage pages  

```python
page = app.new_page()
app.goto(page, "https://example.com")
app.close_page(page)
```

### Execute workflows  

```python
workflow = app.import_workflow_file("workflow.json")
app.flush(workflow)  # adds tasks to the worker's current sequence
```

### Use the CLI  

```bash
chanina-runner run-workflow workflow.json
chanina-runner run-task my_task
```

---

## Modules and Utilities

- **_meta_tools.py**: utility functions for handling URLs and Playwright locators.  
- **navigate.py**: navigation, scrolling, waiting for DOM elements or cookies.  
- **Interact & Filters**: interact with pages (click, fill forms, filter elements).  

---

## Contributing

1. Clone the repository and install dependencies.  
2. Add new features or tests in dedicated modules.  
3. Document your functions with docstrings.  
4. Submit your changes via Pull Request.  

---

## License

Specify your project license here (MIT, GPL, etc.).

