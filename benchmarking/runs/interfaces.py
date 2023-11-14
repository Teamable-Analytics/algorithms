from abc import ABC


class Run(ABC):
    @staticmethod
    def start(num_trials: int = 10, generate_graphs: bool = True):
        raise NotImplementedError
