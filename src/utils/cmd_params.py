from typing import Dict

import argparse
import os


def validate_file(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError(f"{f} does not exist")
    return f


def extract_cmd_params() -> Dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        dest="filename",
        required=True,
        type=validate_file,
        help="survey data file",
        metavar="FILE",
    )

    args = parser.parse_args()
    args_dict = vars(args)
    return args_dict
