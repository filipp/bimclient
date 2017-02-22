### Introduction

This is an ArchiCAD BIMServer/Cloud client library for Python.


### System Requirements

- pip install -r requirements.pip
- ArchiCAD BIMServer or BIMCloud


### Usage

Example 1 - get the version number of your BIM server:

```python
import bimclient
s = bimclient.connect('http://bim.example.com:19000')
s.version
```

Check `tests.py` for more examples.
