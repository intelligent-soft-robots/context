"""
Module providing convenience classes and functions aiming at
accessing recorded ball trajectories.
It also provides method for generating ball trajectories.
"""

# for typing
from __future__ import annotations
import typing
import nptyping as npt

import random
import math
import pathlib
import h5py
import numpy as np

import o80
import pam_configuration
import tennicam_client

if int(npt.__version__[0]) >= 2:

    # from nptyping version 2.0.0, nptying.Shape has been introduced

    # 3: 3d position , Any: nb of points in trajectory
    Trajectory = npt.NDArray[npt.Shape["*, 3"], npt.Float32]

    # List of time stamps, in microseconds
    TimeStamps = npt.NDArray[
        npt.Shape["*"],
        npt.UInt,
    ]

    # List of time durations, in microseconds
    Durations = npt.NDArray[
        npt.Shape["*"],
        npt.UInt,
    ]

else:

    # 3: 3d position , Any: nb of points in trajectory
    Trajectory = npt.NDArray[(typing.Any, 3), np.float32]

    # List of time stamps, in microseconds
    TimeStamps = npt.NDArray[(typing.Any,), np.uint]

    # List of time durations, in microseconds
    Durations = npt.NDArray[(typing.Any,), np.uint]


# set of trajectories
Trajectories = typing.Sequence[Trajectory]

# trajectories and related time stamps
StampedTrajectory = typing.Tuple[TimeStamps, Trajectory]
StampedTrajectories = typing.Sequence[Trajectories]

# durations (microseconds), positions, velocities
DurationTrajectory = typing.Tuple[Durations, Trajectory, Trajectory]
DurationTrajectories = typing.Sequence[DurationTrajectory]
DurationPoint = typing.Tuple[np.uint, o80.Item3dState]


def _list_files(
    dir_path: pathlib.Path, extension: str = "", prefix: str = ""
) -> typing.List[pathlib.Path]:
    """
    Returns the list of file in dir_path of
    the specified extension and/or the specified prefix.
    """
    paths = sorted(
        [
            f
            for f in dir_path.iterdir()
            if f.is_file()
            and str(f).endswith(extension)
            and str(f.name).startswith(prefix)
        ]
    )
    return paths


def to_stamped_trajectory(input: DurationTrajectory) -> StampedTrajectory:

    """
    Converts a Duration trajectory to a stamped trajectory.
    """

    durations = input[0]
    positions = input[1]
    size = len(durations)
    stamps = np.zeros(size, np.uint)
    stamps[1:] = np.cumsum(durations[:-1])
    return stamps, positions


def to_duration_trajectory(input: StampedTrajectory) -> DurationTrajectory:
    """
    Converts a StampedTrajectories to a DurationTrajectory.
    The velocities are estimated by performing finite differences.
    """
    dt = np.diff(input[0])
    dp = np.diff(input[1], axis=0)
    velocities = (dp.T / (dt * 1e-6)).T
    positions = input[1][:-1, :]
    return dt, positions, velocities


class RecordedBallTrajectories:

    """
    Class for parsing an hdf5 file containing sets of
    recorded ball trajectories.

    The expected structure of the file is:
    To get list of time stamps (micro seconds):
    d[group name: str][index: int]["time_stamps"]
    To get related list of 3d positions:
    d[group name: str][index: int]["trajectory"]

    To ensure the hdf5 file is properly closed, it is
    adviced to use the context manager of this class
    (i.e. ```with RecordedBallTrajectories() as rbt ...```)

    Parameters
    ----------
    path: (optional)
      path to the hdf5 file. If omitted, the file at the
      default path will be used, i.e.
      ~/.mpi-is/pam/context/ball_trajectories.hdf5 or
      /opt/mpi-is/pam/context/ball_trajectories.hdf5
      (as installed by the pam_configuration package)
    file_mode: (optional)
      mode in which the h5py file will be open. The default
      is "r" (read only), which is sufficient for all the
      method provided by the class. See the subclass
      MutableRecordedBallTrajectories for methods that will
      update the file.
    """

    _TIME_STAMPS = "time_stamps"
    _TRAJECTORY = "trajectory"

    def __init__(self, path: pathlib.Path = None, file_mode: str = "r"):
        if path is None:
            path = self.get_default_path()
        self._f = h5py.File(path, file_mode)

    @staticmethod
    def get_default_path(create: bool = False) -> pathlib.Path:
        """
        Returns the default path to the file hosting all ball trajectories
        (i.e. in ~/.mpi-is/pam/context/ball_trajectories.hdf5 or
        /opt/mpi-is/pam/context/ball_trajectories.hdf5, as installed by
        the pam_configuration package).

        Parameters
        ----------
        create: optional
          create an empty file if the file does not exists at the
          default location. If create is False and the file does
          not exists, a FileNotFoundError is raised.
        """
        path = (
            pathlib.Path(pam_configuration.get_path())
            / "context"
            / "ball_trajectories.hdf5"
        )
        if not path.exists():
            if not create:
                raise FileNotFoundError(
                    "context package: failed to find the file {}".format(path)
                )
        return path

    def get_groups(self) -> typing.Tuple[str]:
        """
        Returns all the group contained by the file
        (i.e. all the sets)
        """
        return tuple(self._f.keys())

    def get_indexes(self, group: str) -> typing.Tuple[int]:
        """
        Returns all the indexes of the specified group, or
        raise a ValueError if no such group.
        """
        g = self._f[group]
        return tuple([int(index) for index in g.keys()])

    def get_stamped_trajectory(
        self, group: str, index: int, direct: bool = False
    ) -> StampedTrajectory:
        """
        Returns a the stamped trajectory, or raise a ValueError
        if no such group, or no such index in the group.
        If not direct, a tuple of h5py data instances will be
        returned (can not be accessed once the file is closed). Otherwise
        a tuple of numpy arrays is returned.
        """
        g = self._f[group][str(index)]
        # returning directly the h5py datasets
        if not direct:
            return g[self._TIME_STAMPS], g[self._TRAJECTORY]
        # converting the h5py datasets into numpy arrays
        time_stamps_dset = g[self._TIME_STAMPS]
        trajectory_dset = g[self._TRAJECTORY]
        time_stamps = np.zeros(time_stamps_dset.shape, np.uint)
        trajectory = np.zeros(trajectory_dset.shape, np.float32)
        time_stamps_dset.read_direct(time_stamps)
        trajectory_dset.read_direct(trajectory)
        return time_stamps, trajectory

    def get_stamped_trajectories(
        self, group: str, direct: bool = False
    ) -> typing.Dict[int, StampedTrajectory]:
        """
        Returns all trajectories of the group, or raise a ValueError
        if no such group.
        If not direct, a tuple of h5py data instances will be
        returned (can not be accessed once the file is closed). Otherwise
        a tuple of numpy arrays is returned.
        """
        indexes = self.get_indexes(group)
        return {
            int(index): self.get_stamped_trajectory(group, index, direct=direct)
            for index in indexes
        }

    def close(self):
        """
        Close the hdf5 file
        """
        if self._f:
            self._f.close()
            self._f = None

    def __enter__(self) -> RecordedBallTrajectories:
        """
        For the use of this class as a context manager
        which closes the hdf5.
        """
        return self

    def __exit__(self, type, value, traceback):
        """
        For the use of this class as a context manager
        which closes the hdf5.
        """
        self._f.close()
        self._f = None


class MutableRecordedBallTrajectories(RecordedBallTrajectories):
    """
    Subclass of RecordedBallTrajectories that had some method that
    will update the content of the HDF5 file. Open the file using the
    "r+" mode.
    """

    def __init__(self, path: pathlib.Path = None):
        super().__init__(path, file_mode="r+")

    def rm_group(self, group: str) -> None:
        """
        Remove the group of trajectories from the files
        if such group exists, raise a KeyError otherwise
        """
        if group not in self.get_groups():
            raise KeyError("No such group: {}".format(group))
        del self._f[group]

    def overwrite(
        self, group: str, index: int, stamped_trajectory: StampedTrajectory
    ) -> None:
        """
        Overwrite the trajectory at the given group
        and index.
        """
        g = self._f[group]
        del g[str(index)]
        traj_group = g.create_group(str(index))
        time_stamps = stamped_trajectory[0]
        positions = stamped_trajectory[1]
        traj_group.create_dataset(self._TIME_STAMPS, data=time_stamps)
        traj_group.create_dataset(self._TRAJECTORY, data=positions)

    def add_tennicam_trajectories(
        self, group_name: str, tennicam_path: pathlib.Path
    ) -> None:
        """
        It is assumed that tennicam_path is a directory hosting (non recursively)
        a collection of files named tennicam_* that have been generated by the
        executable tennicam_client_logger (package tennicam_client). This function
        will parse all these files and add them to the hdf5 under the specified
        group name (or raise a FileNotFoundError if tennicam_path does not
        exists).

        Returns
        -------
        The number of trajectories added to the file.
        """

        def _read_trajectory(tennicam_file: pathlib.Path) -> StampedTrajectory:
            """
            Parse the file and returned the corresponding
            stamped trajectory.
            """
            time_stamps = []
            trajectory = []
            start_time = None
            for ball_id, time_stamp, position, _ in tennicam_client.parse(
                tennicam_file
            ):
                if ball_id >= 0:
                    time_stamp = int(time_stamp * 1e-3)  # from nano to micro seconds
                    if start_time is None:
                        start_time = time_stamp
                    time_stamp -= start_time
                    time_stamps.append(time_stamp)
                    trajectory.append(position)
            return np.array(time_stamps, np.uint), np.array(trajectory, np.float32)

        def _read_folder(tennicam_path: pathlib.Path) -> StampedTrajectories:
            """
            List all the file in tennicam_path that have the tennicam_ prefix,
            parse them and returns the corresponding list of stamped trajectories.
            """
            files = _list_files(tennicam_path, prefix="tennicam_")
            stamped_trajectories = [_read_trajectory(tennicam_path / f) for f in files]
            return stamped_trajectories

        def _save_trajectory(
            group: h5py._hl.group.Group,
            index: int,
            stamped_trajectory: StampedTrajectory,
        ):
            """
            Create in the group a new subgroup named according to the index
            and add to it 2 datasets, "time_stamps" (list of microseconds
            time stamps) and "trajectory" (list of corresponding 3d positions)
            """
            # creating a new group for this trajectory
            traj_group = group.create_group(str(index))
            # adding 2 datasets: time_stamps and positions
            time_stamps = stamped_trajectory[0]
            positions = stamped_trajectory[1]
            traj_group.create_dataset(self._TIME_STAMPS, data=time_stamps)
            traj_group.create_dataset(self._TRAJECTORY, data=positions)

        # reading all trajectories present in the directory
        stamped_trajectories = _read_folder(tennicam_path)

        # adding the new group to the hdf5 file
        group = self._f.create_group(group_name)

        # adding all trajectories as datasets to this group
        for index, stamped_trajectory in enumerate(stamped_trajectories):
            _save_trajectory(group, index, stamped_trajectory)

        return len(stamped_trajectories)

    def add_json_trajectories(
        self, group_name: str, json_path: pathlib.Path, sampling_rate_us: int
    ) -> int:
        """
        It is assumed that json_path is a directory hosting (non recursively)
        a collection of files named *.json. Each file host the (string) representation
        of a dictionary with the key "ob" associated to an list of a 6d array (3d
        position and 3d velocities).
        This function will parse all these files and add them to the hdf5 under the
        specified group name (or raise a FileNotFoundError if json_path does not
        exists). (note: the velocities values are ignored, and the time stamp list
        is created based on the sampling rate)

        Returns
        -------
        The number of trajectories added to the file.
        """

        def _read_trajectory(json_file: pathlib.Path) -> Trajectory:
            """
            Parse the json file and return the trajectory it
            hosts.
            """
            with open(json_file, "r") as f:
                content = f.read()
            content = content.strip()
            content = eval(content)
            trajectory = np.array(content["ob"], np.float32)[
                :, :3
            ]  # keeping only the position
            return trajectory

        def _read_folder(json_path: pathlib.Path) -> Trajectories:
            """
            List the json files that are at the root of the path,
            parse them and return the corresponding trajectories.
            """
            trajectories = [
                _read_trajectory(json_path / f) for f in _list_files(json_path, ".json")
            ]
            return trajectories

        def _save_trajectory(
            group: h5py._hl.group.Group, index: int, trajectory: Trajectory
        ):
            """
            Create under the group a new subgroup named after the index,
            and add 2 datasets, "time_stamps" (list of time stamps in
            micro seconds inferred using the sample rate) and
            "trajectory", the corresponding list of 3d positions.
            """
            # creating a new group for this trajectory
            traj_group = group.create_group(str(index))
            # inferring time stamps
            time_stamps = np.array(
                [i * sampling_rate_us for i in range(trajectory.shape[0])], np.int32
            )
            # adding 2 datasets: time_stamps and positions
            traj_group.create_dataset(self._TIME_STAMPS, data=time_stamps)
            traj_group.create_dataset(self._TRAJECTORY, data=trajectory)

        # reading all trajectories present in the directory
        trajectories = _read_folder(json_path)

        # adding the new group to the hdf5 file
        group = self._f.create_group(group_name)

        # adding all trajectories as datasets to this group
        for index, trajectory in enumerate(trajectories):
            _save_trajectory(group, index, trajectory)

        return len(trajectories)


class BallTrajectories:
    """
    Convenience wrapper over a hdf5 file which contains
    sets ("groups") of ball trajectories.

    The constructor loads a group of trajectories in the memory,
    and methods provide convenience functions to access them.

    A trajectory is tuple of two lists, one with time stamps
    (in microseconds) and one with related 3d positions.

    Parameters
    ----------
    group:
      name of the group of trajectories to load
    hdf5_path: optional
      absolute path to the hdf5 file to load. If None,
      the default file will be used (i.e. either
      ~/.mpi-is/pam/context/ball_trajectories.hdf5 or
      /opt/mpi-is/pam/context/ball_trajectories.hdf5
    """

    def __init__(self, group: str, hdf5_path: pathlib.Path = None):
        if hdf5_path is None:
            hdf5_path = RecordedBallTrajectories.get_default_path()

        self._path: pathlib.Path = hdf5_path

        with RecordedBallTrajectories(hdf5_path) as rbt:
            self._data: typing.Dict[
                int, StampedTrajectories
            ] = rbt.get_stamped_trajectories(group, direct=True)

    def size(self) -> int:
        """
        Returns the number of trajectories that have been loaded.
        """
        return len(self._data)

    def get_all_trajectories(self) -> typing.Dict[int, StampedTrajectories]:
        """
        Returns a dictionary with key the index of the trajectory and
        the trajectories as values.
        """
        return self._data

    def get_trajectory(self, index: int) -> StampedTrajectory:
        """
        Returns the trajectory at the requested index.
        """
        return self._data[index]

    def random_trajectory(self) -> StampedTrajectory:
        """
        Returns one of the trajectory, randomly selected.
        """
        index = random.choice(list(range(len(self._data.keys()))))
        return self._data[index]

    def get_different_random_trajectories(
        self, nb_trajectories: int
    ) -> StampedTrajectories:
        """
        Returns a list of trajectories, randomly
        ordered and selected.
        """
        if nb_trajectories > self.size():
            raise ValueError(
                "BallTrajectories: only {} trajectories "
                "available ({} requested)".format(
                    len(self._trajectories), nb_trajectories
                )
            )
        indexes = list(self._data.keys())
        random.shuffle(indexes)
        return [self._data[index] for index in indexes[:nb_trajectories]]

    @staticmethod
    def to_duration(input: StampedTrajectory) -> DurationTrajectory:
        """
        Returns a corresponding duration trajectory
        """
        return to_duration_trajectory(input)

    @classmethod
    def iterate(cls, input: StampedTrajectory) -> typing.Generator[DurationPoint]:
        """
        Generator over the trajectory.
        Yields tuples (duration in microseconds, state), state having
        a position and a velocity attribute.
        """
        durations, positions, velocities = cls.to_duration(input)
        for d, p, v in zip(durations, positions, velocities):
            yield d, o80.Item3dState(p, v)
        return


def velocity_line_trajectory(
    start: typing.Sequence[float],
    end: typing.Sequence[float],
    velocity: float,
    sampling_rate: float = 0.01,
) -> DurationTrajectory:

    """
    Start and end being n dimentional points, velocity
    a float value (meter per seconds) and the sampling
    rate between two points (in seconds), returns duration
    trajectory corresponding to a point going from
    start to end at the given velocity
    """

    # vector between end and start
    vector = [e - s for e, s in zip(end, start)]

    # distance between end and start
    distance = math.sqrt(sum([v**2 for v in vector]))

    # duration of motion between start and end,
    # at constant velocity
    duration = distance / velocity

    # the velocity vector
    velnd = np.array([v / duration for v in vector], np.float32)

    # discrete number of steps to go from start
    # to end at given speed and sampling rate
    nb_steps = int((duration / sampling_rate) + 0.5)

    # displacement vector of one step
    step = [v / nb_steps for v in vector]

    # creating the trajectory, translating
    # one displacement vector per step
    point = start
    positions = []
    for cstep in range(nb_steps):
        point = [p + s for p, s in zip(point, step)]
        positions.append(np.array(point, np.float32))
    positions = np.array(positions, np.float32)
    velocities = np.array([velnd] * len(positions), np.float32)

    # durations in microseconds
    durations = np.array([int(sampling_rate * 1e6)] * nb_steps)

    # returning the trajectory
    return durations, positions, velocities


def duration_line_trajectory(
    start: typing.Sequence[float],
    end: typing.Sequence[float],
    duration_ms: float,
    sampling_rate: float = 0.01,
) -> DurationTrajectory:

    """
    Start and end being n dimentional points, duration
    a float value (milliseconds) and the sampling
    rate between two points (in seconds), returns duration
    trajectory corresponding to a point going from
    start to end over the provided duration
    """

    # vector between end and start
    vector = [e - s for e, s in zip(end, start)]

    # duration of motion between start and end,
    # at constant velocity
    duration = duration_ms / 1000.0

    # the velocity vector
    velnd = np.array([v / duration for v in vector], np.float32)

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
    positions = []
    for cstep in range(nb_steps):
        point = [p + s for p, s in zip(point, step)]
        positions.append(np.array(point, np.float32))
    positions = np.array(positions, np.float32)
    velocities = np.array([velnd] * len(positions), np.float32)

    # durations in microseconds
    durations = np.array([int(sampling_rate * 1e6)] * nb_steps)

    # returning the trajectory
    return durations, positions, velocities
