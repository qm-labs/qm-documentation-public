---
search:
  boost: 2
---

# Simulator API

::: qm.simulate.interface.SimulationConfig

::: qm.simulate.loopback.LoopbackInterface

::: qm.simulate.raw.RawInterface

::: qm.results.simulator_samples.SimulatorControllerSamples

## Interpreting Sample Timing

`SimulatorControllerSamples.analog` holds raw arrays. When converting sample index to time, use `analog_sampling_rate` for the relevant port. The built-in `plot()` method already uses that sampling rate and labels the x axis in ns.

For OPX1000 LF-FEM outputs, `analog_sampling_rate` is `2e9`, so adjacent analog samples are `0.5 ns` apart.

```python
samples = job.get_simulated_samples()
port = "1-1"  # FEM 1, port 1
dt_ns = 1e9 / samples.con1.analog_sampling_rate[port]
```

## Waveform Report

The waveform report describes the analog and digital waveforms played during a simulated job, and can
be rendered to a human-readable string.

::: qm.waveform_report.WaveformReport
    options:
        heading_level: 3
        show_root_full_path: false

::: qm.waveform_report.Event
    options:
        heading_level: 3
        show_root_full_path: false

## Cloud Simulator API

::: qm_saas.client
