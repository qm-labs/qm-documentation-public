---
search:
  boost: 1.5
---

# Serialization API

## Program

The object returned by the [`program`][qm.qua.program] context manager. It can be serialized
to and from a protobuf binary for storage or transfer.

::: qm.program.program.Program
    options:
        heading_level: 3
        show_root_full_path: false

## Script Generation and Comparison

Functions for turning a `Program` into a standalone Python script, and for comparing two programs
for structural equality.

::: qm.serialization.generate_qua_script.generate_qua_script
    options:
        heading_level: 3
        show_root_full_path: false

::: qm.serialization.generate_qua_script.assert_programs_are_equal
    options:
        heading_level: 3
        show_root_full_path: false
