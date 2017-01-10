# Copyright (c) 2010-2012 OpenStack Foundation
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
import time

from hashlib import md5,sha1
from swift.common.swob import Request, Response
from swift.common.pybst.avltree import AVLTree

class RedirectMiddleware(object):
    """
    Healthcheck middleware used for monitoring.

    If the path is /healthcheck, it will respond 200 with "OK" as the body.

    If the optional config parameter "disable_path" is set, and a file is
    present at that path, it will respond 503 with "DISABLED BY FILE" as the
    body.
    """

    def __init__(self, app, conf, c_high, c_low):
        self.app = app
        self.conf = conf
        self.c_high = c_high
        self.c_low = c_low

    def COPY(self,req):
        pass

    def REPSTH(self,req):
        pass

    def GET(self, req):
        metaTree = AVLTree().load_tree()
        key = int(md5(''+req.environ['PATH_INFO']+'').hexdigest(),16)
        node = metaTree.get_node(key)
        if node:
            node.hotnessCount += 1
            node.lastVisitTime = time.time()
            req.headers['X-Backend-Storage-Policy-Index'] = 1
        else:
            req.headers['Flag'] = 1
            #how to finish PUT DELETE
            req.headers['X-Backend-Storage-Policy-Index'] = 0
        return req

    def PUT(self,req):
        content_length = req.headers['Content-Length']
        metaTree = AVLTree().load_tree()
        key = int(md5(''+req.environ['PATH_INFO']+'').hexdigest(),16)
        capacity = int(content_length)
        now = time.time()
        metaTree.insert(key,capacity,now,req.environ['PATH_INFO'])
        metaTree.save(metaTree)
        return req

    def DELETE(self,req):
        metaTree = AVLTree().load_tree()
        key = int(md5(''+req.environ['PATH_INFO']+'').hexdigest(),16)
        node = metaTree.get_node(key)
        if node:
            metaTree.delete(key)
            req.headers['Two'] = 1
            metaTree.save(metaTree)
        return req

    def __call__(self, env, start_response):
        req = Request(env)

        if len(req.environ['PATH_INFO'].split('/')) < 5:
            return self.app(env, start_response)

        try:
            req = getattr(self,req.method)(req)
        except UnicodeError:
            # definitely, this is not /healthcheck
            pass
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def redirect_filter(app):
        return RedirectMiddleware(app, conf,2000,200)
    return redirect_filter
