import logging
import os
import subprocess
from pathlib import PurePath

logger = logging.getLogger(__package__)


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


def pre_delete(args):
    assert args.delete

    s3_path = bucket_path(args)
    logger.info("Running pre-deletion: %s", s3_path)
    run_s3_command(args, "rm", "--recursive", s3_path)


def sync_file(args, source_path, dest_path):
    logger.info("Uploading %s -> %s", source_path, dest_path)
    mime_type = get_mime(source_path)
    s3_path = os.path.join(bucket_path(args), dest_path)
    run_s3_command(args, "cp", source_path, s3_path, "--no-progress", "--content-type", mime_type)


def sync_dir(args):
    for dirpath, dirnames, filenames in os.walk(
        args.source, followlinks=args.follow_symlinks,
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
