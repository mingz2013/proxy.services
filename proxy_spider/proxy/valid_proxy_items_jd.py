# -*- coding:utf-8 -*-
__author__ = 'zhaojm'

import time

from proxy import ValidProxyItemsJd

if __name__ == '__main__':

    try:
        valid = ValidProxyItemsJd()
        valid.start_threadpool()
    except Exception, e:
        print e.message
