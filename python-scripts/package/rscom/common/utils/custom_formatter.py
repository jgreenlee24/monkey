from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """This class will allow us to customize the levelname record and rename it to level which Datadog is looking for for log levels."""
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = log_record['levelname']
        del log_record['levelname']
