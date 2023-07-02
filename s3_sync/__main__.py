import argparse
import logging
import os
import sys

from .sync import pre_delete, sync_dir

logger = logging.getLogger(__package__)

LOG_FORMAT = "[%(levelname)s] %(message)s"


def setup_logging(debug):
    log_formatter = logging.Formatter(LOG_FORMAT)
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(log_formatter)

    logger.setLevel(level=logging.DEBUG if debug else logging.INFO)
    logger.addHandler(log_handler)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--debug", action="store_true", help="Whether to emit debug logging",
    )
    argparser.add_argument(
        "--source", required=True, help="Source directory to copy from",
    )
    argparser.add_argument(
        "--dest",
        required=True,
        help="Destination directory to upload to",
    )
    argparser.add_argument(
        "--bucket",
        required=True,
        help="Name of the S3 bucket to write to",
    )
    argparser.add_argument(
        "--profile",
        required=True,
        help="AWS credential profile to use",
    )
    argparser.add_argument(
        "--endpoint",
        help="If not empty, alternate AWS endpoint to use",
    )
    argparser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Whether to follow symbolic links during directory scanning",
    )
    argparser.add_argument(
        "--delete",
        action="store_true",
        help="Whether to delete the destination directory before uploading",
    )
    argparser.add_argument(
        "--exclude",
        nargs="*",
        help="Paths to exclude when synchronizing",
    )

    args = argparser.parse_args()
    setup_logging(args.debug)
    logger.info("Running with arguments: %r", sys.argv)
    logger.debug("Parsed argument values: %s", args)

    if args.dest.startswith("/"):
        logger.error("Destination directory should not start with /")
        sys.exit(1)

    if args.delete:
        pre_delete(args)

    sync_dir(args)
