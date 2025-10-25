import os
import json
from argparse import ArgumentParser


from chanina.utils import log
from chanina.core.bootstrapper import Bootstrapper
from chanina.core.chanina import ChaninaApplication

from uvicorn.importer import import_from_string, ImportFromStringError


def import_workflow_file(path: str) -> dict:
    """ This makes sure the workflow file is a valid json, and returns its content. """
    workflow = None
    if os.path.exists(path) and os.path.isfile(path):
        try:
            with open(path, "r") as f:
                workflow = json.load(f)
        except json.JSONDecodeError as e:
            log(f"[Runner] Error decoding the workflow file : {e}")
    else:
        raise FileNotFoundError(f"[Runner] '{path}' does not exist or is not a file.")
    if not workflow:
        raise ValueError("[Runner] The workflow file is empty")
    return workflow 


def import_application_object(path: str) -> ChaninaApplication:
    try:
        chanina_app = import_from_string(path)
    except ImportFromStringError as e:
        log(f"The specified app path is incorrect: {e}")
        raise e

    if not isinstance(chanina_app, ChaninaApplication):
        raise TypeError(
            f"{chanina_app} is not a valid ChaninaApplication object. ({type(chanina_app)})"
        )
    return chanina_app


def import_arguments(arguments: list[str]):
    """
    Parse the list of nargs passed to the cli and makes it a dict of args.
    nargs needs to be passed in the format: -r key=value key2=value2.
    Exceptions are raised if anything is not correct.
    """
    args = {}
    if not arguments:
        return args

    for kv in arguments:
        if not "=" in kv:
            continue
        k, v = kv.split("=")
        if not k or not v:
            raise ValueError(f"Arguments passed for flag '-r' but could not be turned into a valid dict. ({kv})")
        args[k] = v

    if not args:
        raise KeyError("Arguments passed for flag '-r' got parsed into an empty dictionnary.")

    return args


def add_arguments(argparser: ArgumentParser):
    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("workflow", nargs="?", type=str)
    argparser.add_argument(
        "--app",
        "-a",
        help="Path of the ChaninaApplication's instance. (format: 'module.module:app')",
        required=True,
        type=str
    )
    group.add_argument(
        "--task",
        "-t",
        help="Only runs the task specified here. (identifier only)",
        required=False,
        default="",
        type=str
    )
    argparser.add_argument(
        "--number_of_runs",
        "-n",
        help="How many times the task/workflow will be ran.",
        default=1,
        type=int
    )
    argparser.add_argument(
        "--arguments",
        "-r",
        help="Only in -t mode. Additionnal args to pass to the task. Warning: similar keys in the workflow will be overwritten.",
        nargs="*"
    )


class Runner:
    def __init__(
        self,
        app: ChaninaApplication,
        workflow: dict | None,
        task_identifier: str = "",
        number_of_runs: int = 1,
        additionnal_args: dict = {}
    ) -> None:
        self.app = app
        self.workflow = workflow
        self.task_identifier = task_identifier
        self.bootstrapper = Bootstrapper(
            self.app.features, workflow
        ) if workflow else None
        self.number_of_runs = number_of_runs
        self.additionnal_args = additionnal_args

        self._last_task_ids = []

    @property
    def last_task_ids(self):
        return self._last_task_ids

    def run(self):
        if self.workflow:
            self._run_workflow()
        else:
            self._run_task()

    def _run_task(self):
        feature = self.app.features[self.task_identifier]
        task = feature.task.s(args=self.additionnal_args)
        self._last_task_ids.append(task.apply_async())

    def _run_workflow(self):
        if not self.bootstrapper:
            raise Exception("Failed to run because no Bootstrapper was initialized.")
        self.bootstrapper.build()
        if not self.bootstrapper._built or not self.bootstrapper.sequence:
            raise Exception("[Runner] Can't run a sequence that the bootstrapper did not build.")

        for _ in range(self.number_of_runs):
            if self.task_identifier in self.bootstrapper.sequencer.registry:
                task = self.bootstrapper.sequencer.registry[self.task_identifier]
                task.kwargs["args"].update(self.additionnal_args)
                self._last_task_ids.append(
                    task.apply_async()
                )
            else:
                for sequence in self.bootstrapper.sequence:
                    self._last_task_ids.append(sequence.apply_async())


def run():
    # Handle the arguments for the run metadatas.
    argparser = ArgumentParser()
    add_arguments(argparser)
    args = argparser.parse_args()

    workflow_file = args.workflow
    task_identifier = args.task
    number_of_runs = args.number_of_runs
    app_path = args.app
    arguments_as_list = args.arguments

    # Transform arguments data into the needed components for the run.
    arguments = import_arguments(arguments_as_list)
    app = import_application_object(app_path)
    workflow = import_workflow_file(workflow_file) if workflow_file else None

    # Create a runner
    runner = Runner(app, workflow, task_identifier, number_of_runs, arguments)
    runner.run()


if __name__ == "__main__":
    run()
