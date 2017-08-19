import sys
from conf import LazySettings
sys.modules["settings"] = LazySettings()
