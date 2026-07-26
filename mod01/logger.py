import logging
from env_parser import EnvStore
store = EnvStore()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SensitiveFilter(logging.Filter):
    def filter(self, record):
        if any(word in str(record.msg).lower() for word in store.SENSITIVE):
            record.msg = "[REDACTED]"
        return True


handler = logging.FileHandler("logs/app.log")
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s"))
handler.addFilter(SensitiveFilter())
logger.addHandler(handler)

if __name__ == "__main__":
    logger.info("user login succeede")
    logger.warning("config missing db_password, using default")
