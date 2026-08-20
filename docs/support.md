# Feedback and support

<!-- % For bug reports, technical support and feature requests, please use `the support website <https://quantum-machines.atlassian.net/servicedesk/customer/portals>`_. -->

Join us in our QUA Discord server {{ discord }}. You are welcome to ask questions, suggest features and share your experience!

## Serializing QUA Programs

Generating a serialized version of a QUA program can be very helpful in debugging your code and control flow.
Serialization will resolve Python control flow, make parametrization explicit, and transform your program into a standardized format.

It is possible to serialize a QUA program and a config file using these commands:

[comment]: <> (!!! Note)

[comment]: <> (    Make sure to always update your qua package before you serialize with `pip install -U qm-qua`.)

```python
from qm import generate_qua_script

qmm = QuantumMachinesManager(...)  # Optional - Used for config validation

config = {}

with program() as prog:
    ...

sourceFile = open('debug.py', 'w')
print(generate_qua_script(prog, config), file=sourceFile) 
sourceFile.close()
```

This code will create a file, `debug.py`, which is a standalone runnable serialized QUA program.

See the [Serialization API](API_references/serialization.md) reference for the full signature of {{f("qm.serialization.generate_qua_script.generate_qua_script")}} and the related {{f("qm.serialization.generate_qua_script.assert_programs_are_equal")}}.
