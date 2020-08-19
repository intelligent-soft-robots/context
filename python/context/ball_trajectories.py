import os
from context_wrp import State

def _read_trajectory(json_file):
    with open(json_file,"r") as f:
        content = f.read()
    content = content.trim()
    d = eval(content)["obj"]
    states = [State(p[:3],p[3:])
              for p in d]
    return states

class BallTrajectories:

    def __init__(self,path):
        files = [ f
                  for f in os.listdir(path)
                  if os.path.isfile(os.path.join(path, f))
                  and f.endswith(".json")]

        self._trajectories = [ _read_trajectory(f)
                               for f in files ]
