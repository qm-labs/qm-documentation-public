# OPX Simulator

The simulator is a useful tool to predict and verify the exact output of the OPX for a given QUA program. It also supports feeding input to
measurement commands via a simulated loopback interface.

The simulator returns the samples that will be played to the analog and digital ports.

!!!Note "OPX1000 MW-FEM"
    
    {{ requirement("QOP", "3.0") }}{{ requirement("QUA", "1.2") }}

    Simulation of MW signals from a MW-FEM returns a complex signal of the I and Q quadratures, before the upconversion to GHz freuqency.


## Usage

By calling the {{f("qm.quantum_machines_manager.QuantumMachinesManager.simulate")}} function from the [`qmm`][qm.quantum_machines_manager.QuantumMachinesManager].
This function should receive the configuration and program that are desired for simulation, and a {{f("qm.simulate.interface.SimulationConfig")}} object, whose API is specified in the following section.

!!!Note 

    You can obtain a qmm instance by either connecting to a real hardware device or a [cloud simulator instance](qm_saas_guide.md).

For examples, to simulate a program for 10 us (2500 cycles), we would use:

```python
simulated_job = qmm.simulate(config, prog, SimulationConfig(duration=2500))
```

To obtain the simulates samples use the {{f("qm.jobs.simulated_job.SimulatedJob.get_simulated_samples")}} function of the simulated job object.

!!! Note
    Attempting to simulate a long program would result in a gRPC timeout error.
    To increase the timeout duration, please use the `timeout` parameter when creating the `QuantumMachinesManager` object.

### Simulation Interfaces

The simulation interfaces enables inputting data or samples into a simulation, to simulate the OPX input.

#### Loopback Interface

It is possible to simulate a connection from an output of an OPX to one of the two inputs.
This is done by using the {{f("qm.simulate.loopback.LoopbackInterface")}} which is passed to the {{f("qm.quantum_machines_manager.QuantumMachinesManager.simulate")}} method of the [`qmm`][qm.quantum_machines_manager.QuantumMachinesManager] object.
For example, the following code generates a virtual connection from output 1 to input 2 of controller 1.

```python
qmm.simulate(config, prog, SimulationConfig(duration, simulation_interface=LoopbackInterface([("con1", 1, "con1", 2)]))
```

A list of two such tuples can be passed to the {{f("qm.simulate.loopback.LoopbackInterface")}} per simulated controller (as there are two inputs to the OPX).

Moreover, it is possible to also simulate signal propagation delay and noise using the `noisePower` and `latency` keywords in the {{f("qm.simulate.loopback.LoopbackInterface")}}

- `noisePower` adds gaussian noise with zero mean and a variance (in units \[$V^2$\]) set by this parameter.
- `latency`  adds a signal propagation delay in \[ns\] set by this parameter

For example, the following adds noise with variance 1 $V^2$ and 100 ns latency. All tuples in the loopback interface will have the same noise figure and same latency.

```python
qmm.simulate(config, prog, SimulationConfig(duration, simulation_interface=LoopbackInterface([("con1", 1, "con1", 2)], noisePower=1, latency=100))
```

#### Raw ADC interface

It is possible to explicitly specify the signal passed into the OPX in the simulation.
This is quite similar to the LoopbackInterface described above and supports the same options.

For example, the code snippet below plays a 1 microsecond signal to input 1 of the device called `"con1"`.

```python
signal = np.linspace(0, 0.2, 1000).tolist()
qmm.simulate(config, prog, SimulationConfig(duration, simulation_interface=RawInterface([("con1",1,signal)], noisePower=1, latency=100))
```

### Simulating Multiple Controllers

To simulate a system of multiple controllers, the inter-controller optical connectivity needs to be specified. 
This is important since The exact timing of multi-controllers operations is dependent on that connectivity configuration.
The connectivity is passed to the `controller_connections` parameter of the {{f("qm.simulate.interface.SimulationConfig")}} object.

To ease the configuration, we provide a [helper function](https://github.com/qua-platform/py-qua-tools/blob/main/qualang_tools/simulator_tools.py) as part of our tools' library.
The helper function generates a controller connection object according to the [default optical connectivity](../Hardware/opx+installation.md#connectivity-scheme). 

The following example demonstrates the usage for the case of 3 controllers:

```python
from qualang_tools.simulator_tools import create_simulator_controller_connections
connections = create_simulator_controller_connections(3)
job = qmm.simulate(config,prog,SimulationConfig(duration=1000, controller_connections=connections)

```

## API

See the complete [simulator API page](../API_references/simulator_api.md) in the API reference section for more details.


## Waveform Report

!!! Note 
    {{ requirement("QOP","2.2") }}

Executing quantum circuits at the pulse level and with real-time processing is a challenging task.
The Waveform Report is a feature that helps users to design, execute, and test their desired quantum circuits.
The OPX Simulator, simulating all analog and digital outputs, is the software equivalent of connecting the OPX to an oscilloscope, 
and is an essential tool for experimentalists as they work on developing pulse sequences. 
The Waveform Report is a complementary tool providing detailed information and plots of operations, waveforms, and ADC acquisition during the sequence.
When a waveform report object is created, it holds all the information associated with a specific `play()`, `measure()`, and `wait()` command 
and can be used to get more clarity of the compiler behavior and circuit validation. Additionally, this information can be readily plotted and sorted by elements 
to help experimentalists analyze quantum circuits at the pulse level and compare them to their desired gate-level circuit.

#### Generating the Waveform Report
To use the waveform report you first need to generate it from a simulated job:

```python
# simulate a program
job = qmm.simulate(config, prog, SimulationConfig(
        duration=duration,                    # duration of simulation in units of 4 ns
))

# get DAC and digital samples (optional).
samples = job.get_simulated_samples()
# get the waveform report object
waveform_report = job.get_simulated_waveform_report()
```
<br>

The report object can be cast to a python dictionary containing three keys: 

```python
waveform_dict = waveform_report.to_dict()
waveform_dict.keys() 

# prints: 
dict_keys(['analog_waveforms', 'digital_waveforms', 'adc_acquisitions'])
```
Each key points to a list specifying the analog waveforms, digital waveforms, and the adc acquisition (respectively).<br>

For clarity, let's inspect the first element in each list (for some generic example):

Analog Waveform:
```python
waveform_dict["analog_waveforms"][0]

# prints:
{
    'waveform_name': 'const_wf', # The waveform name that has been played
    'pulse_name': 'OriginPulseName=const',  # The associated pulse name
    'length': 60,  # The length of the pulse in ns
    'timestamp': 232,  # The starting time of the pulse in ns
    'iq_info':  # The IQ information of this element
        {'isPartOfIq': True, 'iqGroupId': 0.0, 'isI': True, 'isQ': False}, 
    'element': 'qe1', # The element to play to.
    'output_ports': [1],  # The OPX analog output port 
    'controller': 'con1',  # the controller number
    'pulser': {'controllerName': 'con1', 'pulserIndex': 0.0},  # The pulser that this waveform has been played from.
    'current_amp_elements': [0.19999999925494194, 0.0],  # The Current amplitudes of the I and Q elements
    'current_dc_offset_by_port': {'1': 0.0},  # The current DC offset of the port that this waveform is played from.
    'current_intermediate_frequency': 10000000.0,  # The current intermediate frequency of the element.
    'current_frame': [1.0, 0.0],  # The current frame of the I and Q elements 
    'current_correction_elements': [1.0, 0.0],  # Current correction elements (the I and Q components)
    'chirp_info': None,  # If this pulse is a chirp, further data (such as length, start and end frequencies and rates) are shown.
    'current_phase': 0.0  # Current phase.
 }
```

Similarly, for the digital waveform:
```python
waveform_dict["digital_waveforms"][0]
# Prints:

{
    'waveform_name': 'ON',
    'pulse_name': 'OriginPulseName=const',
    'length': 60,
    'timestamp': 320,
    'iq_info': 
        {'isPartOfIq': True, 'iqGroupId': 0.0, 'isI': True, 'isQ': False},
    'element': 'qe1',
    'output_ports': [1],
    'controller': 'con1',
    'pulser': {'controllerName': 'con1', 'pulserIndex': 0.0}
}
```

Finally, for the adc acquisition:
```python
print(waveform_dict["adc_acquisitions"][0])

{
    'start_time': 956,  # Start time in ns (including the time of flight)
    'end_time': 1056,
    'process': 'DemodIntegration',  # The process that is executed.
    'pulser': {'controllerName': 'con1', 'pulserIndex': 0.0},
    'quantum_element': 'qe1',
    'adc_ports': [1],  # Ths input port
    'controller': 'con1'
}
```

!!! Note that it can also be printed as a pretty string:
```python
print(waveform_report.to_string())
```
<br>

#### To visualize the Waveform Report:

The waveform report visualizer is a powerful tool that helps the user to analyze the compiler behavior and design his quantum circuits.
It is generated in an *.html file that can be opened in any browser (see the GitHub repo for a concrete example).
```python
waveform_report.create_plot(samples, plot=True, save_path="./")
```
There are a few things to note when using the visualizer:

* For each output port, the simulated output is shown as a function of time. In the panel below, the corresponding pulses are shown.<br> 
If `samples` is not provided, only the lower panel containing the pulse data is shown.
* For each input port, the ADC acquisition timing is indicated alongside the processing type (demodulation, averaging etc.).
* By hovering above the beginning of each pulse segment, the complete characteristic of the played pulse will be shown. 
* You can scroll through the X-axis of all the plots together or each panel separately. This is done by selecting the ***"x-axis scrolling method"*** at the top-right corner.
* By double-clicking an element in the legend, you can view only its occurrences throughout the sequence. Single-click to disable any element.
* More tools can be found in the top-right corner, including exporting to png, zoom-in and out, resetting the axis to the original view, etc.
  * By selecting the 'zoom' option, you can select any kind of rectangle to zoom at. Double-click to reset. 
  * By selecting the 'pan' you can scroll through the plot (according to the scrolling method)

## Examples

See more hands-on examples of the simulator and the waveform report in our [GitHub tutorials](https://github.com/qua-platform/qua-libs/tree/main/Tutorials/intro-to-simulation)
