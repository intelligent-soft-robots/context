import os, random, math, o80_pam, pathlib
from context_wrp import State
from scipy import interpolate


# return abs path to src/context/trajectories
def ball_trajectories_folder():
    return "/opt/mpi-is/context/trajectories"

def _read_trajectory(file):
    if ".json" in file:
        return _read_trajectory_json(file)
    elif ".log" in file:
        return _read_trajectory_o80_log(file)
    else:
        raise NotImplementedError("File format not supported for" + file)

def _read_trajectory_json(json_file):
    with open(json_file, "r") as f:
        content = f.read()
    content = content.strip()
    d = eval(content)["ob"]
    # State : wrapped over from include/context/state.hpp
    # can be serialized for interprocess communication
    states = [State(p[:3], p[3:]) for p in d]
    return states

def _read_trajectory_o80_log(log_file):
    log_file = pathlib.Path(log_file)
    d = list(o80_pam.robot_ball_parser.parse(log_file))
    # State : wrapped over from include/context/state.hpp
    # can be serialized for interprocess communication
    states = [State(p[0][2], p[0][3]) for p in d]
    return states


class BallTrajectories:

    # below : sampling rate ms of 10 :
    # sampling rate at which the trajectories
    # were recorded

    def __init__(self, sampling_rate_ms=10):
        path = ball_trajectories_folder()
        self._files = sorted(
            [
                f
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f)) and (f.endswith(".json") or f.endswith(".log"))
            ]
        )
        self._trajectories = [_read_trajectory(path + os.sep + f) for f in self._files]
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
    
    def get_trajectory_random_rotation(self, index, rotation_range):

        """
        Rotate trajectory counterclockwise by a given angle (in degree) around it's first position.
        """

        rotation_range_radians = rotation_range * math.pi / 180
        angle = (random.random()-0.5) * rotation_range_radians
        len_trajectory = len(self._trajectories[index])

        origin_x, origin_y, _ = self._trajectories[index][0].position

        trajectory_rotated = [State([
                origin_x + math.cos(angle) * (p_x - origin_x) - math.sin(angle) * (p_y - origin_y),
                origin_y + math.sin(angle) * (p_x - origin_x) + math.cos(angle) * (p_y - origin_y),
                p_z],[
                math.cos(angle) * v_x - math.sin(angle) * v_y,
                math.sin(angle) * v_x + math.cos(angle) * v_y,
                v_z])
            for (p_x, p_y, p_z),(v_x, v_y, v_z) in
                [(self._trajectories[index][i].position,self._trajectories[index][i].velocity)
                for i in range(len_trajectory)]]

        return trajectory_rotated

    def random_trajectory_random_rotation(self, rotation_range):
        index = random.choice(list(range(len(self._trajectories))))
        return index, self.get_trajectory_random_rotation(index, rotation_range)

    def get_trajectory_interpolate_time(self, index, fac):
        len_traj = len(self._trajectories[index])

        interpol_traj_func_pos = interpolate.interp1d(list(range(len_traj)), [self._trajectories[index][i].position for i in range(len_traj)], axis=0)
        interpol_traj_func_vel = interpolate.interp1d(list(range(len_traj)), [self._trajectories[index][i].velocity for i in range(len_traj)], axis=0)

        trajectory_interpolated = [State(interpol_traj_func_pos(pos*fac), interpol_traj_func_vel(pos*fac))
            for pos in range(int((len_traj-1)/fac+1))]
        
        return trajectory_interpolated

    def random_trajectory_interpolated_time(self, fac):
        index = random.choice(list(range(len(self._trajectories))))
        return index, self.get_trajectory_interpolate_time(index, fac)        


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

