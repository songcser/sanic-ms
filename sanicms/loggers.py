import os
import sys
import logging
import opentracing
import datetime
import aiohttp
import time
import json
import traceback as tb
import functools
import socket


from sanic.request import Request
from basictracer.recorder import SpanRecorder

from sanicms import utils

STANDARD_ANNOTATIONS = {
    'client': {'cs':[], 'cr':[]},
    'server': {'ss':[], 'sr':[]},
}
STANDARD_ANNOTATIONS_KEYS = frozenset(STANDARD_ANNOTATIONS.keys())

_logger = logging.getLogger('zipkin')

def _default_json_default(obj):
    """
    Coerce everything to strings.
    All objects representing time get output as ISO8601.
    """
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    else:
        return str(obj)

class JsonFormatter(logging.Formatter):
    def __init__(self,
                 fmt=None,
                 json_cls=None,
                 json_default=_default_json_default):
        if fmt is not None:
            self._fmt = json.loads(fmt)
        else:
            self._fmt = {}

        self.json_default = json_default
        self.json_cls = json_cls
        self.defaults = {}
        try:
            self.defaults['hostname'] = socket.gethostname()
        except:
            pass

    def format(self, record):
        fields = record.__dict__.copy()
        if 'args' in fields and fields['args']:
            data = fields.pop('args')
        else:
            data = fields

        msg = fields.pop('msg')
        if 'message' not in data:
            data['message'] = msg
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if 'exc_text' in fields and fields['exc_text']:
            exception = fields.pop('exc_text')
            data.update({
                'exception':  exception,
            })
        elif exc_type and exc_value and exc_traceback:
            formatted = tb.format_exception(exc_type, exc_value, exc_traceback)
            data.update({
                'exception': formatted,
            })

        name = fields['name']
        data.update({
            'index': name,
            'document_type': name,
            '@version': 1,
        })
        if '@timestamp' not in data:
            now = datetime.datetime.utcnow()
            timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (now.microsecond / 1000) + "Z"
            data.update({
               '@timestamp': timestamp
            })
        logr = self.defaults.copy()
        logr.update(data)
        return json.dumps(logr, default=self.json_default, cls=self.json_cls, ensure_ascii=False)

    def _build_fields(self, defaults, fields):
        """Return provided fields including any in defaults
        """
        return dict(list(defaults.get('@fields', {}).items()) + list(fields.items()))

def gen_span(request, name):
    span = opentracing.tracer.start_span(operation_name=name,
                             child_of=request['span'])
    span.log_kv({'event': 'server'})
    return span

def logger(type=None, category=None, detail=None, description=None,
           tracing=True, level=logging.INFO, *args, **kwargs):
    def decorator(fn=None):
        @functools.wraps(fn)
        async def _decorator(*args, **kwargs):
            request = args[0] if len(args) > 0 and isinstance(args[0], Request) else None
            log = {
                'category': category or request.app.name if request else '',  #服务名
                'fun_name': fn.__name__,
                'detail': detail or fn.__name__,  # 方法名或定义URL列表
                'log_type': type or 'method',
                'description': description if description else fn.__doc__ if fn.__doc__ else '',
            }
            span = None
            if request and tracing:
                #oldspan = request['span']
                span = gen_span(request, fn.__name__)
                span.tags.update(log)
                #request['span'] = span
                log.update({
                    'start_time': span.start_time,
                    'trace_id': span.context.trace_id
                })
            else:
                start_time = time.time()
                log.update({
                    'start_time': start_time,
                })
            log.update({
                "args": ",".join([str(a) for a in args]) if isinstance(args, (list, tuple)) else str(args),
                "kwargs": kwargs.copy() if kwargs else {},
            })
            try:
                exce = False
                res = await fn(*args, **kwargs)
                #request['span'] = oldspan
                return res
            except Exception as e:
                exce = True
                raise e
            finally:
                try:
                    if request and tracing:
                        span.set_tag(
                            'component', '{}-{}'.format(request.app.name, log['log_type']))
                        span.finish()
                        log.update({
                            'duration': span.duration,
                            'end_time': span.start_time + span.duration
                        })
                    else:
                        end_time = time.time()
                        log.update({
                            'end_time': end_time,
                            'duration': end_time - start_time
                        })
                    if exce:
                        _logger.exception('{} has error'.format(fn.__name__), log)
                    else:
                        _logger.info('{} is success'.format(fn.__name__), log)
                except Exception as e:
                    _logger.excepion(e)

        _decorator.detail = detail
        _decorator.description = description
        _decorator.level = level
        return _decorator
    decorator.detail = detail
    decorator.description = description
    decorator.level = level
    return decorator

class AioReporter(SpanRecorder):
    def __init__(self, queue=None):
        self.queue = queue

    def record_span(self, span):
        self.queue.put_nowait(span)
