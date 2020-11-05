import os
import random
from context_wrp import State



# return abs path to src/context/trajectories
def ball_trajectories_folder():
    return "/opt/mpi-is/context/trajectories"
                   

def _read_trajectory(json_file):
    with open(json_file,"r") as f:
        content = f.read()
    content = content.strip()
    d = eval(content)["ob"]
    # State : wrapped over from include/context/state.hpp
    # can be serialized for interprocess communication
    states = [State(p[:3],p[3:])
              for p in d]
    return states


class BallTrajectories:

    def __init__(self):
        path = ball_trajectories_folder()
        self._files = sorted([ f
                  for f in os.listdir(path)
                  if os.path.isfile(os.path.join(path, f))
                  and f.endswith(".json") ])
        self._trajectories = [ _read_trajectory(path+os.sep+f)
                               for f in self._files ]

    def print_index_files(self):
        for index,name in enumerate(self._files):
            print(index,name)
        
    def get_file_name(self,index):
        return self._files[index]
        
    def get_trajectory(self,index):
        try :
            return self._trajectories[index]
        except IndexError:
            error = "context.BallTrajectories: incorrect trajectory index {}."
            error += " Max index: {}"
            raise IndexError(error.format(index,len(self._trajectories)-1))
        
    def random_trajectory(self):
        index = random.choice(list(range(len(self._trajectories))))
        trajectory = self._trajectories[index]
        return index,trajectory
        
