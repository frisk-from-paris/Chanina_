from typing import Any, Callable
import celery


class ChaninaTask(celery.Task):
    """
    Base class for Tasks used by the Chanina app.
    This class is meant to be inherited from for user's implementation of specific
    base Tasks.
    """
    ...


class Feature:
    """
        The Feature object is the interface that allows users to create a function with
        access to the playwright context that can be treated as a celery Task.
        The base_task argument is a the base class for the celery task, and the config argument
        is a key/value object that is unwrapped in the task's decorator.
        'args' is passed to the actual function of the feature.
    """
    def __init__(
        self,
        app,
        func: Callable,
        feature_id: str,
        args: dict = {},
        config: dict = {},
        bind: bool = False,
        base_task: Any = ChaninaTask
    ) -> None:
        self.app = app
        self.func = func
        self.bind = bind
        self.args = args
        self.config = config
        self.feature_id = feature_id
        self.base_task = base_task
        self.task = self._register_as_task()

    def _register_as_task(self):
        """ register the feature as a celery task. """
        @self.app.celery.task(
            name=self.feature_id,
            base=self.base_task,
            bind=self.bind,
            **self.config
        )
        def _task(task = None, **kwargs):
            if task:
                return self.func(task, self.app.worker_session, kwargs["args"])
            return self.func(self.app.worker_session, kwargs["args"])
        return _task
