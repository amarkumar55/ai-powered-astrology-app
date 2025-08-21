# admin_panel/log_handler.py

import logging
import traceback

class DBLogHandler(logging.Handler):
    def emit(self, record):
        try:
            # Lazy import here (inside the method)
            from admin_panel.models import AppLog

            AppLog.objects.create(
                level=record.levelname,
                message=record.getMessage(),
                traceback=getattr(record, 'traceback', traceback.format_exc() if record.exc_info else None)
            )
        except Exception:
            # Avoid recursive logging errors
            pass
