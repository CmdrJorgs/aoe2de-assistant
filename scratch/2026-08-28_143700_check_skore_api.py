import inspect
import skore

print("skore version:", skore.__version__)
print("Project init signature:", inspect.signature(skore.Project.__init__))
print("evaluate signature:", inspect.signature(skore.evaluate))
