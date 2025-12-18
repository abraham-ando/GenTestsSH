import inspect
from agent_framework.devui import DevServer, serve

print("DevServer init:", inspect.signature(DevServer.__init__))
print("serve signature:", inspect.signature(serve))
