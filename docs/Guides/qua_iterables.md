---
search:
  boost: 4
---

# Iterables & Auto-Streaming

Writing QUA programs around sweeps usually means the same boilerplate every time: a loop variable, a stream, a `save()` inside the loop, and a {{f("qm.qua.stream_processing")}} block to buffer and reduce the result. Every new sweep axis adds another place to keep in sync.

The iterables and auto-streaming APIs replace those pieces. An iterable describes a sweep axis in one expression. {{f("qm.qua.declare_with_stream")}} ties a QUA variable to a stream and handles the save, the buffer, and (if you ask) the average automatically.

## At a glance

The same experiment, written both ways:

=== "Without iterables and auto-streaming"

    ```python
    n_shots = 1000
    freq_start, freq_stop, freq_step = -100_000_000, 100_000_000, 10_000_000
    N_freq = len(range(freq_start, freq_stop, freq_step))

    with program() as prog:
        n_shot = declare(int)
        freq = declare(int)
        I, Q = declare(fixed), declare(fixed)
        I_stream, Q_stream = declare_output_stream(), declare_output_stream()

        with for_(n_shot, 0, n_shot < n_shots, n_shot + 1):
            with for_(freq, freq_start, freq < freq_stop, freq + freq_step):
                update_frequency("qubit_xy", freq)
                play("pi_pulse", "qubit_xy")
                measure(
                    "readout", "rr",
                    demod.full("cos", I),
                    demod.full("sin", Q),
                )
                save(I, I_stream)
                save(Q, Q_stream)

        with stream_processing():
            I_stream.buffer(N_freq).map(FUNCTIONS.average()).save("I")
            Q_stream.buffer(N_freq).map(FUNCTIONS.average()).save("Q")
    ```

=== "With iterables and auto-streaming"

    ```python
    shots = QuaIterableRange("shots", 1000)
    frequencies = QuaIterable("frequency", np.arange(-100_000_000, 100_000_000, 10_000_000))

    with program() as prog:
        for shot in shots:
            for freq in frequencies:
                update_frequency("qubit_xy", freq)
                play("pi_pulse", "qubit_xy")

                I = declare_with_stream(fixed, "I", average_axes=["shots"])
                Q = declare_with_stream(fixed, "Q", average_axes=["shots"])
                measure(
                    "readout", "rr",
                    demod.full("cos", I),
                    demod.full("sin", Q),
                )
    ```

## Why this is simpler

Both programs run the same experiment. The auto-streaming version is shorter, but the bigger win is how it reads.

In the manual version, the experiment lives in three places. Loop variables and streams are declared at the top. The measurement happens in the middle. The reduction logic sits in a separate `stream_processing()` block at the bottom. To know what shape `I` and `Q` come back as, you read all three and piece it together yourself. Add a new sweep axis and you touch every one of those places.

In the auto-streaming version, the structure is local. The `for` loops *are* the data layout. `average_axes=["shots"]` sits right next to the variable being averaged, so the intent is visible where the variable is declared. Adding a sweep is one more `for` line, and the buffer shape follows automatically.

Concretely, the auto-streaming version drops:

- The manual loop variable declarations
- The stream declarations and `save()` calls
- The whole `stream_processing()` block
- The `N_freq = len(range(...))` axis-size computation, which is easy to get out of sync with the loop bounds

Instead you write one named iterable per sweep and one `declare_with_stream` per output.

The trade-off is flexibility. Auto-streaming assumes the result layout matches the loop layout. For anything outside that pattern (arithmetic between streams, histograms, non-aligned zips), you drop back to manual {{f("qm.qua.stream_processing")}}.

## When to use this

Use these APIs when the result layout follows the loop structure. Common cases: measurements inside `frequency × shots`, parameter sweeps with averaged repetitions, multi-element scans.

Use manual {{f("qm.qua.stream_processing")}} when you need something outside that pattern: explicit `buffer()` reshaping, arithmetic between streams, histograms, zipping non-aligned streams, or any custom pipeline composition. See the [Stream Processing guide](stream_proc.md) for those cases.

## Imports

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

## Iterables

An iterable describes one sweep axis. Two families exist:

- **QUA iterables** ({{f("qm.qua.extensions.qua_iterators.QuaIterable")}}, {{f("qm.qua.extensions.qua_iterators.QuaIterableRange")}}) build loops that run on the QOP. They map to {{f("qm.qua.for_")}} or {{f("qm.qua.for_each_")}}.
- **Native iterables** ({{f("qm.qua.extensions.qua_iterators.NativeIterable")}}, {{f("qm.qua.extensions.qua_iterators.NativeIterableRange")}}) iterate in Python on the host. Use them for sweeps over non-numeric values like element names, or for numeric sweeps you want to keep on the host. They do not create QUA loop variables and cannot be averaged with `average_axes`.

Every iterable carries a name. That name becomes the axis identifier used by auto-buffering and by `average_axes`. Use named native iterables instead of plain Python iterators when the host-side axis should still participate in {{f("qm.qua.extensions.qua_iterators.QuaProduct")}}, {{f("qm.qua.extensions.qua_iterators.QuaZip")}}, or stream naming.

### `QuaIterableRange`

For numeric ranges that map to {{f("qm.qua.for_")}}.

```python
for tau in QuaIterableRange("tau", 20, 120, 20):
    wait(tau)
```

### `QuaIterable`

For explicit numeric value lists. Uniform ranges are optimized to {{f("qm.qua.for_")}}; non-uniform value lists fall back to {{f("qm.qua.for_each_")}}.

```python
for amp_scale in QuaIterable("amp_scale", np.linspace(0.2, 1.0, 5)):
    play("x90" * amp(amp_scale), "q1")
```

### `NativeIterableRange`

For Python-side numeric ranges.

```python
for amp_scale in NativeIterableRange("amp_scale", 0.1, 1.0, 0.05):
    play("x90" * amp(amp_scale), "q1")
```

### `NativeIterable`

For Python-side loops over explicit values, including non-numeric ones such as element names or device labels.

```python
for element in NativeIterable("element", ["q1", "q2"]):
    play("x180", element)
```

## Combining iterables

### `QuaProduct`: nested loops in a flat list

{{f("qm.qua.extensions.qua_iterators.QuaProduct")}} expands a list of iterables into nested loops, similar to Python's `itertools.product`. List order is loop nesting order: the first iterable becomes the outermost loop. Reordering the list changes the nesting and the auto-buffer axis order without rewriting nested `for` blocks.

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

This keeps the body flat and lets you reorder sweeps by editing the list.

### `QuaZip`: aligned iteration

{{f("qm.qua.extensions.qua_iterators.QuaZip")}} combines iterables position-by-position. All iterables in a single zip must be of the same kind:

- all QUA iterables, or
- all native iterables

By default, the zip name is formed by joining the iterable names. Pass `name=` for a shorter handle, especially when nesting inside `QuaProduct`.

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

When a zip is nested inside `QuaProduct`, give it a `name` so its fields are accessible from the product result:

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

## Auto-streaming with `declare_with_stream`

{{f("qm.qua.declare_with_stream")}} creates a QUA variable and attaches the matching save logic in a single call. Any value written into that variable (assignments, loop updates, measurement outputs) is saved automatically to the named stream.

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

`auto_buffer` defaults to `True` and `average_axes` defaults to `None`.

### Buffering

Stream items come out of the OPX as a flat sequence, in the order they were saved. *Buffering* is the step in stream processing that folds that sequence back into an N-dimensional array aligned with the sweep. Without it, the result for `I` would be a 1D array of length `N_shots × N_frequencies × N_taus`, and you would have to reshape it yourself on the client. In a manual `stream_processing()` block you do this with a chain of `.buffer(N_outer, ..., N_inner)` calls, with the sizes matching the loop bounds.

With `auto_buffer=True` (the default), `declare_with_stream` reads the active QUA iterables at the call site, picks up each name and size, and writes that `buffer(...)` call for you. Add a loop and the buffer grows an axis. Reorder the loops and the axis order follows. Native iterables don't add to the buffer shape; each Python-side position becomes its own result stream instead (see [Stream names inside native iterables](#stream-names-inside-native-iterables)). Set `auto_buffer=False` when you want `declare_with_stream` to handle the per-write save but plan to reshape in your own `stream_processing()` block.

### Averaging

`average_axes=[...]` averages over named QUA loop axes while auto-buffering:

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

`I` keeps the `frequency` and `tau` axes and averages over `shots`. `Q` keeps only `frequency` and averages over both `shots` and `tau`.

!!! Note
    `average_axes` requires `auto_buffer=True`.

!!! Note
    `average_axes` can only reference QUA loop names, and averaged axes must be outermost in the loop nesting order. Once a non-averaged QUA axis is kept, later inner QUA axes cannot be averaged.

### Stream names inside native iterables

When `declare_with_stream` runs with `auto_buffer=True` inside a native iterable, the native iteration index is appended to the stream name. A stream named `I` inside `NativeIterable("element", ["q1", "q2"])` produces two result handles, `I_0` and `I_1`. Each Python-side position gets its own handle, and the raw value (which might be a non-numeric label like `"q1"`) does not end up in the result name.
