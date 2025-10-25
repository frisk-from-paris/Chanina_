# Chanina

**Chanina** is a Python application to automate and orchestrate Playwright sessions using a **Celery-based task system**.
It provides a workflow manager, a shared context between tasks, and utilities to interact programmatically with web pages.
A **CLI** is also available to run workflows or tasks from the terminal.

This aims at transforming what is often a tedious and imprecise process, to a more scalable, developper friendly and robust
part of your tests suite.

---

## Features

- **Playwright session management**: `WorkerSession` shares the Playwright context, pages, and utility tools among all tasks within the same worker.
- **Celery task system**: create, register, and execute reusable tasks using the `@feature` decorator.
- **Complex workflows**: support for chains and groups of tasks, with sequences managed automatically.
- **Smart tools for Playwright**: navigate, inspect, interact and wait modules gathers methods.
- **CLI**: run workflows or tasks from the terminal.
- **Isolated browser profiles**: manage profiles to prevent conflicts between workers and the main playwright process.

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
celery -A sub_module.module:celery_app worker --loglevel=info
```

---

## Usage

### Register tasks with Celery  

```python
@app.feature("my_task")
def do_something(session: WorkerSession, args: dict):
    # session is the shared WorkerSession containing the current page and utilities
    page = session.new_page()
    session.goto(page, "https://example.com")
    session.close_page(page)
```
The first parameter of the feature's function always is the WorkerSession object.
!! Except when making a 'bind=True' parameter for the task, in which case the first parameter
is the instance of the class.

### Create and execute workflows  

A workflow is a json file in which you can construct a sequence of tasks and specifies arguments.
The workflow has two main keys : 'steps' and 'instance'.

- The 'steps' section are the features you want to use in your workflow ordered and with the arguments specified.

- The 'instancce' section is where you can specified if a 'step' defined in the other section needs multiple instances.

If you have a 'extract_html' feature, and you add it in your workflow, you can add as much instance of it as you need page
to extract_html from, passing the page url in the 'args' key.

- Every step has a 'flow_type' argument, that can be 'chain' or 'group', and will determine the kind of celery task it will be.

**NOTE**

The sequence is built in the order of the steps in the file.
'group' task will be run FIRST and are non blocking for the rest of the sequence.
In the workflow example underneath, we can imagine that the flow_type 'group' of the task 'save_to_mongodb' is because the task
is a while loop running in parallel which saves in the db what the 'check_post' task is parsing.


Here is an example of a workflow file :

```json
{
  "steps": [
    {
      "identifier": "login_to_platform",
      "args": {"password": $PASSWORD, "username": "Joseph S"},
      "flow_type": "chain"
    },
    {
      "identifier": "check_post",
      "flow_type": "chain"
    },
    {
      "identifier": "save_in_mongodb",
      "args": {"user": "mongo_user", "pw": $MONGOPASSWORD, "host": "localhost", "port": 27017},
      "flow_type": "group"
    }

  ],
  "instances": {
    "check_post": [
      {
        "args": {
            "post_url": "https://instagram.com/p/publication1
        }
      },
      {
        "args": {
            "post_url": "https://instagram.com/p/publication2
        }
      },
      {
        "args": {
            "post_url": "https://instagram.com/p/publication3
        }
      }
    ]
  }
}
```

### Use the CLI  

Tasks can be ran with the CLI, please use 'poetry run cli --help' to learn more.

```bash
    $ poetry run cli login_workflow.json --app login_process.app:celery --arguments password=$PASSWORD username=$USERNAME
```

You can also manually run a task if your worker is still up

```bash
    $ poetry run cli --task check_post --app login_process.app:celery --arguments post_url="https://www.instagram.com/p/another-publication-not-in-the-workflow"
```

---

## License

For now this project has no Licence, i'm working on it.

