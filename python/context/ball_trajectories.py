import os, random, math, pathlib
import pam_configuration
from context_wrp import State


# return abs path to src/context/trajectories
def ball_trajectories_folder()->pathlib.Path:
    path = pathlib.Path(pam_configuration.get_path()) / "context" / "ball_trajectories"
    if not path.exists():
        raise FileNotFoundError("context package: failed to find context/ball_trajectories"
                                "in ",pam_configuration.get_path())
    return path

def _read_trajectory(json_file):
    with open(json_file, "r") as f:
        content = f.read()
    content = content.strip()
    d = eval(content)["ob"]
    # State : wrapped over from include/context/state.hpp
    # can be serialized for interprocess communication
    states = [State(p[:3], p[3:]) for p in d]
    return states


class BallTrajectories:

    # below : sampling rate ms of 10 :
    # sampling rate at which the trajectories
    # were recorded

    def __init__(self, sampling_rate_ms=10):
        path = ball_trajectories_folder()
        self._files = sorted(
            [
                pathlib.Path(f)
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f)) and f.endswith(".json")
            ]
        )
        self._trajectories = [_read_trajectory(path / f) for f in self._files]
        self._sampling_rate_ms = sampling_rate_ms
        
    def size(self):
        return len(self._files)

    def get_sampling_rate_ms(self):
        return self._sampling_rate_ms

    def get_all_trajectories(self):
        return self._trajectories

    def print_index_files(self):
        for index, name in enumerate(self._files):
            print(index, name)

    def get_file_name(self, index):
        return self._files[index]

    def get_trajectory(self, index):
        try:
            return self._trajectories[index]
        except IndexError:
            error = "context.BallTrajectories: incorrect trajectory index {}."
            error += " Max index: {}"
            raise IndexError(error.format(index, len(self._trajectories) - 1))

    def random_trajectory(self):
        index = random.choice(list(range(len(self._trajectories))))
        trajectory = self._trajectories[index]
        return index, trajectory

    def get_different_random_trajectories(self, nb_trajectories):
        if nb_trajectories > len(self._trajectories):
            raise ValueError(
                "BallTrajectories: only {} trajectories "
                "available ({} requested)".format(
                    len(self._trajectories), nb_trajectories
                )
            )
        random.shuffle(self._trajectories)
        return self._trajectories[:nb_trajectories]


def velocity_line_trajectory(start, end, velocity, sampling_rate=0.01):

    """
    start and end being n dimentional points, velocity
    a float value (meter per seconds) and the sampling
    rate between two points, returns a list of instance
    of States corresponding to a point going from
    start to end at the given velocity
    """

    # vector between end and start
    vector = [e - s for e, s in zip(end, start)]

    # distance between end and start
    distance = math.sqrt(sum([v ** 2 for v in vector]))

    # duration of motion between start and end,
    # at constant velocity
    duration = distance / velocity

    # the velocity vector
    velnd = [v / duration for v in vector]

    # discrete number of steps to go from start
    # to end at given speed and sampling rate
    nb_steps = int((duration / sampling_rate) + 0.5)

    # displacement vector of one step
    step = [v / nb_steps for v in vector]

    # creating the trajectory, translating
    # one displacement vector per step
    point = start
    states = []
    for cstep in range(nb_steps):
        point = [p + s for p, s in zip(point, step)]
        states.append(State(point, velnd))

    # returning the trajectory
    return states


def duration_line_trajectory(start, end, duration_ms, sampling_rate=0.01):

    """
    start and end being n dimentional points, duration
    a float value (milliseconds) and the sampling
    rate between two points, returns a list of instance
    of States corresponding to a point going from
    start to end over the provided duration
    """

    # vector between end and start
    vector = [e - s for e, s in zip(end, start)]

    # distance between end and start
    distance = math.sqrt(sum([v ** 2 for v in vector]))

    # duration of motion between start and end,
    # at constant velocity
    duration = duration_ms / 1000.0

    # the velocity vector
    velnd = [v / duration for v in vector]

    # discrete number of steps to go from start
    # to end at given speed and sampling rate
    nb_steps = int((duration / sampling_rate) + 0.5)
    if nb_steps == 0:
        nb_steps = 1

    # displacement vector of one step
    step = [v / nb_steps for v in vector]

    # creating the trajectory, translating
    # one displacement vector per step
    point = start
    states = []
    for cstep in range(nb_steps):
        point = [p + s for p, s in zip(point, step)]
        states.append(State(point, velnd))

    # returning the trajectory
    return states
