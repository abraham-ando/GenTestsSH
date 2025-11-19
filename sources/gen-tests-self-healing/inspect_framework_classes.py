import agent_framework
import inspect

print("agent_framework members:", dir(agent_framework))

# Try to find relevant classes for Workflow construction
for name, obj in inspect.getmembers(agent_framework):
    if inspect.isclass(obj):
        print(f"Class: {name}")
        try:
            print(f"  Init: {inspect.signature(obj.__init__)}")
        except:
            pass
