import logging
import os

import daiquiri


level_name = os.environ.get("DEBUG", "INFO")
level = getattr(logging, level_name)
daiquiri.setup(level=level, outputs=("stderr",))
