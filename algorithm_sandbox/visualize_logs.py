from logger import Logger

class VisualizeLogs:
  def __init__(self, logger: Logger):
    self.logger = logger
    self.state_index = 0
    self.algorithm_states = [*range(0, 100)]
    self.current_algorithm_states = self.algorithm_states[self.state_index]

  def next(self):
    if self.state_index < len(self.algorithm_states):
        self.state_index += 1
        
  def prev(self):
    if self.state_index > 0:
        self.state_index -= 1
        
  def state(self):
    return self.state_index