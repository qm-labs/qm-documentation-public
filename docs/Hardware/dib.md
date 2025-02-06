---
search:
  boost: 0.5
---
# OPD - Operator Digital

The OPD is a separate box that enhances the OPX input with 10 more digital signals.
These 10 inputs have programmable thresholds and are sampled at 1 ns resolution.
They are $50 \Omega$ matched and accept up to 3.3 V (LVTTL).

## Usage

The OPD is directly connected to the OPX. When it is present, the input channels can be defined in the configuration file
similarly to other channels. For example:

```python
'controllers': {
        'con1'': {
            'type': 'opx1',
            "analog_outputs": {
                ...
            },
            'digital_inputs': {
                1: {'polarity': 'RISING', 'deadtime': 4, "threshold": 0.1},
                2: {'polarity': 'RISING', 'deadtime': 15, "threshold": 3.2},
            },
            'analog_inputs': {
                ...
            },
        },
    },
```

When defining a digital input, several parameters needs to be defined:

- `polarity` - Whether it is triggered when `RISING` (rising edge) or `FALLING` (falling edge)
- `deadtime` - Minimal time between pulses in ns. e.g., If it is set to 16 ns, then only the 1st pulse out of two pulses 10 ns apart will be detected. 'deadtime' should be between 4 and 16 ns.
- `threshold` - Voltage threshold

Once defined in the controller, it can be used in a quantum element as follows:

```python
"elements": {
    "qubit": {
        "mixInputs": {
            ...
        },
        'digitalOutputs': {
            'out1': ('con1', 2)
        },
        ...
    },
},
```

## Time Tagging

Time Tagging with the OPD is done similarly to a [normal time tagging](../Guides/features.md#time-tagging) measurement:

```python
times = declare(int, size=10)
counts = declare(int)
measure([pulse], [element], [stream], time_tagging.digital([times], [max_time], [counts], [element_output])
```

- `times` is a vector of integers that is populated by the measurement.
- `max_time` gives the maximum time window, in ns, during which the statement waits for tag arrival.
- `counts` is a variable that is populated with the number of tags which arrived during the measurement.
- `element_output` **must** be defined if the `element` has more than one digital output. In this case, it is a string indicating the output to be measured. It can be left empty when the element has only one input (default is empty string).

The time-tagging operation ends *either* at the set duration *or* when the `times` is fully populated (first one of the two).

Note that the information in `times` is only valid up to `counts`.

In addition, with the OPD you can directly count pulses:

```python
counts = declare(int)
measure([pulse], [element], [stream], counting.digital([counts], [max_time], [element_outputs]))
```

- `counts` is a variable that is populated with the number of pulses which arrived during the measurement.
- `max_time` gives the maximum time window, in ns, during which the statement waits for incoming pulses.
- `element_outputs` **must** be defined if the `element` has more than one digital input. In this case, it is either a string indicating the output to be measured or a tuple with list of strings corresponding to the outputs to be measured. It can be left empty when the element has only one input (default is empty string).

## Wait for trigger

It is possible for any element to wait until a pulse arrives at one of the OPD inputs. This is done with the {{f("qm.qua._dsl.wait_for_trigger")}} function.

```python
wait_for_trigger(element_waiting, pulse_to_play=None, trigger_element=None)
```

- `element_waiting` is the element waiting.
- `pulse_to_play` is the name of the pulse to play on the element while waiting for the external trigger. Must be a constant pulse. Can be None to play nothing while waiting.
- `trigger_element` is an element with digital inputs, when one of his digital inputs is triggered, the `element_waiting` will continue. If `trigger_element` has multiple digital inputs, a specific one **must** be chosen: `trigger_element` can be a tuple, with the 1st item being the element name and the 2nd item being the trigger input. If `trigger_element` is left empty, then it waits for the trigger input in the back panel of the OPX.

!!! Tip 
    See also the following guide on [external triggering](../Guides/external_trigger.md)