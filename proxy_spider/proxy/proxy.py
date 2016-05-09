# -*- coding:utf-8 -*-
__author__ = 'zhaojm'

import urllib2
import threadpool

from proxy_spider.db.mongo import ProxyItemsDB, ProxyItemsValidDB, ProxyItemsJdDB, ProxyItemsDropDB


class DumpAToB(object):
    '''
    验证a中的数据到b中
    '''

    def __init__(self, http_url=None, https_url=None):
        self.http_url = http_url
        self.https_url = https_url
        if not self.http_url and not self.https_url:
            return

        self.pool = None
        self._init_threadpool()
        pass

    def _is_valid_proxy_item_http(self, item):
        '''
        检查item是否可用,通过传入的URl去检查
        :param item:
        :param http_url:
        :param https_url:
        :return:
        '''

        proxy_type = item["type"].lower()

        if self.http_url and proxy_type.find('http') != -1:
            proxy = "%s:%s" % (item["ip"], item["port"])
            try:
                req = urllib2.Request(url=self.http_url)
                req.set_proxy(proxy, 'http')
                response = urllib2.urlopen(req, timeout=self.get_timeout())
            except Exception, e:
                return False
            else:
                code = response.getcode()
                if 200 <= code < 300:
                    return True
                else:
                    return False
            pass
        else:
            # item类型和要爬取的url协议不同, 不可用
            # print "item type not valid: proxy type: %s" % proxy_type
            return False

    def _is_valid_proxy_item_https(self, item):
        '''
        检查item是否可用,通过传入的URl去检查
        :param item:
        :param http_url:
        :param https_url:
        :return:
        '''

        proxy_type = item["type"].lower()

        if self.https_url and proxy_type.find('https') != -1:
            proxy = "%s:%s" % (item["ip"], item["port"])
            try:
                req = urllib2.Request(url=self.https_url)
                req.set_proxy(proxy, 'https')
                response = urllib2.urlopen(req, timeout=self.get_timeout())
            except Exception, e:
                # print "Exception", e
                return False
            else:
                code = response.getcode()
                # print "code", code
                if 200 <= code < 300:
                    return True
                else:
                    return False
        else:
            # item类型和要爬取的url协议不同, 不可用
            # print "item type not valid: proxy type: %s" % proxy_type
            return False

    def thread_call_back(self, is_valid_http, is_valid_https, item):
        pass

    def _thread_call_back(self, args):
        try:
            # print args["type"]
            is_valid_http = self._is_valid_proxy_item_http(args)
            is_valid_https = self._is_valid_proxy_item_https(args)
            # print "is http %s" % is_valid_http
            # print "is_https %s" % is_valid_https
            # if is_valid_https:
            #     print "valid https item: %s:%s" % (args['ip'], args['port'])
            self.thread_call_back(is_valid_http, is_valid_https, args)
        except Exception, e:
            print "thread_call_back: ", e.message

    def get_argss(self):
        return []

    def get_thread_num(self):
        return 1

    def get_timeout(self):
        return 20

    def _init_threadpool(self):
        try:
            thread_num = self.get_thread_num()
            argss = self.get_argss()
            print "thread_num: %s" % thread_num
            print "items num: %s" % argss.count()
            self.pool = threadpool.ThreadPool(thread_num)
            requests = threadpool.makeRequests(self._thread_call_back, argss)
            [self.pool.putRequest(req) for req in requests]
        except Exception, e:
            print "init threadpool: ", e.message
        pass

    def start_threadpool(self):
        try:
            self.pool.wait()
            return True
        except Exception, e:
            print "start threadpool: ", e.message
            return False


class DumpProxyItemsToProxyItemsValid(DumpAToB):
    '''
    验证爬虫爬取的代理到已验证代理中
    '''
    def __init__(self):
        http_url = "http://www.baidu.com/"
        https_url = "https://www.alipay.com/"
        DumpAToB.__init__(self, http_url=http_url, https_url=https_url)
        pass

    def get_argss(self):
        return ProxyItemsDB.get_proxy_items()

    def get_thread_num(self):
        return 60

    def get_timeout(self):
        return 20

    def thread_call_back(self, is_valid_http, is_valid_https, item):
        if is_valid_http or is_valid_https:
            ProxyItemsValidDB.upsert_proxy_item(item)
        else:
            ProxyItemsDropDB.upsert_proxy_item(item)
        ProxyItemsDB.remove_proxy_item(item)
        pass


class ValidProxyItemsValid(DumpAToB):
    '''
    重复 验证已验证代理
    '''

    def __init__(self):
        http_url = "http://www.baidu.com/"
        https_url = "https://www.alipay.com/"
        DumpAToB.__init__(self, http_url=http_url, https_url=https_url)
        pass

    def get_argss(self):
        return ProxyItemsValidDB.get_proxy_items()

    def get_thread_num(self):
        return 60

    def thread_call_back(self, is_valid_http, is_valid_https, item):
        if not is_valid_http and not is_valid_https:
            ProxyItemsValidDB.remove_proxy_item(item)
            ProxyItemsDropDB.upsert_proxy_item(item)


class ValidProxyItemsDrop(DumpAToB):
    '''
    重复 验证 已丢弃的代理,再给一次机会
    '''

    def __init__(self):
        http_url = "http://www.baidu.com/"
        https_url = "https://www.alipay.com/"
        DumpAToB.__init__(self, http_url=http_url, https_url=https_url)
        pass

    def get_argss(self):
        return ProxyItemsDropDB.get_proxy_items()

    def get_thread_num(self):
        return 60

    def get_timeout(self):
        return 20

    def thread_call_back(self, is_valid_http, is_valid_https, item):
        if is_valid_http or is_valid_https:
            ProxyItemsValidDB.upsert_proxy_item(item)
        ProxyItemsDropDB.remove_proxy_item(item)


class ValidProxyItemsJd(DumpAToB):
    '''
    重复 验证已验证jd代理
    '''

    def __init__(self):
        http_url = "http://www.jd.com"
        https_url = "https://www.jd.com/"
        DumpAToB.__init__(self, http_url=http_url, https_url=https_url)
        pass

    def get_argss(self):
        return ProxyItemsJdDB.get_proxy_items()

    def get_thread_num(self):
        return 60

    def thread_call_back(self, is_valid_http, is_valid_https, item):
        if not is_valid_http and not is_valid_https:
            ProxyItemsJdDB.remove_proxy_item(item)
            ProxyItemsDropDB.upsert_proxy_item(item)


class DumpProxyItemsValidToProxyItemsSite(DumpAToB):
    '''
    验证爬取单个网站可用的代理ip
    '''
    def __init__(self, http_url=None, https_url=None):
        DumpAToB.__init__(self, http_url=http_url, https_url=https_url)
        pass

    def get_argss(self):
        return ProxyItemsValidDB.get_proxy_items()

    def get_thread_num(self):
        return 60

    def upsert_proxy_item(self, item):
        pass

    def thread_call_back(self, is_valid_http, is_valid_https, item):
        if is_valid_http and is_valid_https:
            self.upsert_proxy_item(item)


class DumpProxyItemsValidToProxyItemsJd(DumpProxyItemsValidToProxyItemsSite):
    '''
    验证爬取jd可用的代理ip
    '''
    def __init__(self):
        http_url = "http://www.jd.com/"
        https_url = "https://www.jd.com/"
        DumpProxyItemsValidToProxyItemsSite.__init__(self, http_url=http_url, https_url=https_url)

    def upsert_proxy_item(self, item):
        ProxyItemsJdDB.upsert_proxy_item(item)
