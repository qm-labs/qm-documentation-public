---
search:
  boost: 3
---

# The Configuration

Before diving into the many features and possibilities of QUA, it is important to understand the importance and the
basics of the configuration in QUA.
In the following tutorial, we describe the components of the configuration and the principles behind it.

!!! Note
    The configuration may vary significantly from project to project. The examples below demonstrate the general
    building blocks of the configuration. Therefore, we do not recommend copy-pasting them into your project.


## Overview

The configuration is a crucial piece of the QOP which enables writing advanced QUA protocols simply and intuitively,
using 'human language.'

As described in the [conceptual overview](./qop_overview.md), the configuration is
where we define our 'Quantum machine' with its elements and their operations.

For example, a simple quantum machine may be the combination of two analog output ports connected to a superconducting
qubit through an IQ mixer and a readout resonator connected to two analog input ports through another mixer.

In the configuration we will define (partial list):

- The setup connectivity and associated dc offsets
- Intermediate frequencies of the qubit and resonator
- Waveforms, amplitudes, and lengths of both control and measurements pulses
- IQ mixer correction parameters
- Octave configuration (if used)

When performing an operation (e.g., a pi pulse on the qubit), the relevant waveform will be sent out of the associated
analog outputs, adjusted to the required length and amplitude, modulated by the qubit's frequency, and corrected to
account for the IQ mixer imbalance. All within a simple, single line of code.

This is an example of the powerful 'set and forget' approach of QUA.

We will get back to this example later, but for now, let's look at some of the configuration's components.

```python
config = {
    'version': 1,
    'controllers': {...},
    'octaves': {...},
    'elements': {...},
    'pulses': {...},
    'waveforms': {...},
    'digital_waveforms': {...},
    'integration_weights': {...},
    'mixers': {...},
    'oscillators': {...}
}
```

As we can see, the configuration is essentially a Python dictionary of dictionaries, each defining a subsection of the
quantum machine.

!!! tip
    Time values in the configuration are in units of ns, and some are required to be divisible by 4.
    Electric potential is defined in units of V.

## Configuration Components

### Version

Currently, the version value must be set to 1.

### Controllers

=== "OPX1000 - LF"

    The controller's dictionary sets the input and output ports of the control hardware (i.e., your OPX).
    We define and configure the ports that participate in the quantum machine for every controller and Front End Module (FEM).
    In the example below, we use 1 analog outputs, 1 analog inputs, and 1 digital output of an LF-FEM situated in slot 1 of the controller.
    
    ```python
    'controllers': {
        'con1': {
            'type':'opx1000',
            'fems':
                1 :{
                    'type': 'LF',
                    'analog_outputs': {
                        1: {
                            'offset': 0.0,
                            'sampling_rate': 2e9, # Default sampling rate is 1e9
                            'output_mode': 'amplified', # Default output_mode is 'direct'
                            'upsampling_mode': 'pulse', # Default is 'mw'
                        },   
                    },
                        'digital_outputs': {
                            1: {}
                    },
                    'analog_inputs': {
                        1: {
                            'offset': 0.0,
                            'sampling_rate': 2e9, # Default sampling rate is 1e9
                            'gain_db': -3
                        }, 
                }
            }
        }
    },
    ```
    
    #### Analog Outputs
    
    Each analog output port is defined with a `key:item` pair, where the key is the port number and the item is a Python dictionary
    holding some port-specific configuration. We can set an `'offset'`, a `'filter'`, `'delay'` to the port in units of ns.
    Moreover, we can define LF-FEM specific parameters such as `'sampling_rate'`, `'output_mode'`, and `'upsampling_mode'`.
    For more information on the FEM-specific parameters, please refer to the [FEMs guide]().

    For more information on the `filter` capabilities, please refer to the [Guide on output filters](../Guides/output_filter.md).
    

=== "OPX1000 - MW"

    The controller's dictionary sets the input and output ports of the control hardware (i.e., your OPX).
    We define and configure the ports that participate in the quantum machine for every controller and Front End Module (FEM).
    In the example below, we use 1 analog outputs, 1 analog inputs, and 1 digital output of an MW-FEM situated in slot 2 of the controller.
    
    ```python
    'controllers': {
        'con1': {
            'type':'opx1000',
            'fems':
                2 :{
                    'type': 'MW',
                    'analog_outputs': {
                        1: {
                            'sampling_rate': 2e9, # Default sampling rate is 1e9
                            'band': 2, 
                            'full_scale_power_dbm': 10,  # Default is -10
                            'upconverters': {
                                1: {'frequency': 5e9},
                                2: {'frequency': 6e9},
                            },
                            # 'upconverter_frequency': 5e9  # if only one upconverter is used this can replace 'upconverters'.
                        },

                    },
                    'digital_outputs': {
                        1: {}
                    },
                    "analog_inputs": {
                        1: {"sampling_rate": 1e9, "band": 2, "downconverter_frequency": 5e9},
                    }
                }
            }
        }
    },
    ```
    
    #### Analog Outputs
    
    Each analog output port is defined with a `key:item` pair, where the key is the port number and the item is a Python dictionary
    holding some port-specific configuration. We can set an `'offset'`, `'delay'` to the port in units of ns.
    Moreover, we can define MW-FEM specific parameters such as `'sampling_rate'`, `'band'`, `'full_scale_power_dbm'` and `'upconverters'`.
    For more information on the FEM-specific parameters, please refer to the [FEMs guide]().
    

=== "OPX+"
    
    The controller's dictionary sets the input and output ports of the control hardware (i.e., your OPX).
    We define the ports that participate in the quantum machine for every controller and can correct for DC offsets.
    In the example below, an OPX serves as one controller with 4 analog outputs, 2 analog inputs, and 1 digital output.
    
    ```python
    'controllers': {
        'con1': {
            'type':'opx1',
            'analog_outputs': {
                1: {'offset': 0.0},
                2: {'offset': 0.0},
                3: {'offset': 0.0},
                4: {'offset': 0.0},
            },
            'digital_outputs': {
                1: {}
            },
            'analog_inputs': {
                1: {'offset': 0.0},
                2: {'offset': 0.0}
            }
        }
    },
    ```
    
    #### Analog Outputs
    
    Each analog output port is defined with a `key:item` pair, where the key is the port number and the item is a Python dictionary
    holding some port-specific configuration. We can set an `'offset'`, a `'filter'`, and in {{ requirement("QOP","2") }} we can also specify a `'delay'` to the port in units of ns.
    
    For example, we can define an analog output with a 20 mV offset and a 71 ns delay as follows:
    
    ```python
    1: {'offset': 0.02, 'delay': 71}
    ```
    
    For more information on the `filter` capabilities, please refer to the [Guide on output filters](../Guides/output_filter.md).

### Elements

In the element section, each element is defined with its own dictionary. For example, a quantum machine with
two qubits, two readout resonators and a flux line is defined as follows:

```python
'elements': {
    'qubit1': {...},
    'qubit2': {...},
    'resonator1': {...},
    'resonator2': {...},
    'flux_line': {...},
}
```

Within each element's dictionary, we set the input and output parameters, we map between operations and pulses and more. Let's take a closer look at a few examples:

- Mixed Inputs Element
- Single Input Element
- Octave-using Element
- MW FEM-using Element
- LF FEM-using Element

!!! Note

    It is not possible to define an element which has inputs and outputs from different controllers or FEMs.

#### Mixed Inputs Element

```python
'qubit1': {
    'mixInputs': {
        'I': ('con1', 1),
        'Q': ('con1', 2),
        'lo_frequency': qubit_LO,
        'mixer': 'mixer_qubit'
    },
    'intermediate_frequency': qubit_IF,
    'operations': {
        'saturation': 'saturation_pulse',
        'pi': 'pi_pulse',
        'pi_half': 'pi_half_pulse',
    },
```

First, in the `'mixInput'` dictionary, we configure which hardware port is connected to the qubit, as "seen" from
the qubit's perspective. In this case, analog output ports 1 and 2 from controller 1, are connected to the I and Q ports
of the qubit's IQ mixer, respectively.

Moreover, in the `'lo_frequency'` key we define the local oscillator's frequency as an integer in units of Hz, and in
the `'mixer'` key we map to a mixer instance, as defined in the [mixers section](#mixers).

The `'intermediate_frequency'` key defines the frequency at which the waveform samples, as defined in the
[waveforms section](#waveforms), will be modulated with. We can get a DC pulse by setting this frequency to zero.

In the `'operations'` dictionary we map between the abstract operations relevant to the element
(i.e., pi, saturation, measurement, etc.) and their respective pulse instance, as defined in the
[pulses section](#pulses).
This mapping between an `abstract` operation and a pulse allows keeping QUA codes simple and readable while accounting
for the many possible variations, as no two qubits are the same.

Taking a look at an example of a readout resonator, we can see a few more properties, relevant to a measurement element:

```python
'resonator1': {
    'mixInputs': {...},
    'intermediate_frequency': rr_IF,
    'operations': {...},
    "outputs": {
        'out1': ('con1', 1)
    },
    'time_of_flight': 180,
    'smearing': 0
},
```

Note how we define the output of an element, from the perspective of the element. In the case above, the output of the
resonator is connected to input 1 of controller 1.
The `time_of_flight` and `smearing` keys are parameters related to the timing of the signal and are further
explained in the [Guide on demodulation, section on timing of measurement](../Guides/demod.md#timing-of-the-measurement-operation).

#### Single Input Element

```python
'flux_line': {
    'singleInput': {
        'port': ('con1', 9),
    },
    ...
},
```

In the `'singleInput'` dictionary, we configure which hardware port is connected to the `flux_line` element, as "seen" from
the flux line's perspective. In this case analog output port 9 from controller 1 is connected to the flux line.

#### Octave-using Element

```python
'resonator': {
    'RF_inputs': {'port': ('oct1', 1)},
    'RF_outputs': {'port': ('oct1', 1)},
    'intermediate_frequency': rr_IF,
    'operations': {
        'readout': 'readout_pulse',
    },
    "time_of_flight": 180,
    "smearing": 0,
}
```

Similarly to the case of the readout resonator from above, however, here we define the element's ports as used in the octave.
To see how the internal mapping from OPX I&Q ports ot the relevant RF outputs of the octave is done, see the [octave guide](../Guides/octave.md#opx-octave-connectivity)

#### OPX1000 FEM-using Element

In the OPX1000, each port receives an address point in the format `(controller name, FEM number, port number)`. 
For example, `("con1", 1, 2)` refers to port 2 on the FEM in slot 1 of controller 1 (chassis number 1).

##### LF FEM

In the LF-FEM case, there are no differences compared to the OPX cases above (`mixInputs`, `singleInput`, `octave`), except for the port address discussed above.

##### MW FEM

In the MW FEM, we define the ports as follows:

```python
"resonator": {
    "MWInput": {
        "port: ("con1", 5, 2),
        "upconverter": 2  # optional, if not specified, the default will be 1  
    },
    "MWOutput": {
        "port": ("con1", 5, 1),  # Output (FEM input) has only a single downconveter, so there is no need to specificy it
    },
}

```

##### Digital Inputs

It is also possible to define digital inputs in the element section. For example, a digital input can be defined as follows:

```python
'switch': {
    'digitalInputs': {
        'switch_in': ('con1', 1)
    },
},
```


### Pulses

Similar to other components, every pulse is defined with a dictionary.
Let’s take a look at an example of a simple pi pulse:

```python
'pi_pulse': {
    'operation': 'control',
    'length': 60,
    'waveforms': {
        'I': 'pi_wf',
        'Q': 'zero_wf'
    }
},
```

In the `'operation'` key we define whether the pulse is a control or a measurement operation.
The `'length'` sets the pulse duration in units of nanoseconds and must be divisible by 4.
In the `'waveforms'` key, we map between the input name (defined in the element section) and a waveform,
as defined in [the waveforms section](#waveforms).
Note that even though the waveform in Q is set to zero, there will be an output from both ports.
See the following [Mixed input elements section in QUA overview](qua_overview.md#mixed-inputs-element) for more details.

For a measurement pulse we also map to optional integration weights to be used in the demodulation process, as shown below.
You can read more about the integration weights usage in the [Guide on measure statement features](../Guides/features.md#measure-statement-features).

```python
"readout_pulse": {
    "operation": "measurement",
    ...
    "integration_weights": {
        "cos": "integW_cos",
        "sin": "integW_sin",
    },
```

!!! Note
    If the pulse is related to a Single Input element, the `'waveforms'` key holds only one waveform. For example:

    ```python
    'const_flux_pulse': {
        ...
        'waveforms': {
            'single': 'const_flux_wf',
        },
    },
    ```


### Waveforms

In this section we define the waveforms to be used in the pulses. We can define either a constant value waveform or an arbitrary one.
An arbitrary waveform needs to be provided with a list of samples with length which is equal to the pulse duration. i.e. A Gaussian.
Note that in both cases, we define the envelope of the pulse before the modulation by the IF frequency.
For example, in the code below we define a constant 0.4 Volt waveform and an arbitrary waveform.

```python
'waveforms': {
    'const_flux_wf': {
        'type': 'constant',
        'sample': 0.4
    },
    'pi_wf': {
        'type': 'arbitrary',
        # a list of values describing a Gaussian of length equal to the pulse duration
        'samples': [0, 1.2486367355980437e-05, 2.6352133635387178e-05, ... , 2.6352133635387273e-05, 1.248636735598048e-05, 0]
   },
```

!!! Note
    It is possible to compress the pulse memory by using two parameters: `max_allowed_error` and `sampling_rate`. For further information see [Pulse Memory Compression](../Guides/features.md#pulse-memory-compression)

!!! tip
    In the [QUA tools section](https://github.com/qua-platform/py-qua-tools/tree/main/qualang_tools) you can find a lot of useful tools for writing QUA programs. In particular, [Config tools](https://github.com/qua-platform/py-qua-tools/tree/main/qualang_tools/config/) which include [Waveform Tools](https://github.com/qua-platform/py-qua-tools/tree/main/qualang_tools/config/waveform_tools.py) package that provides tools for easy waveform creation and manipulation.

### Digital Waveform

In this section we define the digital waveforms to be used in the program as follows:

```python
'digital_waveforms': {
    'ON': {
        'samples': [(1, 0)]
    }
},
```

Here we defined a digital high waveform named 'ON' that will be played for the entire duration of the pulse it is associated with.
Read more on [how to configure digital outputs](qua_overview.md#digital-waveform-manipulations).

### Integration Weights

The integration weights are used in the demodulation process as part of the measurement and are defined as a list of tuples.
The first element in every tuple is the value of the integration weight and the second is the duration, in ns, for which this value should be used. The duration must be divisible by 4.

In the simple example below, we define two sets of integration weights, `"cos"` and `"sin"`.
The first have the value `1.0` in the cosine component and `0.0` in the sine component for the entire duration of of the pulse.
Read more about [the usage of integration weights](../Guides/demod.md#demodulation-and-measurement) and see [an advanced usage of the integration weights](../Guides/demod.md#rotating-the-iq-plane).

```python
"integration_weights": {
    "cos": {
        "cosine": [(1.0, readout_len)],
        "sine": [(0.0, readout_len)]
    },
    "sin": {
        "cosine": [(0.0, readout_len)],
        "sine": [(1.0, readout_len)],
    },
},
```

!!! tip
    In the [QUA tools repository](https://github.com/qua-platform/py-qua-tools/tree/main/qualang_tools) you can find a lot of useful tools for writing QUA programs. In particular, [Config tools](https://github.com/qua-platform/py-qua-tools/tree/main/qualang_tools/config/) which include [Integration Weights Tools](https://github.com/qua-platform/py-qua-tools/tree/main/qualang_tools/config/integration_weights_tools.py) package that allows for easy conversion and compression of the integration weights.

### Mixers

In this section we configure the IQ mixer instances that are used by the elements.
Each mixer instance contains a list of dictionaries for the [correction matrix](qua_overview.md#the-c-matrix) for every pair of IF and LO.

```python
'mixers': {
    'mixer_qubit': [
        {'intermediate_frequency': qubit_IF, 'lo_frequency': qubit_LO,
         'correction': [1.0, 0.0, 0.0, 1.0]}
    ],
    'mixer_RR': [
        {'intermediate_frequency': rr_IF, 'lo_frequency': rr_LO,
         'correction': [1.0, 0.0, 0.0, 1.0]}
    ],
}
```

### Oscillators

{{ requirement("OPX+", "2.0") }} {{ requirement("QUA", "0.3.4") }}

In the oscillators section, we can specifically define oscillators that can be shared between elements.
When multiple elements share an oscillator, then any operation on that oscillator (frequency, frame or correction changes)
will affect both elements.
It is defined as follows:

```python
'oscillators': {
    'osc': {...},
    'osc2': {...},
}
```

With each oscillator defined as follows:

```python
"osc": {
    "intermediate_frequency": osc_IF,
    'lo_frequency': osc_LO,
    'mixer': 'mixer_qubit'
}
```

Defining the `lo_frequency` and `mixer` is optional and is only used if the oscillator is being used by an element with a
`mixInputs`. Note that even if two elements output to different ports (and different mixers), they will have to use
the same correction matrix.

In order to use the oscillator with multiple elements, the oscillator must be declared in the element's configuration
instead of declaring an `intermediate_frequency`. For example:

```python
'qubit1': {
    'mixInputs': {...},
    'oscillator': "osc",
    'operations': {...}
```

## Further details

You can find a `beta` tool detailing [the complete config specification](../API_references/config_spec.md).
