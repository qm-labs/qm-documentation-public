# OPX1000 Front End Modules (FEMs)

## Low Frequency FEM (LF-FEM)
The LF-FEM module features 8 analog outputs at a sampling rate of 2 GSa/s, 2 analog inputs at a sampling rate of 2 GSa/s, 
and 8 digital outputs at a sampling rate of 1 GSa/s.
For more information about the panel and the connectors, see [OPX1000 Hardware](../Hardware/OPX1000_hardware.md).

### Sampling Rate
The DACs and ADCs of the LF-FEM always operate at 2 GSa/s. The Pulse Processor Unit (PPU) can be set to operate at 1 GSa/s,
or 2 GSa/s, by setting the config field `sampling_rate` of an output/input port to be either `1e9` or `2e9`:

* When the output port is set to `1e9`, which is the default value, the samples are generated at 1 GSa/s and the PPU upsamples the output from 1 GSa/s to 2 GSa/s at which the DACs operate. This is controlled by an additional field `upsampling_mode`:
    - `mw` - In this mode, the upsampling is done by passing the 1 GSa/s samples through a 14-taps Dolph-Chebyshev filter which is optimized to reduce spurs and produce clean MW signals. This is the recommended mode whenever the output is expected to have an intermediate frequency larger than 100 MHz.
    - `pulsed` - In this mode, the upsampling is done by passing the 1 GSa/s samples through a 2 taps moving average filter which is optimized to produce clean step responses. This is the recommended mode whenever the output is **not** expected to have an intermediate frequency.
* When the output port is set to `2e9`, the samples are generated at 2 GSa/s and the PPU passes them directly to the DACs.

This has the following implications: 

* Any element using an output port set to `1e9` will be limited to a frequency of 500 MHz, and the waveforms' sampling rate is limited to `1e9`.
* Any measurement done on an input port set to `1e9` will produce an ADC stream at `1e9` and the demodulation will be limited to 500 MHz.
* Any element using an output port set to `2e9` will consume double the amount of threads.

!!! Note
    If an element is using output ports set to `1e9`, and input ports set to `2e9`, it will also consume double the 
    amount of threads.

### Output Mode
The analog outputs can operate in one of two modes, set in the config at the output port using the field `output_mode`:

* `direct` -  The output range is between -0.5 V to 0.5 V.
* `amplified` - The output range is between -2.5 V to 2.5 V, the hardware filters are optimized for a cleaner step response.


## Microwave FEM (MW-FEM)
The MW-FEM module features 8 analog outputs at a quadrature sampling rate of 1 GSa/s which are digitally unconverted to 
MW frequencies, 2 analog inputs at a sampling rate of 1 GSa/s, and 8 digital outputs at a sampling rate of 1 GSa/s.
For more information about the panel and the connectors, see [OPX1000 Hardware](../Hardware/OPX1000_hardware.md).

!!! Note
    The quadrature sampling rate for the MW output ports defines the rate at which samples are sent from the PPU to the
    DACs, per quadrature. This is then being digitally upconvertered to GHz frequencies.

### Reset Upconverter and Downconverter phase

The upconverter and downconverter frequencies are created digitally and therefore, their phase can be reset from QUA.
This is useful for 2qb gates which relay on the absolute lab phase of pulses, such as FSIM in this [Google paper](https://arxiv.org/pdf/2101.08870). It can also be used for debugging when viewing the pulses on the scope.
Resetting the phase is achieved using the command, {{f("qm.qua._dsl.reset_global_phase")}}, which would reset the phase of all upconverters, downconverters & intermediate frequencies in the program, and is further explained in [this section](phase_and_frame.md#global-phase).

[//]: # (### Sampling Rate)

[//]: # (The analog outputs and inputs sampling rate can be defined to be 1 or 2 GSa/s, by setting the field `sampling_rate` to be)

[//]: # (either `1e9` &#40;default&#41; or `2e9` in the config at the port. This has the following implications:)

[//]: # ()
[//]: # (* An output port set to `2e9` can only have a single upconverter.)

[//]: # (* Any element using an output port set to `2e9` will consume double the amount of threads.)

[//]: # (* Any element using an output port set to `1e9` will be limited to a frequency of 500 MHz, and the waveforms' sampling rate is limited to `1e9`.)

[//]: # (* Any measurement done on an input port set to `1e9` will produce an ADC stream at `1e9` and the demodulation will be limited to 500MHz.)

[//]: # ()
[//]: # (!!! Note)

[//]: # (    If an element is using output ports set to `1e9`, and input ports set to `2e9`, it will also consume double the )

[//]: # (    amount of threads.)

### Bands
Each analog port must specify the `band` at which it operates in the config, the supported bands are:

* `1` - 50 MHz - 5.5 GHz
* `2` - 4.5 GHz - 7.5 GHz
* `3` - 6.5 GHz - 10.5 GHz

In addition, the following pairs of analog ports are coupled:

* Out 1 & In 1
* Out 2 & Out 3
* Out 4 & Out 5
* Out 6 & Out 7
* Out 8 & In 2

Coupled ports must be in the same band, or in bands `1` and `3`.

### Upconverters and Downconverters
Each analog output port must define either an `upconverter_frequency` field with a frequency in the port's band, or 
a `upconverters` field, with up to 2 upconverters per port:

```python
'upconverters': {
    1: {'frequency': 5e9},
    2: {'frequency': 6e9},
}
```

In the elements `MWInput` field, the user can set the `upconverter` field, the default is 1.

Each analog input port must define a `downconverter_frequency` field with a frequency in the port's band.

### Output Power

The analog output power is defined using the field `full_scale_power_dbm`, which can be set between `-41` and `10` dBm 
with a 3 dB granularity.
This will set the power delivered to a 50 ohm load when the waveform is set to full scale (`[-1, 1]`).

!!! Note
    To calculate the voltage that will be seen on a scope set to 50 ohm, first convert the power to voltage:

    \begin{eqnarray}
    x_{mw} = 10^{\frac{x_{dbm}}{10}} \\
    x_v = \sqrt{\frac{2 \cdot 50 \cdot x_{mw}}{1000}}
    \end{eqnarray}

    Where $x_{dbm}$ is the value written in the config. This is then multiplied by the waveform amplitude and any
    realtime modification done in QUA.

