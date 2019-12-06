#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import Crypto
from Crypto.PublicKey import RSA
import time
from fuse import FUSE, FuseOSError, Operations, fuse_get_context
from multiprocessing import Process, Pipe
from unprivileged import DH
from chacha20poly1305 import ChaCha20Poly1305
import pyDH


class f_system(Operations):

    def __init__(self, root):
        self.root = root
        self.value = "parent"
        key = RSA.generate(2048)
        binPrivKey = key.exportKey('DER')
        binPubKey = key.publickey().exportKey('DER')
        privKeyObj = RSA.importKey(binPrivKey)
        pubKeyObj = RSA.importKey(binPubKey)

        try:
            newpid = os.fork()
        except:
            return 'service not started'

        if newpid == 0:
            time.sleep(2)
            os.system("python server.py "+str(root))
        else:

            privilegedProcessPipeEnd, unprivilegedProcessPipeEnd = Pipe()
            unprivilegedProcess = Process(target=DH(unprivilegedProcessPipeEnd).share_key(root))
            unprivilegedProcess.start()

            d1 = pyDH.DiffieHellman()
            d1_key = d1.gen_public_key()
            privilegedProcessPipeEnd.send(d1_key)
            d2_key = privilegedProcessPipeEnd.recv()
            shared_key = d1.gen_shared_key(d2_key)
            self.shared_key = shared_key # GroupService
            self.privilegedProcessPipeEnd = privilegedProcessPipeEnd
            self._ = privilegedProcessPipeEnd.recv()
            self._1 = privilegedProcessPipeEnd.recv()
            self._2 = privilegedProcessPipeEnd.recv()
            self._3 = privilegedProcessPipeEnd.recv()
            self.__ = ChaCha20Poly1305(hashlib.sha256(shared_key).digest())
            del d1
            del d2_key

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if path.split('/')[-1] == 'config':
            return 0
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        (uid,gid,pid) = fuse_get_context()
        print 'open called'
        print 'path is '+full_path
        if path.split('/').count('shared')>0:
            n = os.urandom(12)
            self.privilegedProcessPipeEnd.send(n)
            if self.cip.decrypt(n,self.privilegedProcessPipeEnd.recv()) != n:
                return 0
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        (uid,gid,pid) = fuse_get_context()
        print("pid is :"+str(pid))
	#if pid != self.pid:
	#	return 0
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        (uid, gid, pid) = fuse_get_context()
        if path.split("/")[-1] == "config":
		   return 0
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        (uid, gid, pid) = fuse_get_context()
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(f_system(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
