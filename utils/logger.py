# utils/logger.py
from functools import wraps
from flask import request, g
from models import AuditLog, db
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import traceback

def log_action(user_id, action, target_type, target_id, status, ip_address=None, extra_data=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        status=status,
        ip_address=ip_address or request.remote_addr,
        extra_data=extra_data
    )
    db.session.add(log)
    db.session.commit()

def log_audit(action, target_type=None):
    """
    Use as a decorator to automatically log route actions.
    Example:
        @log_audit(action="Create Event", target_type="Event")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = None
            target_id = None
            status = "Success"
            ip = request.remote_addr
            extra_data = None

            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()

                response = func(*args, **kwargs)

                # Optionally extract target_id from the response or kwargs
                if isinstance(response, tuple) and isinstance(response[0], dict):
                    body = response[0]
                    target_id = body.get("id") or kwargs.get("id")

                return response

            except Exception as e:
                status = "Failed"
                extra_data = traceback.format_exc()
                raise e

            finally:
                log = AuditLog(
                    user_id=user_id,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    status=status,
                    ip_address=ip,
                    extra_data=extra_data
                )
                db.session.add(log)
                db.session.commit()

        return wrapper
    return decorator
