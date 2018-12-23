# -*- coding: utf-8 -*-
"""Utility functions to get information about the
git or mercurial repository in the working directory
"""
import subprocess
import os


def get_current_git_branch():
    command = ["git", "symbolic-ref", "--short", "-q", "HEAD"]
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = proc.communicate()
        return out.strip().decode("utf-8")
    except subprocess.CalledProcessError:
        pass
    return ""


# We'll avoid shelling out to hg for speed.
def find_hg_root():
    def get_parent_dir(directory):
        return os.path.abspath(os.path.join(directory, os.pardir))

    cwd = os.getcwd()
    while True:
        pardir = get_parent_dir(cwd)

        hgroot = os.path.join(cwd, ".hg")
        if os.path.isdir(hgroot):
            return hgroot

        if cwd == pardir:
            break

        cwd = pardir

    return ""


def get_current_hg_branch():
    try:
        hgroot = find_hg_root()
        with open(os.path.join(hgroot, "branch")) as f:
            branch = f.read().rstrip()
    except IOError:
        branch = ""

    return branch


def get_current_hg_bookmark():
    try:
        hgroot = find_hg_root()
        with open(os.path.join(hgroot, "bookmarks.current")) as f:
            bookmark = f.read()
    except IOError:
        bookmark = ""
    return bookmark


def get_current_hg_id():
    branch = get_current_hg_branch()
    bookmark = get_current_hg_bookmark()
    if bookmark:
        # If we have a bookmark, the default branch is no longer
        # an interesting name.
        if branch == "default":
            branch = ""
        branch += " " + bookmark
    return branch


def get_current_vcs_branch():
    return get_current_git_branch() + get_current_hg_id()
