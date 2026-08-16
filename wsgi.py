# PythonAnywhere WSGI entry point.
# In the Web tab, set this file as your WSGI configuration file,
# or paste its contents into the default WSGI file after replacing USERNAME.

import os
import sys

# >>> Change this to your PythonAnywhere username <<<
USERNAME = "YOUR_USERNAME"
project_home = f"/home/{USERNAME}/aquaviva"

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(project_home, ".env"))
except ImportError:
    pass

from booking_engine import app as application  # noqa: E402
