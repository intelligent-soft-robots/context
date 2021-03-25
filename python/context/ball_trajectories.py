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
        

def line_trajectory(start,end,velocity,sampling_rate=0.01):

    '''
    start and end being n dimentional points, velocity
    a float value (meter per seconds) and the sampling
    rate between two points, returns a list of instance
    of States corresponding to a point going from 
    start to end at the given velocity
    '''

    # vector between end and start
    vector = [e-s for e,s in zip(end,start)]

    # distance between end and start
    distance = math.sqrt(sum([v**2 for v in vector]))

    # duration of motion between start and end,
    # at constant velocity
    duration = distance/velocity

    # the velocity vector
    velnd = [v/duration for v in vector]

    # discrete number of steps to go from start
    # to end at given speed and sampling rate
    nb_steps = int ( (duration/sampling_rate) + 0.5 )

    # displacement vector of one step 
    step = [v/nb_steps for v in vector]

    # creating the trajectory, translating
    # one displacement vector per step
    point = end
    states = []
    for _ in range(nb_steps):
        point = [p+s for p,s in zip(point,step)]
        states.append(State(point,velnd))

    # returning the trajectory
    return states
    
