import traceback

def error_handler(func):
    async def wrapper(*args, **kwargs):
        base = args[0]
        logger = base.logger
        try:
            data = await func(*args, **kwargs)
            return data
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(e)
            return
    return wrapper


def send_cont_error_handler(func):
    async def wrapper(*args, **kwargs):
        app = args[0]
        logger = app.container.logger
        try:
            data = await func(*args, **kwargs)
            return data
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(e)
            return
    return wrapper
