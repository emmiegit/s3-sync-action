import argparse
import logging
import os
import sys

logger = logging.getLogger(__package__)

LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
LOG_DATE_FORMAT = "[%Y/%m/%d %H:%M:%S]"

if __name__ == "__main__":
    log_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(log_formatter)

    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(log_handler)

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--source", required=True, help="Source directory to copy from"
    )
    argparser.add_argument(
        "--dest",
        "--destination",
        required=True,
        help="Destination directory to upload to",
    )
    argparser.add_argument(
        "--bucket", required=True, help="Name of the S3 bucket to write to",
    )
    argparser.add_argument(
        "--profile", required=True, help="AWS credential profile to use",
    )
    argparser.add_argument(
        "--endpoint", help="If not empty, alternate AWS endpoint to use",
    )
    argparser.add_argument(
        "--delete",
        action="store_true",
        help="Whether to delete the destination directory before uploading",
    )
    argparser.add_argument(
        "--exclude", nargs="*", help="Paths to exclude when synchronizing",
    )
    args = argparser.parse_args()

    # TODO
