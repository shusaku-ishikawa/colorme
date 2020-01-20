import os

k = 'inventory_env'
if k in os.environ and os.environ[k] == 'prod':
   from .prod import *
else:
   from .dev import *
