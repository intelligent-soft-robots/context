import h5py
import pathlib
import pytest
import numpy as np
from context import ball_trajectories as bt


# configuration of the stamped_trajectory fixture
_START_POSITION = (1.0, 2.0, 1.0)
_END_POSITION = (3.0, 4.0, 1.0)
_VELOCITY = 0.5
_SAMPLING_RATE = 0.01

# configuration for working_directory fixture
_NB_JSONS = 3
_JSON_FILES = ["{}.json".format(i) for i in range(_NB_JSONS)]
_JSON_GROUP = "json"
_NB_TENNICAMS = 2
_TENNICAM_FILES = ["tennicam_{}".format(i) for i in range(_NB_TENNICAMS)]
_TENNICAM_GROUP = "tennicam"
_HDF5 = "test.hdf5"


@pytest.fixture
def state_trajectory() -> bt.StateTrajectory:
    """
    Generate a line trajectory from start to end position
    """
    return bt.velocity_line_trajectory(
        _START_POSITION, _END_POSITION, _VELOCITY, _SAMPLING_RATE
    )


@pytest.fixture
def json_trajectory(state_trajectory: bt.StateTrajectory) -> str:
    """
    Convert the state trajectory to a json string representation,
    as supported by bt.RecordedBallTrajectories.add_json_trajectories.
    """

    entries = [s.position + s.velocity for s in state_trajectory]
    d = {"ob": entries}
    return repr(d)


@pytest.fixture
def tennicam_trajectory(state_trajectory: bt.StateTrajectory) -> str:
    """
    create the string representation of a ball trajectory
    in tennicam format.
    """

    size = len(state_trajectory)
    ball_ids = [i for i in range(size)]
    stamped_trajectory = bt.to_stamped_trajectory(state_trajectory, _SAMPLING_RATE)
    time_stamps = stamped_trajectory[0]
    positions = [s.position for s in state_trajectory]
    velocities = [s.velocity for s in state_trajectory]
    entries = [
        (ball_id, time_stamp * 1e3, position, velocity)
        for ball_id, time_stamp, position, velocity in zip(
            ball_ids, time_stamps, positions, velocities
        )
    ]

    return "\n".join([repr(e) for e in entries])


@pytest.fixture
def working_directory(
    tmp_path: pathlib.Path, json_trajectory: str, tennicam_trajectory: str
) -> pathlib.Path:
    """
    Generate some json and tennicam files, as well as an 
    empty hdf5 file, in a tmp directory
    """

    jsons = [tmp_path / jf for jf in _JSON_FILES]

    tennicams = [tmp_path / tf for tf in _TENNICAM_FILES]

    for jf in jsons:
        with open(jf, "w") as f:
            f.write(json_trajectory)

    for tf in tennicams:
        with open(tf, "w") as f:
            f.write(tennicam_trajectory)

    hdf5_file = tmp_path / _HDF5
    with h5py.File(hdf5_file, "w"):
        pass

    return tmp_path


@pytest.fixture
def loaded_hdf5(working_directory) -> pathlib.Path:
    """
    Add content to the hdf5 file present in the 
    working directory, and returns the absolute path
    to this file.
    """

    hdf5_file = working_directory / _HDF5

    with bt.RecordedBallTrajectories(path=hdf5_file) as rbt:
        rbt.add_json_trajectories(_JSON_GROUP, working_directory, _SAMPLING_RATE * 1e6)
        rbt.add_tennicam_trajectories(_TENNICAM_GROUP, working_directory)

    return hdf5_file


def test_conversions(state_trajectory) -> None:
    """
    Test the conversions from state trajectory to 
    stamped trajectory, and vice-versa
    """

    stamped_trajectory = bt.to_stamped_trajectory(state_trajectory, _SAMPLING_RATE)

    restate_trajectory = bt.to_state_trajectory(stamped_trajectory)

    for s1, s2 in zip(state_trajectory, restate_trajectory):
        assert s1.position == s2.position
        assert s1.velocity == pytest.approx(s2.velocity, abs=1e-3)


@pytest.mark.parametrize("formatting", [_JSON_GROUP, _TENNICAM_GROUP])
def test_add_trajectories(
    working_directory: pathlib.Path,
    state_trajectory: bt.StateTrajectory,
    formatting: str,
):
    """
    Test a hdf5 file can be updated via an instance of RecordedBallTrajectories
    with trajectories stored in json files or tennicam files.
    """

    stamped_trajectory = bt.to_stamped_trajectory(state_trajectory, _SAMPLING_RATE)
    ref_time_stamps = stamped_trajectory[0]
    ref_positions = stamped_trajectory[1]
    ref_trajectory_size = len(ref_time_stamps)

    hdf5_path = working_directory / _HDF5

    group_name = formatting

    with bt.RecordedBallTrajectories(path=hdf5_path) as rbt:
        if formatting == _JSON_GROUP:
            rbt.add_json_trajectories(
                group_name, working_directory, _SAMPLING_RATE * 1e6
            )
            expected_size = _NB_JSONS
        else:
            rbt.add_tennicam_trajectories(group_name, working_directory)
            expected_size = _NB_TENNICAMS

    with bt.RecordedBallTrajectories(path=hdf5_path) as rbt:
        assert group_name in rbt.get_groups()
        assert len(rbt.get_indexes(group_name)) == expected_size
        trajectory: StampedTrajectory = rbt.get_stamped_trajectory(group_name, 0)
        time_stamps = trajectory[0]
        positions = trajectory[1]
        assert time_stamps.shape == (ref_trajectory_size,)
        assert positions.shape == (ref_trajectory_size, 3)
        assert list(time_stamps) == pytest.approx(list(ref_time_stamps), abs=1)
        np.testing.assert_almost_equal(trajectory[1], stamped_trajectory[1])


@pytest.mark.parametrize("formatting", [_JSON_GROUP, _TENNICAM_GROUP])
def test_ball_trajectories(
    loaded_hdf5: pathlib.Path, state_trajectory: bt.StateTrajectory, formatting: str
):
    """
    Test the API of BallTrajectories
    """

    if formatting == _JSON_GROUP:
        ball_trajectories = bt.BallTrajectories(_JSON_GROUP, loaded_hdf5)
        expected_size = _NB_JSONS
    else:
        ball_trajectories = bt.BallTrajectories(_TENNICAM_GROUP, loaded_hdf5)
        expected_size = _NB_TENNICAMS

    assert len(ball_trajectories.get_all_trajectories()) == expected_size
    assert ball_trajectories.size() == expected_size
    assert (
        len(ball_trajectories.get_different_random_trajectories(expected_size))
        == expected_size
    )
    assert len(
        ball_trajectories.get_different_random_trajectories(expected_size - 1)
    ) == (expected_size - 1)

    stamped_trajectory = ball_trajectories.get_trajectory(0)
    time_stamps = stamped_trajectory[0]
    positions = stamped_trajectory[1]
    assert time_stamps.shape == (len(state_trajectory),)
    assert positions.shape == (len(state_trajectory), 3)
