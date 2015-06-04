# -*- coding: utf-8 -*-
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import urlparse 
import logging,os,functools
import simplejson as json 
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
from tornado.web import HTTPError, asynchronous
from tornado.httpclient import HTTPRequest
from tornado.options import define, options
import mako.lookup
import mako.template
try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient as AsyncHTTPClient
except ImportError:
    from tornado.simple_httpclient import SimpleAsyncHTTPClient as AsyncHTTPClient
relpath = lambda *a: os.path.join(os.path.dirname(__file__), *a)

api_setting = open('urls.txt').read()
define("port", default=8888, help="run on the given port", type=int)
define("api_protocol", default="http")
define("api_host", default="pre3.test.com")
define("api_port", default="8989")
define("api_setting", default=json.loads(api_setting))
define("debug", default=True, type=bool)
define("template_path", default=u'F:\\Appflood\\af_web\\templates\\')
define("static_path", default=u'F:\\Appflood\\af_web\\static\\')

SETTINGS={
    "template_path":options.template_path,
    "static_path":options.static_path,
    "cookie_secret": "cxP6yKNYQZyhAtJ5/1gxCq1BCwD+qUnzqiHHYt2GvNY=",
    }

class ProxyHandler(tornado.web.RequestHandler):
    def initialize(self):
        template_path = options.template_path #self.get_template_path()
        
        self.lookup = mako.lookup.TemplateLookup(directories=[template_path], input_encoding='utf-8', output_encoding='utf-8')

    def render_string(self, filename, **kwargs):
        template = self.lookup.get_template(filename)
        namespace = self.get_template_namespace()
        namespace.update(kwargs)
        return template.render(**namespace)

    def render(self, filename, **kwargs):
        self.finish(self.render_string(filename, **kwargs))

        
    @asynchronous
    def get(self):
        # enable API GET request when debugging
        
        if options.debug:
            return self.post()
        else:
            raise HTTPError(405)
 
    @asynchronous
    def post(self):
        protocol = options.api_protocol
        host = options.api_host
        port = options.api_port
 
        # port suffix
        port = "" if port == "80" else ":%s" % port
 
        uri = self.request.uri
        url = "%s://%s%s%s" % (protocol, host, port, uri)
 
        # update host to destination host
        headers = dict(self.request.headers)
        headers["Host"] = host
        if self.request.path in options.api_setting.keys():
            headers["If-Appflood-Api"] = "true"
        try:
            a=AsyncHTTPClient().fetch(
                HTTPRequest(url=url,
                            method="POST",
                            body=self.request.body,
                            headers=headers,
                            follow_redirects=False),
                self._on_proxy)

        except tornado.httpclient.HTTPError, x:
            if hasattr(x, "response") and x.response:
                self._on_proxy(x.response)
            else:
                logging.error("Tornado signalled HTTPError %s", x)

    
    def _on_proxy(self, response):
        if response.error and not isinstance(response.error,
                                             tornado.httpclient.HTTPError):
            raise HTTPError(500)
        else:
            self.set_status(response.code)
            api_setting=options.api_setting
            host=self.request.host
            for header in response.headers.keys():
                v = response.headers.get(header)
                if header=='Location' and v:
                    uri=list(urlparse.urlparse(v))
                    if uri[1]==options.api_host:
                        uri[1]=host
                    v=urlparse.urlunparse(uri)
                    self.set_header(header, v)
                    return self.finish()
                if v and header!='Content-Length':
                    self.set_header(header, v)
            for name in api_setting.keys():
                
                if self.request.path==name:
                    data=json.loads(response.body)
                    return self.render(api_setting[name],**data)
 
            if response.body:
                self.write(response.body)
            self.finish()


  

 
def main():
    tornado.options.parse_command_line()
    urls=[
        (r"/images/(.*)",tornado.web.StaticFileHandler, {"path": options.static_path+'images'}),
        (r"/js/(.*)",tornado.web.StaticFileHandler, {"path": options.static_path+'js'}),
        (r"/css/(.*)",tornado.web.StaticFileHandler, {"path": options.static_path+'css'})
    ]
    urls.append((r"/.*", ProxyHandler))
    application = tornado.web.Application(handlers =urls,**SETTINGS)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
 
if __name__ == "__main__":
    main()
