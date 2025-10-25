from chanina.utils import log
from chanina.core.chanina import Feature

from celery import chain, group


class Sequencer:
    """ The sequencer is maintaining the current sequence being bootstrapped. """
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


class Bootstrapper:
    """
    The Bootstrapping is the process where the workflow and features are turned into a sequence 
    of celery 'chains' or 'groups' that can be ran by the Runner.
    """
    def __init__(self, features: dict[str, Feature], workflow: dict) -> None:
        self.features = features
        self.workflow = workflow
        self._sequencer = Sequencer()
        self._built = False
    
    @property
    def built(self):
        return self._built

    @property
    def sequencer(self):
        return self._sequencer

    @property
    def sequence(self):
        if not self.built:
            log(f"[Bootstrapper] Trying to access sequence before the bootstrapper has been built.")
            return []
        return self._sequencer.sequence

    def build(self):
        """
        The build process is creating a sequence of chains and groups.
        When a step is a 'chain' 'flow_type', it is added to a chain list.
        Whenever another a step has another 'flow_type', the chain list is appended
        to the sequence, and a new list is created to append the other 'flow_type',
        etc.
        """
        if self.built:
            raise Exception("You cannot build a Bootstrapper more than once.")
        for step in self.workflow["steps"]:
            feature = self.features.get(step["identifier"])
            if not feature:
                log(f"[Bootstrapper] {step['identifier']} is not implemented.")
                continue
            # If the step needs multiple instances we build it here.
            if step["identifier"] in self.workflow["instances"]:
                for instance in self.workflow["instances"][step["identifier"]]:
                    print(instance)
                    # 'instances' are dicts of args with which we re-run the task.
                    self._sequencer.add(step, feature, instance)
            # Otherwise we build the task here.
            else:
                # 'step' is passed as 'args' cause it does contain the args at the key 'args'.
                self._sequencer.add(step, feature, step)
        self._sequencer.flush()
        self._built = True
