#!/usr/bin/env python3

"""
For manipulating a ball trajectory hdf5 file:
- adding trajectories to it (via json or tennicam files)
- for deleting trajectories
- for getting info about the file
- for translating all the points of a group of trajectories.
"""

import sys
import argparse
import logging
import pathlib
import typing
import numpy as np
import context.ball_trajectories as bt


def _info_group(rbt: bt.RecordedBallTrajectories, group_name: str):

    indexes = rbt.get_indexes(group_name)

    print("\ngroup: {} , found {} trajectories".format(group_name, len(indexes)))
    for index in sorted(indexes):
        stamps, positions = rbt.get_stamped_trajectory(group_name, index)
        nb_points = len(stamps)
        duration = (stamps[-1] - stamps[0]) * 1e-6
        first_position = str("{:.2f} " * 3).format(*list(positions[0, :]))
        print(
            "\tindex: {}\t {} points\t{:.2f} seconds ( first: {})".format(
                index, nb_points, duration, first_position
            )
        )
    print()


def _info_whole_file(rbt: bt.RecordedBallTrajectories):
    groups = rbt.get_groups()
    print()
    for group in groups:
        print("group: {} , {} trajectories".format(group, len(rbt.get_indexes(group))))
    print()


def _info(hdf5_path: pathlib.Path, group_name: str = None):
    with bt.RecordedBallTrajectories(hdf5_path) as rbt:
        print("\nhdf5 trajectories file: {}".format(hdf5_path))
        if group_name:
            _info_group(rbt, group_name)
        else:
            _info_whole_file(rbt)


def _add_json(hdf5_path: pathlib.Path, group_name: str, sampling: int):
    logging.info("recording trajectories in {}".format(hdf5_path))
    with bt.MutableRecordedBallTrajectories(path=hdf5_path) as rbt:
        if group_name in rbt.get_groups():
            raise ValueError("group {} already present in the file")
        nb_added = rbt.add_json_trajectories(group_name, pathlib.Path.cwd(), sampling)
    logging.info("added {} trajectories".format(nb_added))


def _add_tennicam(hdf5_path: pathlib.Path, group_name: str):
    logging.info("recording trajectories in {}".format(hdf5_path))
    with bt.MutableRecordedBallTrajectories(path=hdf5_path) as rbt:
        if group_name in rbt.get_groups():
            raise ValueError("group {} already present in the file")
    nb_added = rbt.add_tennicam_trajectories(group_name, pathlib.Path.cwd())
    logging.info("added {} trajectories".format(nb_added))


def _rm_group(hdf5_path: pathlib.Path, group_name: str):
    with bt.MutableRecordedBallTrajectories(path=hdf5_path) as rbt:
        rbt.rm_group(group_name)


def _translate(hdf5_path: pathlib.Path, group_name: str, coords: typing.List[float]):
    coords = np.array(coords, np.float32)
    with bt.RecordedBallTrajectories(path=hdf5_path) as rbt:
        for index in rbt.get_indexes(group_name):
            stamps, trajectory = rbt.get_stamped_trajectory(
                group_name, index, direct=True
            )
            trajectory += coords
            rbt.overwrite(group_name, index, (stamps, trajectory))


def run():

    parser = argparse.ArgumentParser()

    # the executable will use by default the hdf5 managed by
    # pam_configuration, but user has the option to point to
    # another file.
    parser.add_argument(
        "--path",
        type=str,
        required=False,
        help="path to the hdf5 file encapsulating the ball trajectories",
    )

    # 5 commands supported: info, add-json, add-tennicam,
    # rm and translate.
    subparser = parser.add_subparsers(dest="command", required=True)

    # for displaying info about the hdf5 file
    info = subparser.add_parser(
        "info",
        help="print information about the whole file, or a given group in the file.",
    )
    info.add_argument(
        "--group", type=str, required=False, help="the group of trajectories"
    )

    # for adding the json files of the current folder
    # to a hdf5 trajectory file
    add_json = subparser.add_parser(
        "add-json",
        help="""for saving in a new group all json trajectories present in the current
            directory
        """,
    )
    add_json.add_argument(
        "--group", type=str, required=True, help="the group of trajectories"
    )
    add_json.add_argument(
        "--sampling-rate-us",
        type=int,
        required=True,
        help="record sampling rate, in microseconds (int)",
    )

    # for adding the tennicam files of the current folder
    # to a hdf5 trajectory file
    add_tennicam = subparser.add_parser(
        "add-tennicam",
        help="for saving in a new group all tennicam present in the current directory",
    )
    add_tennicam.add_argument(
        "--group", type=str, required=True, help="the group of trajectories"
    )

    # for removing a group from the hdf5 file
    rm_group = subparser.add_parser(
        "rm", help="for removing trajectories from the file"
    )
    rm_group.add_argument(
        "--group", type=str, required=True, help="the group of trajectories"
    )

    # for translating all points in all the trajectories of the group
    translate = subparser.add_parser(
        "translate", help="translate all the positions of all trajectories of the group"
    )
    translate.add_argument(
        "--group", type=str, required=True, help="the group of trajectories"
    )
    translate.add_argument(
        "--coords", type=float, nargs=3, required=True, help="x y z coordinates (float)"
    )

    # parsing the arguments
    args = parser.parse_args()

    # all subparsers asks for an optional path. Using this path if provided,
    # the default hdf5 path otherwise
    if args.path:
        hdf5_path = pathlib.Path(args.path)
    else:
        hdf5_path = bt.RecordedBallTrajectories.get_default_path(create=True)

    # checking the file exists
    if not pathlib.Path(hdf5_path).is_file():
        raise FileNotFoundError("failed to find the file {}".format(hdf5_path))

    # going ahead based on the arguments
    if args.command == "info":
        _info(hdf5_path, args.group)

    elif args.command == "add-json":
        _add_json(hdf5_path, args.group, args.sampling_rate_us)

    elif args.command == "add-tennicam":
        _add_tennicam(hdf5_path, args.group)

    elif args.command == "rm":
        _rm_group(hdf5_path, args.group)

    elif args.command == "translate":
        _translate(hdf5_path, args.group, args.coords)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # try:
    run()
    # except Exception as e:
    #    logging.error("failed with error: {}".format(e))
    #    sys.exit(1)

    sys.exit(0)
