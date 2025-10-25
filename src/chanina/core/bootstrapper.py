from chanina.utils import log
from chanina.core.chanina import Feature
from chanina.core.sequencer import Sequencer


class Bootstrapper:
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
