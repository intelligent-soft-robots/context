import h5py
import pathlib
import pytest
import numpy as np
from context import ball_trajectories as bt


# configuration of the stamped_trajectory fixture
_START_POSITION = (1.0, 2.0, 1.0)
_END_POSITION = (3.0, 4.0, 1.0)
_VELOCITY = 0.5
_SAMPLING_RATE = 10000  # microseconds

# configuration for working_directory fixture
_NB_JSONS = 3
_JSON_FILES = ["{}.json".format(i) for i in range(_NB_JSONS)]
_JSON_GROUP = "json"
_NB_TENNICAMS = 2
_TENNICAM_FILES = ["tennicam_{}".format(i) for i in range(_NB_TENNICAMS)]
_TENNICAM_GROUP = "tennicam"
_HDF5 = "test.hdf5"


@pytest.fixture
def duration_trajectory() -> bt.DurationTrajectory:
    """
    Generate a line trajectory from start to end position
    """
    return bt.velocity_line_trajectory(
        _START_POSITION, _END_POSITION, _VELOCITY, float(_SAMPLING_RATE * 1e-6)
    )


@pytest.fixture
def json_trajectory(duration_trajectory: bt.DurationTrajectory) -> str:
    """
    Convert the duration trajectory to a json string representation,
    as supported by bt.RecordedBallTrajectories.add_json_trajectories.
    """
    positions = duration_trajectory[1]
    velocities = duration_trajectory[2]
    entries = np.concatenate((positions, velocities), axis=1)
    entries = list([list(entries[i, :]) for i in range(entries.shape[0])])
    d = {"ob": entries}
    return repr(d)


@pytest.fixture
def tennicam_trajectory(duration_trajectory: bt.DurationTrajectory) -> str:
    """
    create the string representation of a ball trajectory
    in tennicam format.
    """

    size = len(duration_trajectory[0])
    ball_ids = [i for i in range(size)]
    stamped_trajectory = bt.to_stamped_trajectory(duration_trajectory)
    time_stamps = stamped_trajectory[0]
    positions = list(duration_trajectory[1])
    velocities = list(duration_trajectory[2])
    entries = [
        (ball_id, time_stamp * 1e3, list(position), list(velocity))
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

    with bt.MutableRecordedBallTrajectories(path=hdf5_file) as rbt:
        rbt.add_json_trajectories(_JSON_GROUP, working_directory, _SAMPLING_RATE * 1e6)
        rbt.add_tennicam_trajectories(_TENNICAM_GROUP, working_directory)

    return hdf5_file


def test_rm_group(loaded_hdf5) -> None:
    """
    Test the RecordedBallTrajectories.rm_group
    method.
    """

    path = loaded_hdf5
    with bt.MutableRecordedBallTrajectories(path) as rbt:
        assert _JSON_GROUP in rbt.get_groups()
        rbt.rm_group(_JSON_GROUP)
        assert _JSON_GROUP not in rbt.get_groups()

    with bt.MutableRecordedBallTrajectories(path) as rbt:
        assert _JSON_GROUP not in rbt.get_groups()


def test_overwrite(loaded_hdf5) -> None:
    """
    Test the MutableRecordedBallTrajectories.overwrite
    method.
    """
    stamps = np.array([10] * 5)
    positions = np.array([np.array([2] * 3)] * 5)
    path = loaded_hdf5

    with bt.MutableRecordedBallTrajectories(path) as rbt:
        rbt.overwrite(_JSON_GROUP, 1, (stamps, positions))

    with bt.RecordedBallTrajectories(path) as rbt:
        stamped_trajectory = rbt.get_stamped_trajectory(_JSON_GROUP, 1)
        restamps = stamped_trajectory[0]
        repositions = stamped_trajectory[1]
        assert np.array_equal(stamps, restamps)
        for line in range(positions.shape[0]):
            p1 = positions[line, :]
            p2 = repositions[line, :]
            np.testing.assert_almost_equal(p1, p2)


def test_conversions(duration_trajectory) -> None:
    """
    Test the conversions from state trajectory to
    stamped trajectory, and vice-versa
    """

    stamped_trajectory = bt.to_stamped_trajectory(duration_trajectory)
    reduration_trajectory = bt.to_duration_trajectory(stamped_trajectory)

    # durations
    assert np.array_equal(duration_trajectory[0][:-1], reduration_trajectory[0])

    # positions
    for line in range(duration_trajectory[1][1:, :].shape[0]):
        p1 = duration_trajectory[1][line, :]
        p2 = reduration_trajectory[1][line, :]
        np.testing.assert_almost_equal(p1, p2)

    # velocities
    for line in range(duration_trajectory[2][1:, :].shape[0]):
        v1 = duration_trajectory[2][line, :]
        v2 = reduration_trajectory[2][line, :]
        np.testing.assert_almost_equal(v1, v2)


@pytest.mark.parametrize("formatting", [_JSON_GROUP, _TENNICAM_GROUP])
def test_add_trajectories(
    working_directory: pathlib.Path,
    duration_trajectory: bt.DurationTrajectory,
    formatting: str,
):
    """
    Test a hdf5 file can be updated via an instance of RecordedBallTrajectories
    with trajectories stored in json files or tennicam files.
    """

    stamped_trajectory = bt.to_stamped_trajectory(duration_trajectory)
    ref_time_stamps = stamped_trajectory[0]
    ref_trajectory_size = len(ref_time_stamps)

    print()
    print(duration_trajectory[0][:10])
    print(ref_time_stamps[:10])
    print()

    hdf5_path = working_directory / _HDF5

    group_name = formatting

    with bt.MutableRecordedBallTrajectories(path=hdf5_path) as rbt:
        if formatting == _JSON_GROUP:
            nb_added = rbt.add_json_trajectories(
                group_name, working_directory, _SAMPLING_RATE
            )
            expected_size = _NB_JSONS
        else:
            nb_added = rbt.add_tennicam_trajectories(group_name, working_directory)
            expected_size = _NB_TENNICAMS

    assert nb_added == expected_size

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
    loaded_hdf5: pathlib.Path,
    duration_trajectory: bt.DurationTrajectory,
    formatting: str,
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
    assert time_stamps.shape == (len(duration_trajectory[0]),)
    assert positions.shape == (len(duration_trajectory[0]), 3)
