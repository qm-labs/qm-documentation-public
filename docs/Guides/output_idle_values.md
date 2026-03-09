# Output Idle Values

When a Quantum Machine (QM) is open, the hardware holds defined *idle values* on its output channels between jobs.
Understanding what these idle values are, when they apply, and how they interact with runtime changes is important for
controlling DC biases (e.g. flux lines) and digital markers reliably across a multi-job workflow.

## What Are Idle Values?

Idle values are the hardware state the QM enforces on output channels **between jobs**:

- **Analog outputs** — the DC offset (volts) defined in the controller config under `analog_outputs[n]['offset']`.
- **Digital outputs** — the polarity state set by the `'inverted'` flag in `digital_outputs[n]`. When `inverted: True`, the digital output holds **HIGH** between jobs (see [Inverted Digital Marker](features.md#inverted-digital-marker)).

=== "OPX1000"

    !!! note "QOP 3.4 or earlier"
        The idle-value lifecycle described in this tab applies to the **OPX1000 with {{ requirement("QOP","3.5") }} or later**.
        For earlier QOP versions, refer to the **OPX+** tab.

    ### Lifecycle

    | Event | Hardware output | Idle value |
    |-------|----------------|------------|
    | QM opened | Set to the loaded idle value | Loaded from controller's config |
    | Between jobs | Holds idle value | Unchanged |
    | Job starts | Holds idle value unless overwritten | Unchanged |
    | Job/QUA API while Job is running | Updated immediately | **Unchanged** |
    | `qm.update_config()` called during job execution | **Unchanged** | **Updated** |
    | Job ends | **Reverts to idle value** | Unchanged |
    | `qm.update_config()` called not during job execution | Updates immediately | Updated |
    | QM closed | Back to default values | No longer applied |

    ### Runtime Changes Are Temporary

    Any of the following changes the *current* hardware value during a job, but **does not update the idle value**:

    - `set_dc_offset(element, input, offset)` — called from inside a QUA program.
    - `job.set_output_dc_offset_by_element(element, input, offset)` — called via the Job API.
    - A controller config passed alongside a job at submission time (e.g. `qm.execute(prog, controller_config=...)`): the offset in that config applies **only for that job**.

    When the job ends the hardware reverts to the idle value that was in effect before the job started.

    ### Updating the Idle Value Permanently

    To change the idle value without closing and re-opening the QM, use `qm.update_config()`:

    ```python
    qm.update_config({
        "controllers": {
            "con1": {
                "fems": {
                    1: {
                        "type": "LF",
                        "analog_outputs": {
                            1: {"offset": 0.25},  # new idle value
                        },
                    }
                }
            }
        },
    })
    ```

    The new idle value takes effect between the current job and the next one. Already-compiled or already-running jobs are not affected.

    ### Digital Channels

    Digital output polarity follows the same pattern. The `inverted` flag in the controller config sets the idle state when the QM opens and this state is restored between jobs.
    Changing digital polarity at runtime does not persist beyond the job.

=== "OPX+"

    !!! note "QOP 3.4 or earlier"
        Before QOP 3.5, OPX1000 behaved in the same way as the OPX+.
    
    On the OPX+ the offset field in the config is used to initialise the DC offset when the QM is opened,
    but the **persistence model is different from the OPX1000**:

    - `qm.set_output_dc_offset_by_element()` is a **QM-level** call (not job-level). Changes **persist between jobs** for as long as the QM remains open.
    - There is no `qm.update_config()` API on the OPX+.
    - **Closing the QM resets all DC offsets to zero**, regardless of what value was active. To prevent this, pass `keep_dc_offsets_when_closing=True` to `open_qm()` (available from qm-qua 1.2.1 / QOP 2.4.2):

    ```python
    qm = qmm.open_qm(config, keep_dc_offsets_when_closing=True)
    ```

    !!! note
        `keep_dc_offsets_when_closing` is an OPX+ only feature and is not applicable to the OPX1000.

---

## FAQ

**When a job finishes, is the DC offset on the channel maintained?**

Yes — on the OPX1000 ({{ requirement("QOP","3.5") }}) the channel reverts to its idle value, which is the offset defined in the controller config (or last set via `qm.update_config()`).
On the OPX+ the offset set via `qm.set_output_dc_offset_by_element()` persists between jobs.

**What happens to the DC offset when the QM is closed?**

By default, closing the QM resets hardware DC offsets to zero (both OPX1000 and OPX+). On OPX+, you can keep the current offsets by opening the QM with `keep_dc_offsets_when_closing=True`.

**I used `job.set_output_dc_offset_by_element()` during a job. Which offset will be present after the job ends?**

The original idle value (from the controller config, or from the last `qm.update_config()` call) — not the value you set during the job.
This API is OPX1000/QOP 3.x only.

**How do I permanently change the DC offset without re-opening the QM?**

Use `qm.update_config()` (OPX1000/QOP 3.x). On the OPX+ use `qm.set_output_dc_offset_by_element()`, which already persists across jobs.
