#PyToolBag
Simple tools that I use for my python applications.



## ResWatcher

To watch RAM and CPU consumption.

```
/res_watcher
```

Usage:

```python
from res_watcher import ResWatcher

def main():
  # All amazing things that you wanna do
  pass

if __name__ == '__main__':
  watcher = ResWatcher()
  watcher.start()
  main()
  watcher.stop()

```
