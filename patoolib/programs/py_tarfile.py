# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Bastian Kleineidam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Archive commands for the tarfile Python module."""
from .. import util
import tarfile

READ_SIZE_BYTES = 1024*1024


def list_tar (archive, compression, cmd, verbosity, interactive):
    """List a TAR archive with the tarfile Python module."""
    try:
        with tarfile.open(archive) as tfile:
            tfile.list(verbose=verbosity>1)
    except Exception as err:
        msg = "error listing %s" % (archive, )
        raise util.PatoolError(msg) from err
    return None

test_tar = list_tar

def extract_tar (archive, compression, cmd, verbosity, interactive, outdir):
    """Extract a TAR archive with the tarfile Python module."""
    try:
        with tarfile.open(archive) as tfile:
            import os

            def is_within_directory(directory, target):
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
                prefix = os.path.commonprefix([abs_directory, abs_target])
                return prefix == abs_directory

            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
                tar.extractall(path, members, numeric_owner=numeric_owner) 

            safe_extract(tfile, path=outdir)
    except Exception as err:
        msg = "error extracting %s" % (archive, )
        raise util.PatoolError(msg) from err
    return None


def create_tar (archive, compression, cmd, verbosity, interactive, filenames):
    """Create a TAR archive with the tarfile Python module."""
    mode = get_tar_mode(compression)
    try:
        with tarfile.open(archive, mode) as tfile:
            for filename in filenames:
                tfile.add(filename)
    except Exception as err:
        msg = "error creating %s" % (archive, )
        raise util.PatoolError(msg) from err
    return None


def get_tar_mode (compression):
    """Determine tarfile open mode according to the given compression."""
    if compression == 'gzip':
        return 'w:gz'
    if compression == 'bzip2':
        return 'w:bz2'
    if compression == 'lzma':
        return 'w:xz'
    if compression:
        msg = 'pytarfile does not support %s for tar compression'
        raise util.PatoolError(msg % compression)
    # no compression
    return 'w'
