---
search:
  boost: 4
---

# Sweep Program

Sweep Program APIs reduce the boilerplate required when a QUA program contains repeated sweeps, nested loops, and result streaming.
They provide iterator helpers for loop construction and automatic streaming with the matching save and buffering logic for declared variables.

## Import paths

{{f("qm.qua.declare_with_stream")}} and the iterator helpers are available from `qm.qua`.

```python
import numpy as np

from qm.qua import (
    declare_with_stream,
    NativeIterable,
    NativeIterableRange,
    QuaIterable,
    QuaIterableRange,
    QuaProduct,
    QuaZip,
)
```

## QUA iterables and native iterables

{{f("qm.qua.extensions.qua_iterators.QuaIterableRange")}} and {{f("qm.qua.extensions.qua_iterators.QuaIterable")}} build loops inside the QUA program.
Use them when the sweep should run on the QOP as a {{f("qm.qua.for_")}} or {{f("qm.qua.for_each_")}} loop.

{{f("qm.qua.extensions.qua_iterators.NativeIterableRange")}} and {{f("qm.qua.extensions.qua_iterators.NativeIterable")}} iterate in Python.
Use them when the loop chooses between Python-side values such as element names, device labels, or configuration variants.
Use them instead of plain Python iterators when the Python-side axis should still participate in Sweep Program composition.
A named native iterable can be combined inside {{f("qm.qua.extensions.qua_iterators.QuaProduct")}} and {{f("qm.qua.extensions.qua_iterators.QuaZip")}}, and with {{f("qm.qua.declare_with_stream")}} its current value is reflected in the generated stream name.
Native iterables do not create QUA loop variables, and they cannot be averaged with `average_axes`.

### `QuaIterableRange`

Use {{f("qm.qua.extensions.qua_iterators.QuaIterableRange")}} for numeric ranges that map to {{f("qm.qua.for_")}}.

```python
for tau in QuaIterableRange("tau", 20, 120, 20):
    wait(tau)
```

### `QuaIterable`

Use {{f("qm.qua.extensions.qua_iterators.QuaIterable")}} for explicit numeric value lists.
If the values form a uniform range, the SDK can optimize the loop to {{f("qm.qua.for_")}}.
Otherwise it uses {{f("qm.qua.for_each_")}}.

```python
for amp_scale in QuaIterable("amp_scale", np.linspace(0.2, 1.0, 5)):
    play("x90" * amp(amp_scale), "q1")
```

### `NativeIterableRange`

Use {{f("qm.qua.extensions.qua_iterators.NativeIterableRange")}} when the loop stays in Python but follows a simple numeric range.
They do not create QUA loop variables, and they cannot be averaged with `average_axes`.

```python
for amp_scale in NativeIterableRange("amp_scale", 0.1, 1.0, 0.05):
    play("x90" * amp(amp_scale), "q1")
```

### `NativeIterable`

Use {{f("qm.qua.extensions.qua_iterators.NativeIterable")}} for Python-side loops over explicit values.
They do not create QUA loop variables, and they cannot be averaged with `average_axes`.

```python
for element in NativeIterable("element", ["q1", "q2"]):
    play("x180", element)
```

## Combining iterables

{{f("qm.qua.extensions.qua_iterators.QuaProduct")}} expands a list of iterables into nested loops, similarly to Python's `itertools.product`.
The list order is the loop nesting order, so the first iterable becomes the outermost loop.
Reordering that list changes the nesting order and the auto-buffer axis order without rewriting nested `for` blocks.

```python
for args in QuaProduct(
    [
        QuaIterableRange("shot", 100),
        NativeIterable("element", ["q1", "q2"]),
        QuaIterable("amp", [0.2, 0.5, 0.8]),
    ]
):
    play("x90" * amp(args.amp), args.element)
```

{{f("qm.qua.extensions.qua_iterators.QuaZip")}} combines iterables position-by-position.
All iterables in a single zip must be of the same kind:

- all QUA iterables
- all native iterables

By default, the zip name is formed from the joined iterable names.
Provide `name=` when you want a shorter handle or when the zip is nested inside {{f("qm.qua.extensions.qua_iterators.QuaProduct")}} for more convenient access.

```python
for pair in QuaZip(
    [
        QuaIterable("amp", [0.2, 0.5, 0.8]),
        QuaIterable("tau", [16, 32, 64]),
    ]
):
    play("x90" * amp(pair.amp), "q1")
    wait(pair.tau)
```

If {{f("qm.qua.extensions.qua_iterators.QuaZip")}} is used inside {{f("qm.qua.extensions.qua_iterators.QuaProduct")}}, give the zip a `name` so its fields can be accessed from the product result.

```python
shots = QuaIterableRange("shot", 100)
qubits = NativeIterable("qubit", ["q1", "q2"])
amps = QuaIterable("amp", np.linspace(0.1, 1.0, 10))
taus = QuaIterableRange("tau", 20, 120, 20)

for args in QuaProduct(
    [
        shots,
        qubits,
        QuaZip([amps, taus], name="drive"),
    ]
):
    play("pulse" * amp(args.drive.amp), args.qubit)
    wait(args.drive.tau)
```

## Automatic streaming

{{f("qm.qua.declare_with_stream")}} creates a QUA variable and attaches the matching save logic to it.
Assignments, loop updates, and measurement outputs written into that variable are saved automatically with the given stream name.

```python
I = declare_with_stream(fixed, "I")
Q = declare_with_stream(fixed, "Q")

measure(
    "readout",
    "rr",
    demod.full("cos", I),
    demod.full("sin", Q),
)
```

Use this when the result stream should follow the declared variable through the program without manually calling {{f("qm.qua.save")}} and {{f("qm.qua.declare_stream")}}.
`auto_buffer` defaults to `True`, and `average_axes` defaults to `None`.

### Buffering and averaging

By default, {{f("qm.qua.declare_with_stream")}} derives the buffer structure from the enclosing named QUA loops.
Set `auto_buffer=False` when you want automatic saving without generated buffering.

Use `average_axes=[...]` to average over named QUA loop axes while auto-buffering:

```python
shots = QuaIterableRange("shots", 100)
frequencies = QuaIterable("frequency", [1e6, 2e6, 3e6, 5e6])
taus = QuaIterable("tau", [20, 44, 60])

with program() as prog:
    for shot in shots:
        for freq in frequencies:
            for tau in taus:
                I = declare_with_stream(
                    fixed,
                    "I",
                    auto_buffer=True,
                    average_axes=["shots"],
                )
                Q = declare_with_stream(
                    fixed,
                    "Q",
                    auto_buffer=True,
                    average_axes=["shots", "tau"],
                )
                wait(tau)
                measure(
                    "readout",
                    "rr",
                    demod.full("cos", I),
                    demod.full("sin", Q),
                )
```

In this example, the saved result keeps the `frequency` and `tau` axes and averages over `shots`.

!!! Note
    `average_axes` can only be used with `auto_buffer=True`.

!!! Note
    `average_axes` can only reference QUA loop names, and averaged axes must be outermost in the QUA loop nesting order.
    Once a non-averaged QUA axis is kept, later inner QUA axes cannot be averaged.

### Native iterable stream names

When {{f("qm.qua.declare_with_stream")}} is used with `auto_buffer=True` inside native iterables, the native iteration index is appended to the stream name.
This lets different Python-side sweep positions produce separate result handles without embedding the raw Python values in the result name.

For example, a stream name of `I` inside {{f("qm.qua.extensions.qua_iterators.NativeIterable")}} over `["q1", "q2"]` produces result names such as `I_0` and `I_1`.

## When to use manual stream processing

Use Sweep Program APIs when the loop structure and the result layout follow the same sweep axes.

Use manual {{f("qm.qua.stream_processing")}} when you need custom operators such as explicit `buffer()`, `zip()`, arithmetic between streams, histogramming, or nonstandard pipeline composition.
See the [Stream Processing guide](stream_proc.md) and the [Sweep Program API reference](../API_references/qua/sweep_program.md) for details.
