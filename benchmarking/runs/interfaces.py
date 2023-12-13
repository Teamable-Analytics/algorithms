from abc import ABC


class Run(ABC):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        raise NotImplementedError
