

def _default_json_default(obj):
    """
    Coerce everything to strings.
    All objects representing time get output as ISO8601.
    """
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    else:
        return str(obj)


class ConsoleFormatter(logging.Formatter):

    def format(self, record):
        args = record.args
        a = []
        for arg in args:
            if isinstance(arg, Request):
                continue
            a.append(arg)
        record.args = a
        s = super(ConsoleFormatter, self).format(record)
        return s


class LogstashFormatter(logging.Formatter):
    """
    A custom formatter to prepare logs to be
    shipped out to logstash.
    """

    def __init__(self,
                 fmt=None,
                 datefmt=None,
                 json_cls=None,
                 json_default=_default_json_default):
        """
        :param fmt: Config as a JSON string, allowed fields;
               extra: provide extra fields always present in logs
               source_host: override source host name
        :param datefmt: Date format to use (required by logging.Formatter
            interface but not used)
        :param json_cls: JSON encoder to forward to json.dumps
        :param json_default: Default JSON representation for unknown types,
                             by default coerce everything to a string
        """

        if fmt is not None:
            self._fmt = json.loads(fmt)
        else:
            self._fmt = {}

        self.json_default = json_default
        self.json_cls = json_cls
        if 'extra' not in self._fmt:
            self.defaults = {}
        else:
            self.defaults = self._fmt['extra']
        if 'source_host' in self._fmt:
            self.source_host = self._fmt['source_host']
        else:
            try:
                self.source_host = socket.gethostname()
            except:
                self.source_host = ""

    def format(self, record):
        """
        Format a log record to JSON, if the message is a dict
        assume an empty message and use the dict as additional
        fields.
        """

        fields = record.__dict__.copy()

        if 'msg' in fields and 'message' not in fields:
            msg = fields.pop('msg')
            try:
                msg = msg.format(**fields)
            except KeyError:
                pass
            fields['message'] = msg

        if 'exc_info' in fields:
            if fields['exc_info']:
                formatted = tb.format_exception(*fields['exc_info'])
                fields['exception'] = formatted
            fields.pop('exc_info')

        if 'exc_text' in fields and not fields['exc_text']:
            fields.pop('exc_text')

        for arg in fields["args"]:
            if isinstance(arg, Request):
                request = arg
                # fields["request_header"] = request.headers
                fields["request_base_url"] = request.base_url
                fields["request_method"] = request.method
                fields["request_args"] = request.args
                fields["clientip"] = request.remote_addr
                # fields["request_data"] = request.json if request.data else {}
                fields["token"] = request.headers["Soundlife-Token"] if "Soundlife-Token" in request.headers else ''
                fields["device"] = request.headers["Soundlife-Device"] if "Soundlife-Device" in request.headers else ''

        now = datetime.datetime.utcnow()
        base_log = {'@timestamp': now.strftime("%Y-%m-%dT%H:%M:%S") +
                    ".%03d" % (now.microsecond / 1000) + "Z",
                    '@version': 1}
        base_log.update(fields)

        logr = self.defaults.copy()
        logr.update(base_log)

        return json.dumps(logr, default=self.json_default, cls=self.json_cls, ensure_ascii=False)

    def _build_fields(self, defaults, fields):
        """Return provided fields including any in defaults

        >>> f = LogstashFormatter()
        # Verify that ``fields`` is used
        >>> f._build_fields({}, {'foo': 'one'}) == \
                {'foo': 'one'}
        True
        # Verify that ``@fields`` in ``defaults`` is used
        >>> f._build_fields({'@fields': {'bar': 'two'}}, {'foo': 'one'}) == \
                {'foo': 'one', 'bar': 'two'}
        True
        # Verify that ``fields`` takes precedence
        >>> f._build_fields({'@fields': {'foo': 'two'}}, {'foo': 'one'}) == \
                {'foo': 'one'}
        True
        """
        return dict(list(defaults.get('@fields', {}).items()) + list(fields.items()))


class DeployFilter(logging.Filter):

    def filter(self, record):
        deploy = os.environ.get("CONSOLELOG", None)
        if deploy and deploy == "no":
            return False
        else:
            return True


default_logging_config = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'json': {
            'format': ''
        },
        'logstash': {
            'format': '{}',
            '()': LogstashFormatter,
        },
        'console': {
            '()': ConsoleFormatter
        }
    },
    'filters': {
        "deployFilter": {
            '()': DeployFilter,
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'filters': ['deployFilter']
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOGPATH, 'logs/file.log'),
            'maxBytes': 1024000,
            'backupCount': 10,
        },
        'sql': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOGPATH, 'logs/sql.log'),
            'maxBytes': 1024000,
            'backupCount': 10,
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'logstash',
            'filename': os.path.join(LOGPATH, 'logs/info.log'),
            'maxBytes': 1024000,
            'backupCount': 10,
        },
        'app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'logstash',
            'filename': os.path.join(LOGPATH, 'logs/app_info.log'),
            'maxBytes': 1024000,
            'backupCount': 10,
        }
    },
    'loggers': {
        'root': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}
