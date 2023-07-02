import logging
import os
import subprocess

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
        "--no-progress",
    ]
    arguments.extend(options)
    logger.debug("Running command %r", arguments)
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


def sync_file(args, path):
    logger.info("Uploading %s", fullpath)
    mime_type = get_mime(path)
    run_s3_command(args, "cp", source, dest, "--content-type", mime_type)


def sync_dir(args):
    for dirpath, dirnames, filenames in os.walk(
        args.source, followlinks=args.follow_symlinks,
    ):
        if is_excluded(args, dirpath):
            logger.debug("Skipping directory %s", dirpath)
            continue

        logger.info("Entered %s", dirpath)
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            if is_excluded(args, fullpath):
                logger.debug("Skipping path %s", fullpath)
                continue

            sync_file(args, fullpath)


def is_excluded(args, path):
    for excluded_path in args.exclude:
        if os.path.samefile(path, excluded_path):
            return True
    return False
