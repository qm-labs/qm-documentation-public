# NVQLink & CUDA-Q

**Quick links:** [Overview](#overview) · [Roles](#roles)
· [Prerequisites](#prerequisites) · [Installation](#installation)
· [Usage](#usage) · [Troubleshooting & Logging](#troubleshooting-logging)
· [Examples](#examples) · [Further resources](#further-resources)

## Overview

**QM Backend** is the layer that lets you run high-level quantum
programs written in [NVIDIA CUDA-Q](https://developer.nvidia.com/cuda-q) on a
OPX1000 controller. It implements Quantum Machines' side of
[NVIDIA NVQLink](https://www.nvidia.com/en-us/solutions/quantum-computing/nvqlink/), the
open architecture for real-time orchestration between quantum and classical
computing resources — see the
[Quantum Machines NVQLink integration announcement](https://www.quantum-machines.co/press-release/quantum-machines-announces-nvidia-nvqlink-integration-extending-real-time-quantum-classical-computing-solution/)
for background on the partnership.

QM Backend consists of three services:

| Service | Role |
|---|---|
| `config-server` | Stores the device's **QUAM config** (wiring + gate implementations). |
| `ir-transpiler` | **Transpiles** gate-level programs into pulse-level QUA, using the config. |
| `cudaq-frontend` | Accepts **CUDA-Q** programs and drives transpilation + execution. |

These services run on a **dedicated QM Backend host**, separate from the QOP / OPX1000
device, which executes the resulting pulse program on the hardware.

![NVQLink / CUDA-Q data flow: a calibrator publishes the QUAM config to the
config-server; a client submits CUDA-Q programs to the cudaq-frontend, which
authenticates and fetches qubit-allocation config from the config-server,
transpiles the program via the ir-transpiler (which exchanges config and gates
with the config-server), and runs the job on the OPX1000 controller, which
drives the QPU below it. The config-server, ir-transpiler, and cudaq-frontend all
run together on a dedicated QM Backend host, separate from the OPX1000 controller.
A separate accelerator server, with the OPNIC card and a GPU/CPU as physical
devices and the OPNIC bridge (`cudaq-realtime`) as its service, connects
directly to the OPX1000 controller over the low-latency OPNIC
link.](assets/nvqlink_cudaq_flow.svg)

!!! Note "Relation to the OPNIC Hybrid Link"
    QM Backend's CUDA-Q path (publish config → submit program → transpile → run) does
    **not** go through the OPNIC link — `cudaq-frontend` talks directly to the
    OPX1000 controller. The OPNIC link is exercised at runtime when a kernel
    uses `cudaq::device_call` to invoke classical compute on the accelerator
    server — see [Device Call](#device-call) below and the
    [OPNIC Hybrid Link Guide](OPNIC_Guide.md).

## Roles

| Role | Responsibility | Runs from |
|---|---|---|
| **Calibrator** | Publishes the QUAM config (device model + gate macros) to `config-server`. | The calibrator machine. |
| **Classical Code Developer** | Authors, compiles, deploys, and runs CPU/GPU device calls. | The accelerator server. |
| **CUDA-Q Developer** | Writes and submits CUDA-Q programs to `cudaq-frontend`. | The client machine. |

The **data flow** is: calibrator → `config-server`; then client →
`cudaq-frontend` → `ir-transpiler` (transpile, fetching config from
`config-server`) → the OPX1000 controller → QPU → results.

## Prerequisites

- A **OPX1000 controller**, updated to a supporting QOP version (>3.7) and
  network-reachable from the QM Backend host.
- A **classical accelerator with OPNIC installed**, connected to the
  OPX1000 controller over the low-latency OPNIC link.
- SSH access to the QM Backend host and to the accelerator server, for
  installing/deploying software and reading logs.
- QM CUDA-Q backend repository - provided by QM


---

## Installation

Download the packages and install the modules by following the installation
instructions that come with the deployment package.

??? "Deployed Machines"

    Five distinct machines can be involved, and installation differs by machine:

    | Machine | Functionality | Installed here |
    |---|---|---|
    | **OPX1000 controller** | Executes the pulse-level program on the hardware and produces measurement results. | Base QOP, updated to a supporting version. |
    | **QM Backend host** | Runs the services that accept CUDA-Q programs, transpile them against the published config, and drive execution on the OPX1000 controller. Can be a dedicated system, or co-located with the accelerator server or the calibrator machine, depending on your deployment. | `config-server`, `ir-transpiler`, `cudaq-frontend`. |
    | **Accelerator server** | Server running classical decoders or device calls, connected to the OPX1000 controller over the low-latency OPNIC link. | OPNIC driver, SDK, and CLI; the OPNIC Bridge daemon (`cudaq-realtime`); your classical RPC handlers (CUDA/C++). |
    | **Calibrator machine** | Where the calibrator builds and publishes the QUAM config describing the device's wiring and gate implementations. | A Python environment with `quam` and `quam_config_generator`. |
    | **Client machine** | Where the CUDA-Q developer writes and submits CUDA-Q programs. | The CUDA-Q client (`cudaq`, `nvq++`). |

    See the [OPNIC Hybrid Link Guide](OPNIC_Guide.md) for the physical connection
    and pairing steps between the accelerator server and the OPX1000 controller.


---

## Usage

### Create and publish config (calibrator)

Run from the **calibrator machine**, which needs `quam` and
`quam_config_generator` installed. Publishing pushes a QUAM
config to `config-server`. There are **three ways**, from most explicit (you
supply the gate macros) to fully automated.

??? "1. From a QuAM machine with implemented gates (macros)"

    Build your QuAM machine with its gate macros already defined (see the
    [QuAM documentation](https://qua-platform.github.io/quam/) on macros). Use the
    **`HLSWQuam`** class as your machine's root (or mirror its structure) so it
    serializes/loads the way `config-server` and `ir-transpiler` expect, then push it
    **as-is** — no gate injection, so you control exactly which gate each qubit/pair
    implements:

    ```python
    from quam_config_generator import generate_and_push_from_machine

    generate_and_push_from_machine(
        quam_machine=machine,                # your QuAM machine, gate macros already attached
        store_url="http://<host>:8050",
        profile="default",
    )
    ```

??? "2. From an existing QUAM state, injecting default gates"

    `generate_and_push` reads a **QUAM root** and adds the **default gate
    implementations to every active qubit and pair** — no hand-authored macros
    needed (the simplest path):

    ```python
    from quam_config_generator import generate_and_push

    generate_and_push(quam_root="/path/to/QUAM_ROOT", store_url="http://<host>:8050", profile="default")
    # add_default_gates_to_all_qubits / _pairs default to True
    ```

    `quam_config_generator` also ships a **CLI** wrapping this same path (generate +
    push from a QUAM root, no code) — the `qm-config-push` console script:

    ```bash
    qm-config-push --quam-root /path/to/QUAM_ROOT --store-url http://<host>:8050 --profile default
    # omit --profile to push every profile found under <quam_root>/config
    # --watch keeps it running, re-pushing on every source-file change (see method 3)
    ```

    **Expected QUAM-root structure** — one **profile** per device (e.g. `default`):

    ```
    <quam_root>/
    ├── config/<profile>/
    │   ├── state.json     # the serialized QuAM machine (qubits, channels, params)
    │   └── wiring.json    # hardware wiring (controllers / FEMs / ports)
    ├── gates/<profile>/
    │   ├── single_qubit_gates.py   # default 1-qubit gate macros
    │   └── two_qubit_gates.py      # default 2-qubit gate macros
    └── quam_classes/<profile>/
        └── <your_pkg>/…            # importable package with your custom QuAM classes
    ```

    - **`config/<profile>/state.json` (+ `wiring.json`)** — your device's QuAM state.
      Its top-level `"__class__"` names your custom QuAM **root class**, which
      subclasses `quam.core.QuamRoot` and declares `active_qubit_names` /
      `active_qubit_pair_names` — the qubits/pairs the default gates are applied to.
    - **`quam_classes/<profile>/<your_pkg>/`** — an importable package providing that
      root class + any custom components the state references. `generate_and_push` adds
      it to the import path for you (from `<quam_root>/quam_classes`, overridable via
      `QUAM_CLASSES`).
    - **`gates/<profile>/*.py`** — the default gate macros: each a subclass of
      `SingleQubitGate` / `TwoQubitGate` (from `quam_config_generator.gates.gate_base`)
      with a `name` and an `apply()` that emits QUA.

??? "3. Watch & auto-push on change (`watch_generate_and_push`)"

    Same as (2) — **same QUAM-root structure** — but it **keeps the server in sync
    while you work**: it pushes once on start, then polls the profile's `config/` +
    `gates/` dirs every `poll_interval` seconds (default 60) and re-runs
    `generate_and_push` whenever a source file changes. It runs on a background
    daemon thread and returns a `ConfigWatcher` — call `.stop()` to end it.

    ```python
    from quam_config_generator import watch_generate_and_push

    watcher = watch_generate_and_push(
        quam_root="/path/to/QUAM_ROOT", store_url="http://<host>:8050", profile="default",
        poll_interval=60,     # seconds between checks
        push_on_start=True,   # push immediately, then on every change
    )
    # ... edit files under config/<profile>/ or gates/<profile>/ to trigger re-pushes ...
    watcher.stop()
    ```

**Verify the config landed** (any of the three):

```bash
curl "http://<host>:8050/version?profile=default"              # -> {"profile":"default","last_updated":…}
curl -o /dev/null -w "%{http_code}\n" \
     "http://<host>:8050/quam/config_and_gates?profile=default"   # -> 200 (what ir-gw fetches)
```

### Generate and run classical kernels (accelerator server)

**This only applies if you intend to use `cudaq::device_call`.** Run from the
**accelerator server**:

**1. CUDA/C++ Device Calls** — author or select the classical kernel(s) which
invokes a decoder, or any classical routine.

#### Device Call

A kernel can call out to a classical compute RPC handler running on the
OPNIC bridge daemon.

> `cudaq::device_call` is only supported from **C++** — there is no Python
> equivalent.

??? "Device Call"

    The client-side kernel chains two `device_call`s — for example, an
    increment, then an add — into the RPC handlers registered above.

    Compile and run on a running client container:

    ```bash
    docker cp your-kernel.cpp <cudaq-client>:/tmp/your-kernel.cpp
    docker exec <cudaq-client> nvq++ --target quantum_machines --quantum_machines-url "http://<host>:8000" --quantum_machines-executor "qpu" --quantum_machines-qubit_mapping_mode "backend" /tmp/your-kernel.cpp -o /tmp/your-kernel
    docker exec <cudaq-client> /tmp/your-kernel
    ```

    **Develop inside the container with VS Code.** For an interactive loop
    (editing, running, debugging with `cudaq` and the target already
    installed), attach VS Code to the running client container instead of
    copying files in and out:

    **1. Install the Dev Containers extension** in VS Code.

    **2. Make sure the client container is running** — either your
    already-running container, or start one yourself (a
    CUDA-Q client image):

    ```bash
    docker run -d --name cudaq-client <your-cudaq-client-image> sleep infinity
    ```

    **3. Attach to it.** Open the Command Palette (`F1`) → **Dev Containers:
    Attach to Running Container…** and pick the client container. VS Code
    opens a window running *inside* it; use **File → Open Folder** (e.g.
    `/tmp` or `/work`) and the integrated terminal to edit and `python3
    your_program.py` right there.

    > If the client container shares a Docker network with `cudaq-frontend`,
    > reach it by service name (e.g. `http://cudaq-frontend:8000`);
    > otherwise use `http://<host>:8000`.

    Notes:

    - **Publish the profile's config first** (see
      [Create and publish config](#create-and-publish-config-calibrator)) —
      otherwise the frontend returns HTTP 500 (no `SystemData` to transpile
      against).
    - `executor="sim"` (the default) uses the gateway's pulse-level
      simulator; it returns well-formed readout but doesn't model gate
      logic, so treat the histogram as a path/shape check, not a physical
      distribution. Set `executor="qpu"` to run on actual hardware instead
      — see the `set_target` options table in
      [Run a CUDA-Q program](#run-a-cuda-q-program-client) below.
    - `api_key` is omitted here — the frontend runs with
      `AUTHENTICATION_MODE=ALLOWED`, so no key is required (pass
      `api_key="…"` only if your frontend enforces it).
    - The available qubits/gates come from the **published config** (e.g.
      the `default` profile's `qP0…`), so the number of qubits your kernel
      allocates (`cudaq.qvector(n)`) must not exceed the qubits the device
      exposes.

**2. Compile and test** — build against `cudaq-realtime`
(`cmake -B build -G Ninja . && cmake --build build`) and run the executable
standalone to confirm it behaves correctly before wiring it to `device_call`.

**3. Generate the function table** — register the RPC handler(s) on the
accelerator server via the NVQLink framework and the OPNIC SDK, so
`device_call` can dispatch to them.

**4. Run classical kernels** — run the built executable **as root**, since
CUDA requires root to create the memory maps the OPNIC bridge uses:

```bash
sudo ./build/<your_executable>
```

### Run a CUDA-Q program (client)

Run from the **client machine**, which needs the CUDA-Q client installed. Point the target at the device's
`cudaq-frontend`; the frontend transpiles the program (via `ir-transpiler`,
using the config you published) and executes it on the device — from either
**Python** or **C++**, below.

**Target options** — same meaning whether set via Python's `set_target()`
keyword arguments or C++'s `--quantum_machines-<argument>` compiler flags:

| Arg | Values | Meaning |
|---|---|---|
| `qubit_mapping_mode` | **`backend`** — qubits assigned by the backend at compile time · `local_get_latest` — the *default* if omitted; the client fetches the latest qubit map and maps locally · `local_file` — read a previously-fetched mapping from a local file | How logical qubits (`q[0]`, `q[1]`, …) map to physical device qubits. |
| `executor` | **`sim`** / `simulator` — the *default* if omitted; runs on the gateway's pulse-level simulator · `qpu` — runs on the actual QPU/hardware · `mock` — a test-only path that doesn't reach the gateway at all | Whether the job actually executes on hardware. |
| `simulator_duration` | an integer, e.g. `3000` | How long the simulated run lasts — only relevant when `executor="sim"`. |
| `api_key` | a string | Only needed if your `cudaq-frontend` deployment enforces authentication. |

#### Python

Write the program to a **file** — `@cudaq.kernel` reads the kernel's source with
`inspect`, so it must be an on-disk file (not stdin / `python -c`):

```python
# bell.py
import cudaq

cudaq.set_target(
    "quantum_machines",
    url="http://<host>:8000",      # the device's cudaq-frontend
    qubit_mapping_mode="backend",  # qubits assigned by the backend at compile time
    executor="sim",                # run on the gateway's simulator
)

@cudaq.kernel
def bell():
    q = cudaq.qvector(2)
    h(q[0])
    x.ctrl(q[0], q[1])

result = cudaq.sample(bell, shots_count=100)
result.dump()                                    # e.g. { 00:52 11:48 }
counts = {bits: result.count(bits) for bits in result}
print(counts)
```

```bash
python3 bell.py
```

**`cudaq.run()` is also supported** (API-wise), alongside `cudaq.sample()` above.
Where `sample()` collects measurements into a histogram, `run()` requires the
kernel to declare an explicit return type/value and returns the **raw per-shot
return values** instead:

```python
@cudaq.kernel
def all_h() -> bool:
    q = cudaq.qvector(5)
    for i in range(4):
        h(q[i])
    mz(q[0])
    return mz(q[1])

cudaq.run(all_h).dump()   # one bool per shot, instead of a bitstring histogram
```

Supported return types: `bool` and `list[bool]` (e.g. return every qubit's
measurement) — with either `qubit_mapping_mode` (`backend`, or the client-side
`local_get_latest`/`local_file` modes).

#### C++

Pass target arguments on the `nvq++` compiler as
`--quantum_machines-<argument> <value>`:

```cpp
// bell.cpp
#include <cudaq.h>

__qpu__ void bell() {
  cudaq::qvector q(2);
  h(q[0]);
  cx(q[0], q[1]);
  mz(q);
}

int main() {
  auto result = cudaq::sample(bell);
  result.dump();                                    // e.g. { 00:512 11:488 }
}
```

```bash
nvq++ --target quantum_machines \
      --quantum_machines-url "http://<host>:8000" \
      --quantum_machines-executor "sim" \
      bell.cpp -o out.x
./out.x
```

!!! Note
    `cudaq::device_call` (see [Device Call](#device-call)) is only supported
    from C++ — there is no Python equivalent.

Notes:

- **Publish the profile's config first** (see
  [Create and publish config](#create-and-publish-config-calibrator)) —
  otherwise the frontend returns HTTP 500 (no config to transpile against).
- The available qubits/gates come from the **published config**, so the
  number of qubits your kernel allocates must not exceed the qubits the
  device exposes.
- **Results** — expected output types and the API for inspecting them:
  `cudaq.sample()` / `cudaq::sample()` return a `SampleResult` histogram
  (`.dump()`, `.count(bitstring)`, or iterate it directly, as shown above);
  `cudaq.run()` returns the raw per-shot return values instead (`bool` or
  `list[bool]`, per the supported types above). Both calls are synchronous
  and return only once the job completes on the device.

---

## Troubleshooting & Logging

### Inspect the service logs

When the frontend returns a 500 or a transpile fails, the cause is in the
service logs **on the QM Backend host** (the client only sees an opaque error):

```bash
ssh root@<host> "journalctl -u cudaq-frontend -n 50 --no-pager"   # or config-server / irgwd / gwd
# follow live (e.g. while you submit a CUDA-Q program):
ssh root@<host> "journalctl -u cudaq-frontend -f"
# all three QM Backend services interleaved by time:
ssh root@<host> "journalctl -u config-server -u irgwd -u cudaq-frontend -n 200 --no-pager"
```

Note: the unit names are the **service** names (`cudaq-frontend`, `config-server`,
`irgwd`), not the package names.

### Logging the published gates

All three push functions (`generate_and_push`, `generate_and_push_from_machine`,
`watch_generate_and_push`, plus `generate_and_push_all`) take a
`log_published_gates` argument for visibility into what got compiled/pushed:

```python
from quam_config_generator import generate_and_push
from quam_config_generator.gates.gate_models import LogPublishedGates

generate_and_push(
    quam_root="/path/to/QUAM_ROOT", store_url="http://<host>:8050", profile="default",
    log_published_gates=LogPublishedGates.GATES,   # or "gates" (a plain string also works)
)
```

| `log_published_gates` | Logs |
|---|---|
| `LogPublishedGates.DEFAULT` (`"default"`, the default) | Nothing. |
| `LogPublishedGates.GATES` (`"gates"`) | Each target's gate names. |
| `LogPublishedGates.GATES_CONTENT` (`"gates_content"`) | Gate names **and** each gate's compiled script body (verbose). |

Same flag on the CLI: `qm-config-push ... --log-published-gates gates`.

---

## Examples

Full worked example of the `cudaq::device_call` flow: a classical kernel on
the accelerator server that registers two RPC handlers — an increment and an
add — and a CUDA-Q client kernel that chains both through `device_call`.
Matches [Generate and run classical kernels](#generate-and-run-classical-kernels-accelerator-server)
and [Device Call](#device-call) above.

#### GPU device call RPC handlers (accelerator server)

??? "main.cu"

    ```cpp
    #include <atomic>
    #include <chrono>
    #include <csignal>
    #include <cstdint>
    #include <cstring>
    #include <cuda_runtime.h>
    #include <iostream>
    #include <sstream>
    #include <string>
    #include <thread>
    #include <exception>

    #include <cuda_runtime.h>

    #include "cudaq/realtime/daemon/bridge/bridge_interface.h"
    #include "cudaq/realtime/daemon/dispatcher/cudaq_realtime.h"
    #include "cudaq/realtime/daemon/dispatcher/dispatch_kernel.cuh"
    #include "opnic/opnic_cudaq_bridge.h"
    #include "opnic/dispatcher/dispatcher.cuh"

    #define CUDA_CHECK(call)                                                       \
      do {                                                                         \
        cudaError_t err = call;                                                    \
        if (err != cudaSuccess) {                                                  \
          std::cerr << "CUDA error in " << __FILE__ << ":" << __LINE__ << ": "     \
                    << cudaGetErrorString(err) << " (" << err << ")" << std::endl; \
          std::exit(EXIT_FAILURE);                                                 \
        }                                                                          \
    } while (0)

    #define CUDAQ_CHECK(call)                                                      \
      do {                                                                         \
        auto err = call;                                                           \
        if (err != CUDAQ_OK) {                                                     \
          std::cerr << "CUDAQ error in " << __FILE__ << ":" << __LINE__ << ": "    \
                    << err << std::endl;                                           \
          std::exit(EXIT_FAILURE);                                                 \
        }                                                                          \
      } while (0)

    __device__ int rpc_add_one_handler(
        const void* input,
        void* output,
        const std::uint32_t arg_len,
        const std::uint32_t max_result_len,
        std::uint32_t* result_len
    )
    {
        printf(
            "  [rpc] enter: input=%p output=%p arg_len=%u max_result_len=%u result_len_ptr=%p\n",
            input,
            output,
            arg_len,
            max_result_len,
            static_cast<void*>(result_len)
        );

        const std::uint32_t* in_data = static_cast<const std::uint32_t*>(input);
        std::uint32_t* out_data = static_cast<std::uint32_t*>(output);
        std::uint32_t len = (arg_len < max_result_len) ? arg_len : max_result_len;
        printf("  [rpc] len=%u\n", len);

        std::uint32_t v = *in_data;
        printf("  [rpc] read value=%u, writing incremented value\n", v);
        *out_data = v + 1;

        printf("  [rpc] writing *result_len\n");
        *result_len = len;
        printf("  [rpc] exit\n");

        return 0;
    }

    __device__ int rpc_add_handler(
        const void* input,
        void* output,
        const std::uint32_t arg_len,
        const std::uint32_t max_result_len,
        std::uint32_t* result_len
    )
    {
        printf(
            "  [rpc add] enter: input=%p output=%p arg_len=%u max_result_len=%u result_len_ptr=%p\n",
            input,
            output,
            arg_len,
            max_result_len,
            static_cast<void*>(result_len)
        );

        const std::uint32_t* in_data = static_cast<const std::uint32_t*>(input);
        std::uint32_t* out_data = static_cast<std::uint32_t*>(output);
        std::uint32_t len = (arg_len < max_result_len) ? arg_len : max_result_len;
        printf("  [rpc add] len=%u\n", len);

        std::uint32_t a = in_data[0];
        std::uint32_t b = in_data[1];
        printf("  [rpc add] read a=%u, b=%u writing incremented value\n", a, b);
        out_data[0] = a + b;

        printf("  [rpc add] writing *result_len\n");
        *result_len = len;
        printf("  [rpc add] exit\n");

        return 0;
    }

    constexpr std::uint32_t RPC_ADD_ONE_FUNCTION_ID =
            cudaq::realtime::fnv1a_hash("rpc_add_one");

    constexpr std::uint32_t RPC_ADD_FUNCTION_ID =
            cudaq::realtime::fnv1a_hash("rpc_add");

    constexpr auto FUNCTION_TABLE_COUNT = 2;

    /// @brief Kernel to populate a cudaq_function_entry_t with the increment
    ///        handler.
    __global__ void init_function_table_kernel(cudaq_function_entry_t* entries)
    {
        if (threadIdx.x == 0 && blockIdx.x == 0)
        {
            entries[0].handler.device_fn_ptr =
                    reinterpret_cast<void*>(&rpc_add_one_handler);
            entries[0].function_id = RPC_ADD_ONE_FUNCTION_ID;
            entries[0].dispatch_mode = CUDAQ_DISPATCH_DEVICE_CALL;
            entries[0].reserved[0] = 0;
            entries[0].reserved[1] = 0;
            entries[0].reserved[2] = 0;

            // Schema: 1 array argument (uint32), 1 array result (uint32)
            entries[0].schema.num_args = 1;
            entries[0].schema.num_results = 1;
            entries[0].schema.reserved = 0;
            entries[0].schema.args[0].type_id = CUDAQ_TYPE_ARRAY_INT32;
            entries[0].schema.args[0].reserved[0] = 0;
            entries[0].schema.args[0].reserved[1] = 0;
            entries[0].schema.args[0].reserved[2] = 0;
            entries[0].schema.args[0].size_bytes = sizeof(int32_t);
            entries[0].schema.args[0].num_elements = 1;
            entries[0].schema.results[0].type_id = CUDAQ_TYPE_ARRAY_INT32;
            entries[0].schema.results[0].reserved[0] = 0;
            entries[0].schema.results[0].reserved[1] = 0;
            entries[0].schema.results[0].reserved[2] = 0;
            entries[0].schema.results[0].size_bytes = sizeof(int32_t);
            entries[0].schema.results[0].num_elements = 1;


            entries[1].handler.device_fn_ptr =
                    reinterpret_cast<void*>(&rpc_add_handler);
            entries[1].function_id = RPC_ADD_FUNCTION_ID;
            entries[1].dispatch_mode = CUDAQ_DISPATCH_DEVICE_CALL;

            // Schema: 2 arguments (uint32), 1 result (uint32)
            entries[1].schema.num_args = 2;
            entries[1].schema.args[0].type_id = CUDAQ_TYPE_INT32;
            entries[1].schema.args[0].size_bytes = sizeof(int32_t);
            entries[1].schema.args[0].num_elements = 1;

            entries[1].schema.args[1].type_id = CUDAQ_TYPE_INT32;
            entries[1].schema.args[1].size_bytes = sizeof(int32_t);
            entries[1].schema.args[1].num_elements = 1;

            entries[1].schema.num_results = 1;
            entries[1].schema.results[0].type_id = CUDAQ_TYPE_INT32;
            entries[1].schema.results[0].size_bytes = sizeof(int32_t);
            entries[1].schema.results[0].num_elements = 1;
        }
    }


    void setup_function_table(cudaq_function_entry_t* d_entries)
    {
        init_function_table_kernel<<<1, 1>>>(d_entries);
        CUDA_CHECK(cudaGetLastError());       // catch async launch-config errors
        CUDA_CHECK(cudaDeviceSynchronize());  // catch in-kernel execution errors
    }

    std::atomic<bool>& bridge_shutdown_flag()
    {
        static std::atomic<bool> flag{false};
        return flag;
    }

    void bridge_signal_handler(int) { bridge_shutdown_flag() = true; }

    int main(int argc, char* argv[])
    {
        try
        {
            signal(SIGINT, bridge_signal_handler);
            signal(SIGTERM, bridge_signal_handler);
            auto& g_shutdown = bridge_shutdown_flag();

            std::cout << "=== OPNIC Bridge ===" << std::endl;

            void* tmp_shutdown = nullptr;
            CUDA_CHECK(
                cudaHostAlloc(&tmp_shutdown, sizeof(int), cudaHostAllocMapped)
            );
            void* tmp_d_shutdown = nullptr;
            CUDA_CHECK(
                cudaHostGetDevicePointer(&tmp_d_shutdown, tmp_shutdown, 0)
            );

            volatile int* d_shutdown_flag = static_cast<volatile int*>(tmp_d_shutdown);
            volatile int* shutdown_flag = static_cast<volatile int*>(tmp_shutdown);

            // CUDA-Q realtime variables
            uint64_t* d_stats = nullptr;
            CUDA_CHECK(cudaMalloc(&d_stats, sizeof(uint64_t)));
            CUDA_CHECK(cudaMemset(d_stats, 0, sizeof(uint64_t)));

            cudaq_function_entry_t* d_function_entries = nullptr;

            cudaq_dispatch_manager_t* manager = nullptr;
            cudaq_dispatcher_t* dispatcher = nullptr;

            cudaq_realtime_bridge_handle_t bridge_handle = nullptr;
            CUDAQ_CHECK(opnic_bridge_create(&bridge_handle, argc, argv));
            std::cout << "Bridge created successfully. Connecting..." << std::endl;

            CUDAQ_CHECK(opnic_bridge_connect(bridge_handle));
            std::cout << "Wiring unified dispatch kernel..." << std::endl;

            *shutdown_flag = 0;
            constexpr int zero = 0;
            CUDA_CHECK(
                cudaMemcpy(const_cast<int*>(d_shutdown_flag), &zero,
                    sizeof(int), cudaMemcpyHostToDevice)
            );

            // Create CUDA-Q dispatcher manager
            CUDAQ_CHECK(cudaq_dispatch_manager_create(&manager));

            cudaq_dispatcher_config_t dispatcher_config{
                .device_id = 0,
                .num_blocks = 1,
                .threads_per_block = 1,
                .num_slots = 0,
                .slot_size = 0,
                .vp_id = 0,
                .kernel_type = CUDAQ_KERNEL_UNIFIED,
                .dispatch_mode = CUDAQ_DISPATCH_DEVICE_CALL
            };

            // Create dispatcher with the above config
            CUDAQ_CHECK(cudaq_dispatcher_create(manager, &dispatcher_config, &dispatcher));

            cudaq_unified_dispatch_ctx_t unified_dispatch{};
            std::cout << "Retrieving the unified dispatch context ..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_get_transport_context(bridge_handle, UNIFIED, &unified_dispatch));

            if (cudaq_dispatcher_set_unified_launch(
                    dispatcher,
                    unified_dispatch.launch_fn,
                    unified_dispatch.transport_ctx
                ) != CUDAQ_OK)
            {
                std::cerr << "ERROR: Failed to set unified launch function" << std::endl;
                return 1;
            }

            // Set up the function table with the increment handler entries
            // Populate the GPU function table with the increment handler entry
            CUDA_CHECK(cudaMalloc(&d_function_entries, sizeof(cudaq_function_entry_t) * FUNCTION_TABLE_COUNT));
            setup_function_table(d_function_entries);

            // Create a function table struct to pass to the dispatcher
            cudaq_function_table_t table{};
            table.entries = d_function_entries;
            table.count = FUNCTION_TABLE_COUNT;

            // Set the function table for the dispatcher
            CUDAQ_CHECK(cudaq_dispatcher_set_function_table(dispatcher, &table));
            CUDAQ_CHECK(opnic_set_function_table(bridge_handle, &table));

            // Set the control variables (shutdown flag and stats pointer) for the
            // dispatcher
            CUDAQ_CHECK(cudaq_dispatcher_set_control(dispatcher, d_shutdown_flag, d_stats));

            // Start the dispatcher (launches the dispatch kernel)
            CUDAQ_CHECK(cudaq_dispatcher_start(dispatcher));
            std::cout << "Dispatch kernel launched" << std::endl;

            // Launch opnic kernels and run
            CUDAQ_CHECK(opnic_bridge_launch(bridge_handle));

            //============================================================================
            // Main run loop
            //============================================================================
            cudaStream_t diag_stream = nullptr;
            CUDA_CHECK(cudaStreamCreateWithFlags(&diag_stream, cudaStreamNonBlocking));

            auto start_time = std::chrono::steady_clock::now();
            uint64_t last_processed = 0;

            while (!g_shutdown)
            {
                auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                            std::chrono::steady_clock::now() - start_time
                        )
                        .count();

                // Progress report every 5 seconds
                if (d_stats && elapsed > 0 && elapsed % 5 == 0)
                {
                    uint64_t processed = 0;
                    cudaMemcpyAsync(&processed, d_stats, sizeof(uint64_t), cudaMemcpyDeviceToHost, diag_stream);
                    cudaStreamSynchronize(diag_stream);

                    if (processed != last_processed)
                    {
                        std::cout << "  [" << elapsed << "s] Processed " << processed << " packets" << std::endl;
                        last_processed = processed;
                    }
                }

                std::this_thread::sleep_for(std::chrono::microseconds(500));
            }

            std::cout << "\n=== Shutting down ===" << std::endl;
            *shutdown_flag = 1;
            __sync_synchronize();
            cudaq_dispatcher_stop(dispatcher);

            uint64_t total_processed = 0;
            cudaq_dispatcher_get_processed(dispatcher, &total_processed);
            std::cout << "  Total packets processed (dispatch RX): "
                    << total_processed << std::endl;

            std::cout << "  Disconnecting bridge..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_disconnect(bridge_handle));
            CUDA_CHECK(cudaFree(d_function_entries));
            CUDA_CHECK(cudaFree(d_stats));

            if (dispatcher)
                cudaq_dispatcher_destroy(dispatcher);

            if (manager)
                cudaq_dispatch_manager_destroy(manager);

            std::cout << "  Destroying bridge..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_destroy(bridge_handle));

            std::cout << "Bridge shut down successfully." << std::endl;
            if (shutdown_flag)
                CUDA_CHECK(cudaFreeHost(const_cast<int *>(shutdown_flag)));
        }
        catch (const std::exception& e)
        {
            std::cerr << "ERROR: " << e.what() << std::endl;
            return 1;
        }
    }
    ```

??? "CMakeLists.txt"

    ```cmake
    cmake_minimum_required(VERSION 3.20)

    project(
            rpc_example
            LANGUAGES C CXX CUDA
    )

    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    find_package(CUDAToolkit REQUIRED)
    find_package(Threads REQUIRED)


    # pass -DCMAKE_PREFIX_PATH=<cudaq-realtime-path>
    find_package(cudaq-realtime CONFIG REQUIRED)
    find_package(opnic-cudaq-bridge REQUIRED)

    add_executable(rpc_example main.cu)
    target_link_libraries(rpc_example PRIVATE
            qm::opnic-cudaq-bridge
            CUDA::cudart
    )
    set_target_properties(rpc_example PROPERTIES
            CUDA_SEPARABLE_COMPILATION ON
            CUDA_RESOLVE_DEVICE_SYMBOLS ON
            CUDA_ARCHITECTURES native
    )
    ```

Registers two RPC handlers with the dispatcher's function table —
`rpc_add_one` (increment) and `rpc_add` (add) — then starts the dispatcher and
runs until interrupted. The function table is also registered with the bridge
via `opnic_set_function_table`, and the setup kernel's launch and execution
errors are checked with `CUDA_CHECK`. Pass `-DCMAKE_PREFIX_PATH=<cudaq-realtime-path>`
to CMake so `find_package(cudaq-realtime)` can locate it. This is the accelerator-side half of
[Generate and run classical kernels](#generate-and-run-classical-kernels-accelerator-server).

#### CPU device call RPC handlers (accelerator server)

CPU-only counterpart to `main.cu`: the same two RPCs (increment and add), but
registered as `CUDAQ_DISPATCH_HOST_CALL` entries and driven by the CPU
dataplane's single-thread host dispatch loop instead of a persistent GPU
kernel. No CUDA device or kernel launch is involved in this program.

??? "main.cpp"

    ```cpp
    //
    // CPU-only counterpart to main.cu: the same two RPCs (increment, add), but
    // registered as CUDAQ_DISPATCH_HOST_CALL entries and driven by the CPU
    // dataplane's single-thread host dispatch loop (cudaq_host_unified_loop)
    // instead of a persistent GPU kernel. No CUDA device or kernel launch is
    // involved anywhere in this program.
    //

    #include <atomic>
    #include <chrono>
    #include <csignal>
    #include <cstdint>
    #include <cstring>
    #include <iostream>
    #include <thread>
    #include <vector>

    #include "cudaq/realtime/daemon/bridge/bridge_interface.h"
    #include "cudaq/realtime/daemon/dispatcher/cudaq_realtime.h"
    #include "cudaq/realtime/daemon/dispatcher/dispatch_kernel_launch.h"
    #include "opnic/opnic_cudaq_bridge.h"

    #define CUDAQ_CHECK(call)                                                      \
      do {                                                                         \
        auto err = call;                                                           \
        if (err != CUDAQ_OK) {                                                     \
          std::cerr << "CUDAQ error in " << __FILE__ << ":" << __LINE__ << ": "    \
                    << err << std::endl;                                           \
          std::exit(EXIT_FAILURE);                                                 \
        }                                                                          \
      } while (0)

    namespace
    {

    // CUDAQ_DISPATCH_HOST_CALL handlers, unlike DEVICE_CALL handlers, are NOT
    // handed stripped arg/result buffers -- the dispatcher passes the raw ring
    // slot straight through (host_dispatcher.cu's invoke_host_call), so the
    // handler itself must parse the RPCHeader (24 bytes) at the front of rx_slot
    // and write an RPCResponse (24 bytes) at the front of tx_slot, with raw
    // payload bytes immediately after each. rx_slot and tx_slot are distinct
    // buffers, so request_id/ptp_timestamp must be echoed explicitly.
    void rpc_increment_handler(const void* rx_slot, void* tx_slot, const size_t slot_size)
    {
        const auto* header = static_cast<const cudaq::realtime::RPCHeader*>(rx_slot);
        if (header->magic != CUDAQ_RPC_MAGIC_REQUEST)
            return;

        const auto* arg = reinterpret_cast<const int32_t*>(
            static_cast<const uint8_t*>(rx_slot) + sizeof(cudaq::realtime::RPCHeader)
        );

        auto* response = static_cast<cudaq::realtime::RPCResponse*>(tx_slot);
        response->magic = CUDAQ_RPC_MAGIC_RESPONSE;
        response->status = 0;
        response->result_len = sizeof(int32_t);
        response->request_id = header->request_id;
        response->ptp_timestamp = header->ptp_timestamp;

        auto* result = reinterpret_cast<int32_t*>(
            static_cast<uint8_t*>(tx_slot) + sizeof(cudaq::realtime::RPCResponse)
        );
        result[0] = arg[0] + 1;
    }

    void rpc_add_handler(const void* rx_slot, void* tx_slot, const size_t slot_size)
    {
        const auto* header = static_cast<const cudaq::realtime::RPCHeader*>(rx_slot);
        if (header->magic != CUDAQ_RPC_MAGIC_REQUEST)
            return;

        const auto* args = reinterpret_cast<const int32_t*>(
            static_cast<const uint8_t*>(rx_slot) + sizeof(cudaq::realtime::RPCHeader)
        );

        auto* response = static_cast<cudaq::realtime::RPCResponse*>(tx_slot);
        response->magic = CUDAQ_RPC_MAGIC_RESPONSE;
        response->status = 0;
        response->result_len = sizeof(int32_t);
        response->request_id = header->request_id;
        response->ptp_timestamp = header->ptp_timestamp;

        auto* result = reinterpret_cast<int32_t*>(
            static_cast<uint8_t*>(tx_slot) + sizeof(cudaq::realtime::RPCResponse)
        );
        result[0] = args[0] + args[1];
    }

    constexpr uint32_t RPC_INCREMENT_FUNCTION_ID = cudaq::realtime::fnv1a_hash("rpc_add_one");
    constexpr uint32_t RPC_ADD_FUNCTION_ID = cudaq::realtime::fnv1a_hash("rpc_add");

    cudaq_function_entry_t make_increment_entry()
    {
        cudaq_function_entry_t entry{};
        entry.handler.host_fn = &rpc_increment_handler;
        entry.function_id = RPC_INCREMENT_FUNCTION_ID;
        entry.dispatch_mode = CUDAQ_DISPATCH_HOST_CALL;
        entry.schema.num_args = 1;
        entry.schema.args[0].type_id = CUDAQ_TYPE_INT32;
        entry.schema.args[0].size_bytes = sizeof(int32_t);
        entry.schema.args[0].num_elements = 1;
        entry.schema.num_results = 1;
        entry.schema.results[0].type_id = CUDAQ_TYPE_INT32;
        entry.schema.results[0].size_bytes = sizeof(int32_t);
        entry.schema.results[0].num_elements = 1;
        return entry;
    }

    cudaq_function_entry_t make_add_entry()
    {
        cudaq_function_entry_t entry{};
        entry.handler.host_fn = &rpc_add_handler;
        entry.function_id = RPC_ADD_FUNCTION_ID;
        entry.dispatch_mode = CUDAQ_DISPATCH_HOST_CALL;
        entry.schema.num_args = 2;
        entry.schema.args[0].type_id = CUDAQ_TYPE_INT32;
        entry.schema.args[0].size_bytes = sizeof(int32_t);
        entry.schema.args[0].num_elements = 1;
        entry.schema.args[1].type_id = CUDAQ_TYPE_INT32;
        entry.schema.args[1].size_bytes = sizeof(int32_t);
        entry.schema.args[1].num_elements = 1;
        entry.schema.num_results = 1;
        entry.schema.results[0].type_id = CUDAQ_TYPE_INT32;
        entry.schema.results[0].size_bytes = sizeof(int32_t);
        entry.schema.results[0].num_elements = 1;
        return entry;
    }

    std::atomic<bool>& bridge_shutdown_flag()
    {
        static std::atomic<bool> flag{false};
        return flag;
    }

    void bridge_signal_handler(int) { bridge_shutdown_flag() = true; }
    } // namespace

    int main(int argc, char* argv[])
    {
        try
        {
            signal(SIGINT, bridge_signal_handler);
            signal(SIGTERM, bridge_signal_handler);
            auto& g_shutdown = bridge_shutdown_flag();

            std::cout << "=== OPNIC CPU Bridge (increment + add) ===" << std::endl;

            volatile int shutdown_flag = 0;
            uint64_t stats = 0;

            cudaq_realtime_bridge_handle_t bridge_handle = nullptr;
            CUDAQ_CHECK(opnic_bridge_create(&bridge_handle, argc, argv));
            std::cout << "Bridge created successfully. Connecting..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_connect(bridge_handle));

            std::vector function_table = {make_increment_entry(), make_add_entry()};
            const cudaq_function_table_t table{
                .entries = function_table.data(),
                .count = static_cast<uint32_t>(function_table.size())
            };

            // Registers with the bridge first -- this is what lets the CPU
            // dataplane size its rx/tx ring slots from the schema below, before
            // it's requested via opnic_bridge_get_cpu_dataplane.
            CUDAQ_CHECK(opnic_set_function_table(bridge_handle, &table));

            cudaq_dispatch_manager_t* manager = nullptr;
            CUDAQ_CHECK(cudaq_dispatch_manager_create(&manager));

            constexpr cudaq_dispatcher_config_t dispatcher_config{
                .device_id = 0,
                .num_blocks = 0,
                .threads_per_block = 0,
                .num_slots = 0, // unused by the CPU dataplane's unified path
                .slot_size = 0, // ditto -- CpuDataplane sizes its own rx/tx slots
                .vp_id = 0,
                .kernel_type = CUDAQ_KERNEL_UNIFIED,
                .dispatch_mode = CUDAQ_DISPATCH_HOST_CALL,
                .dispatch_path = CUDAQ_DISPATCH_PATH_HOST,
            };

            cudaq_dispatcher_t* dispatcher = nullptr;
            CUDAQ_CHECK(cudaq_dispatcher_create(manager, &dispatcher_config, &dispatcher));

            cudaq_cpu_dataplane_t cpu_dataplane{};
            std::cout << "Retrieving the CPU dataplane..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_get_cpu_dataplane(bridge_handle, &cpu_dataplane));
            CUDAQ_CHECK(cudaq_dispatcher_set_cpu_dataplane(dispatcher, &cpu_dataplane));

            CUDAQ_CHECK(cudaq_dispatcher_set_function_table(dispatcher, &table));

            // Plain host pointers suffice here (no cudaHostAlloc/pinned memory
            // needed): the HOST dispatch loop runs on an ordinary CPU thread and
            // touches these via plain std::atomic, not device code.
            CUDAQ_CHECK(cudaq_dispatcher_set_control(dispatcher, &shutdown_flag, &stats));

            CUDAQ_CHECK(cudaq_dispatcher_start(dispatcher));
            std::cout << "Host dispatch loop started" << std::endl;

            CUDAQ_CHECK(opnic_bridge_launch(bridge_handle));

            //============================================================================
            // Main run loop
            //============================================================================
            auto start_time = std::chrono::steady_clock::now();
            uint64_t last_processed = 0;

            while (!g_shutdown)
            {
                const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                    std::chrono::steady_clock::now() - start_time
                ).count();

                if (elapsed > 0 && elapsed % 5 == 0)
                {
                    uint64_t processed = 0;
                    cudaq_dispatcher_get_processed(dispatcher, &processed);
                    if (processed != last_processed)
                    {
                        std::cout << "  [" << elapsed << "s] Processed " << processed << " requests" << std::endl;
                        last_processed = processed;
                    }
                }

                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }

            std::cout << "\n=== Shutting down ===" << std::endl;
            CUDAQ_CHECK(cudaq_dispatcher_stop(dispatcher));

            uint64_t total_processed = 0;
            cudaq_dispatcher_get_processed(dispatcher, &total_processed);
            std::cout << "  Total requests processed: " << total_processed << std::endl;

            std::cout << "  Disconnecting bridge..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_disconnect(bridge_handle));

            CUDAQ_CHECK(cudaq_dispatcher_destroy(dispatcher));
            CUDAQ_CHECK(cudaq_dispatch_manager_destroy(manager));

            std::cout << "  Destroying bridge..." << std::endl;
            CUDAQ_CHECK(opnic_bridge_destroy(bridge_handle));

            std::cout << "Bridge shut down successfully." << std::endl;
        }
        catch (const std::exception& e)
        {
            std::cerr << "ERROR: " << e.what() << std::endl;
            return 1;
        }
    }
    ```

??? "CMakeLists.txt"

    ```cmake
    cmake_minimum_required(VERSION 3.20)

    project(
            rpc_example
            LANGUAGES C CXX CUDA
    )

    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    find_package(CUDAToolkit REQUIRED)
    find_package(Threads REQUIRED)

    # When using manual installation uncomment these lines
    # set(CUDA_FOUND TRUE)
    # add_subdirectory(cuda-quantum/realtime)

    find_package(cudaq-realtime CONFIG REQUIRED)
    find_package(opnic-cudaq-bridge REQUIRED)

    add_executable(rpc_example main.cpp)
    target_link_libraries(rpc_example PRIVATE
            qm::opnic-cudaq-bridge
            CUDA::cudart
    )
    # main.cpp has no CUDA code, but qm::opnic-cudaq-bridge does (compiled with
    # separable compilation) -- these properties are still needed so cmake emits
    # the CUDA device-link step, or linking fails with "undefined reference to
    # __cudaRegisterLinkedBinary_...".
    set_target_properties(rpc_example PROPERTIES
            CUDA_SEPARABLE_COMPILATION ON
            CUDA_RESOLVE_DEVICE_SYMBOLS ON
            CUDA_ARCHITECTURES native
    )
    ```

Unlike `DEVICE_CALL` handlers, `HOST_CALL` handlers are not handed stripped
argument/result buffers: the dispatcher passes the raw ring slot through, so
each handler parses the 24-byte `RPCHeader` at the front of `rx_slot` and
writes a 24-byte `RPCResponse` at the front of `tx_slot`, with the raw payload
immediately after each. Because `rx_slot` and `tx_slot` are distinct buffers,
the handler must echo `request_id` and `ptp_timestamp` explicitly. The
function table is registered with the bridge via `opnic_set_function_table`
before requesting the CPU dataplane, so the dataplane can size its slots from
the schema. The client-side kernel is the same
[CUDA-Q client kernel](#cuda-q-client-kernel-client-machine) used with the GPU
example.

### CUDA-Q client kernel (client machine)

??? "cudaq-side.cpp"

    ```cpp
    /*******************************************************************************
     * Copyright (c) 2026 NVIDIA Corporation & Affiliates.                         *
     * All rights reserved.                                                        *
     *                                                                             *
     * This source code and the accompanying materials are made available under    *
     * the terms of the Apache License 2.0 which accompanies this distribution.    *
     ******************************************************************************/

    // Minimal CUDA-Q example using cudaq::device_call.
    //
    // Compile and run with:
    // nvq++ --target quantum_machines --quantum_machines-url "http://<host_address>:8000" --quantum_machines-executor
    // "qpu" --quantum_machines-qubit_mapping_mode "backend" cudaq-side.cpp -o cudaq-side && ./cudaq-side

    #include <cudaq.h>
    #include <cstdint>
    #include <cstdio>

    extern "C" {
      // Host-side device methods.
      // Linked in for real hardware; this stub lets the example build standalone.

      // Returns: value + 1
      extern std::int32_t rpc_add_one(std::uint32_t value) {
        (void)value;
        return value + 1;
      }

      // Returns: a + b
      extern std::int32_t rpc_add(std::int32_t a, std::int32_t b) {
        return a + b;
      }
    }

    struct simple {
      auto operator()(std::int32_t input) __qpu__ {
        std::int32_t incremented = cudaq::device_call(rpc_add_one, static_cast<std::uint32_t>(input));
        std::int32_t incremented_add1 = incremented + 1;
        std::int32_t res = cudaq::device_call(rpc_add, incremented, incremented_add1);
        return res;
      }
    };


    int main() {
      const std::size_t num_shots = 3;

      const std::int32_t input = 2;
      auto results = cudaq::run(num_shots, simple{}, input);
      for (auto res : results) {
        printf("device_call returned: %d\n", res);
      }
    }
    ```

The `simple` kernel chains two `device_call`s — first `rpc_add_one`
(increment), then `rpc_add` (add) — matching the two handlers registered by
`main.cu` above. This is the client-side half of [Device Call](#device-call).

---

## Further resources

- [NVIDIA NVQLink](https://www.nvidia.com/en-us/solutions/quantum-computing/nvqlink/)
- [NVIDIA CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/)
- [CUDA-Q `quantum_machines` hardware backend](https://nvidia.github.io/cuda-quantum/latest/using/backends/hardware/qcontrol.html#quantum-machines)
- [CUDA-Q Quantum Machines examples](https://nvidia.github.io/cuda-quantum/latest/using/examples/hardware_providers.html#quantum-machines-examples)
- [QuAM documentation](https://qua-platform.github.io/quam/)
- [Quantum Machines NVQLink integration announcement](https://www.quantum-machines.co/press-release/quantum-machines-announces-nvidia-nvqlink-integration-extending-real-time-quantum-classical-computing-solution/)
- [OPNIC Hybrid Link Guide](OPNIC_Guide.md)
- [OPNIC Installation Guide](../Hardware/OPNIC_Installation.md)
