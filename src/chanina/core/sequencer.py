from celery import chain, group

from chanina.core.chanina import Feature


class Sequencer:
    def __init__(self) -> None:
        self.init()

    def init(self):
        self.chain_tasks = []
        self.group_tasks = []
        self.current_sequence = []
        self.registry = {}
        self._sequence = None
        self.previous_flow_type = None

    @property
    def sequence(self):
        return self._sequence

    def add(self, step: dict, feature: Feature, instance: dict = {}):
        name = step["identifier"]
        flow_type = step["flow_type"]
        args = instance.get("args", {})

        # flush if changing flow_type
        if self.previous_flow_type and flow_type != self.previous_flow_type:
            if self.previous_flow_type == "chain" and self.chain_tasks:
                self.current_sequence.append(chain(self.chain_tasks.copy()))
                self.chain_tasks = []
            elif self.previous_flow_type == "group" and self.group_tasks:
                self.current_sequence.append(group(self.group_tasks.copy()))
                self.group_tasks = []

        # add task to its list
        task = feature.task.si(args=args)

        if flow_type == "chain":
            self.chain_tasks.append(task)
        elif flow_type == "group":
            self.group_tasks.append(task)
        else:
            raise Exception(f"{flow_type} unrecognized flow_type.")
        
        self.registry[name] = task
        self.previous_flow_type = flow_type

    def flush(self):
        """ When the sequence has been built, flushing it means adding the reminder tasks
        to the current_sequence. """
        if self.chain_tasks:
            self.current_sequence.append(chain(self.chain_tasks.copy()))
            self.chain_tasks = []
        if self.group_tasks:
            self.current_sequence.append(group(self.group_tasks.copy()))
            self.group_tasks = []
        self._sequence = tuple(self.current_sequence)

    def __repr__(self) -> str:
        return f"Sequencer<Chain{self.chain_tasks}, Group{self.group_tasks}, CurrentSequence{self.current_sequence}>"
