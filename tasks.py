#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
tasks module.
"""

import configparser
import os

from invoke import task


@task
def new_release(context, version_part):
    """
    new_release task.
    """

    repo_dirpath = os.path.dirname(os.path.realpath(__file__))
    if not os.environ.get("GITHUB_USERNAME", None):
        raise OSError("Environment variable 'GITHUB_USERNAME' not set")

    version_parts = ["major", "minor", "patch"]
    if version_part.lower() not in version_parts:
        version_part_error = "Version Part must be one of {} not {}"
        raise ValueError(
            version_part_error.format(version_parts, version_part)
        )

    changelog_config = os.path.join(
        repo_dirpath, ".github_changelog_generator"
    )
    if not os.path.exists(changelog_config):
        changelog_error = "Github Changelog Generator config not found: {}"
        raise OSError(changelog_error.format(changelog_config))

    bumpversion_config = os.path.join(repo_dirpath, ".bumpversion.cfg")
    if not os.path.exists(bumpversion_config):
        bumpversion_error = "Bumpversion config not found: {}"
        raise OSError(bumpversion_error.format(bumpversion_config))

    context.run("bump2version {}".format(version_part))
    context.run("git push")

    config = configparser.ConfigParser()
    config.read(bumpversion_config)
    current_version = config["bumpversion"]["current_version"]
    git_commit_changelog = 'git commit --message="Generate changelog: v{}"'

    context.run("github_changelog_generator --user $GITHUB_USERNAME")
    context.run("git add --all")
    context.run(git_commit_changelog.format(current_version))
    context.run("git push")


@task
def revert_last(context):
    """
    revert_last task.
    """

    latest_tag = context.run("git describe --abbrev=0 --tags", hide=True).stdout.strip()
    prompt = ">>> Are you sure?? You're about to run these commands:"
    git_reset_hard = "git reset --hard HEAD~2"
    git_tag_delete = "git tag --delete {}".format(latest_tag)
    git_push_delete = "git push --delete origin {}".format(latest_tag)
    git_push_force = "git push --force"
    user_input = input(
        "{}\n{}\n{}\n{}\n{}\n>>> [y/N]".format(
            prompt,
            git_reset_hard,
            git_tag_delete,
            git_push_delete,
            git_push_force,
        )
    )
    if not user_input.lower().startswith("y"):
        raise SystemExit
    context.run(git_reset_hard)
    context.run(git_tag_delete)
    context.run(git_push_delete)
    context.run(git_push_force)
