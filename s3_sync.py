import argparse
import logging
import os
import subprocess
import sys
from pathlib import PurePath

logger = logging.getLogger(__package__)


def setup_logging(debug):
    log_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(log_formatter)

    logger.setLevel(level=logging.DEBUG if debug else logging.INFO)
    logger.addHandler(log_handler)


def bucket_path(args):
    return f"s3://{args.bucket}/{args.dest}"


def run_s3_command(args, command, *options):
    arguments = [
        "aws",
        "s3",
        command,
        "--profile",
        args.profile,
    ]
    arguments.extend(options)
    logger.debug("Running command: %r", arguments)
    subprocess.check_call(arguments)


def get_mime(path):
    output = subprocess.check_output(
        [
            "file",
            "--brief",
            "--mime",
            path,
        ]
    )
    mime_type = output.decode("utf-8").rstrip()
    logger.debug("Got MIME type for %s: %s", path, mime_type)
    return mime_type


def is_excluded(args, path):
    if args.exclude is not None:
        for excluded_path in args.exclude:
            if os.path.samefile(path, excluded_path):
                return True
    return False


def parent_path(parent, child):
    parent_path = PurePath(parent)
    child_path = PurePath(child)
    return str(child_path.relative_to(parent_path))


def pre_delete(args):
    assert args.delete

    s3_path = bucket_path(args)
    logger.info("Running pre-deletion: %s", s3_path)
    run_s3_command(args, "rm", "--recursive", s3_path)


def sync_file(args, source_path, dest_path):
    logger.info("Uploading %s -> %s", source_path, dest_path)
    mime_type = get_mime(source_path)
    s3_path = os.path.join(bucket_path(args), dest_path)
    run_s3_command(
        args,
        "cp",
        source_path,
        s3_path,
        "--no-progress",
        "--content-type",
        mime_type,
    )


def sync_dir(args):
    logger.info("Beginning upload to %s", bucket_path(args))

    for dirpath, dirnames, filenames in os.walk(
        args.source,
        followlinks=args.follow_symlinks,
    ):
        if is_excluded(args, dirpath):
            logger.debug("Skipping directory %s", dirpath)
            continue

        logger.info("Entered %s", dirpath)
        destdir = parent_path(args.source, dirpath)
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            destpath = os.path.join(destdir, filename) if destdir != "." else filename

            if is_excluded(args, fullpath):
                logger.debug("Skipping path %s", fullpath)
                continue

            sync_file(args, fullpath, destpath)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--debug",
        action="store_true",
        help="Whether to emit debug logging",
    )
    argparser.add_argument(
        "--source",
        required=True,
        help="Source directory to copy from",
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
    logger.info("Finished uploading to S3!")
