import logging

import ecs_logging

# Get the Logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
logger.addHandler(handler)

# Add an ECS formatter to the Handler
fileHandler = logging.FileHandler('logs/search-dashboard.app.json')
fileHandler.setFormatter(
    ecs_logging.StdlibFormatter(extra={'event.dataset': 'SearchDashboard'})
)
logger.addHandler(fileHandler)
