# Copyright (c) 2010-2015 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from os.path import join
import random
import time
import socket
import itertools
from collections import defaultdict
import cPickle as pickle
import shutil

from eventlet import (GreenPile, GreenPool, Timeout, sleep, hubs, tpool,
                      spawn)
from eventlet.support.greenlets import GreenletExit

from swift import gettext_ as _
from swift.common.utils import (
    whataremyips, unlink_older_than, compute_eta, get_logger,
    dump_recon_cache, ismount, mkdirs, config_true_value, list_from_csv,
    get_hub, tpool_reraise, GreenAsyncPile, Timestamp, remove_file)
from swift.common.swob import HeaderKeyDict
from swift.common.bufferedhttp import http_connect
from swift.common.daemon import Daemon
from swift.common.ring.utils import is_local_device
from swift.obj.ssync_sender import Sender as ssync_sender
from swift.common.http import HTTP_OK, HTTP_INSUFFICIENT_STORAGE
from swift.obj.diskfile import DiskFileRouter, get_data_dir, \
    get_tmp_dir
from swift.common.storage_policy import POLICIES, EC_POLICY
from swift.common.exceptions import ConnectionTimeout, DiskFileError, \
    SuffixSyncError

SYNC, REVERT = ('sync_only', 'sync_revert')


hubs.use_hub(get_hub())

class ObjectDiskinfo(Daemon):
    """
    Reconstruct objects using erasure code.  And also rebalance EC Fragment
    Archive objects off handoff nodes.

    Encapsulates most logic and data needed by the object reconstruction
    process. Each call to .reconstruct() performs one pass.  It's up to the
    caller to do this in a loop.
    """

    def __init__(self, conf, logger=None):
        """
        :param conf: configuration object obtained from ConfigParser
        :param logger: logging object
        """
        self.conf = conf
        self.logger = logger or get_logger(
            conf, log_route='object-reconstructor')
        self.run_pause = int(conf.get('run_pause', 30))
        self.http_timeout = int(conf.get('http_timeout', 60))
        self.recon_cache_path = conf.get('recon_cache_path',
                                         '/var/cache/swift')
        self.rcache = os.path.join(self.recon_cache_path, "object.recon")
        # defaults subject to change after beta
        self.conn_timeout = float(conf.get('conn_timeout', 0.5))
        self.sde1 = "df /dev/sde1"
        self.sds = [self.sde1]
        self.ip = "192.168.1.222"
        self.port = 8080

    def get_disk_info(self, **kwargs):
        """Run a diskInfo pass"""
        self.Size = 0
        self.Used = 0
        try:
            for sd in self.sds:
                disks = os.popen(sd)
                i = 0
                for disk in disks:
                    if i==0:
                        i = 1
                        continue
                    self.Size += float(disk.split()[1])
                    self.Used += float(disk.split()[2])
            return str(self.Size) + " " + str(self.Used)
        except:
            return "error"
    def run_once(self, *args, **kwargs):
        start = time.time()
        self.logger.info(_("Running object diskInfo in script mode."))
        sock = sock.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind((self.ip,self.port))
        sock.listen(1)
        connection,address = sock.accept()
        try:
            connection.settimeout(10)
            buf = connection.recv(1024)
            if buf == "get disk Info":
                connection.send(self.get_disk_info())
            else:
                connection.send("Unknow message!")
        except socket.timeout:
            self.logger.debug('diskInfo socket timeout.')
        connection.close()
        total = (time.time() - start) / 60
        self.logger.info(
            _("Object diskInfo complete (once). (%.02f minutes)"), total)
        dump_recon_cache({'object_diskInfo_time': total,
                          'object_diskInfo_last': time.time()},
                        self.rcache, self.logger)

    def run_forever(self, *args, **kwargs):
        self.logger.info(_("Starting object diskInfo in daemon mode."))
        # Run the diskInfo continually
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind((self.ip,self.port))
        sock.listen(1)
        while True:
            start = time.time()
            self.logger.info(_("Starting object diskInfo pass."))
            # Run the diskInfo
            connection,address = sock.accept()
            try:
                connection.settimeout(10)
                buf = connection.recv(1024)
                if buf == "get disk info":
                    ss = self.get_disk_info()
                    self.logger.info(ss)
                    connection.send(ss)
                else:
                    connection.send("Unknow message!")
            except socket.timeout:
                self.logger.debug('diskInfo socket timeout.')
            connection.close()
            total = (time.time() - start) / 60
            self.logger.info(
                _("Object diskInfo complete. (%.02f minutes)"), total)
            dump_recon_cache({'object_diskInfo_time': total,
                              'object_diskInfo_last': time.time()},
                             self.rcache, self.logger)
            self.logger.debug('diskInfo sleeping for %s seconds.',
                              self.run_pause)
            sleep(self.run_pause)


