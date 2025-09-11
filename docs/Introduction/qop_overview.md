# QOP Conceptual Overview

This section describes the main concepts constituting the Quantum Orchestration Platform (QOP).


## Quantum Orchestration Platform

QM's Quantum Orchestration Platform (QOP) is a hardware and software platform for designing quantum control protocols, executing them on a wide range of quantum hardware platforms and optimizing performance.
The QOP is designed to meet the extremely demanding requirements of quantum control, including synchronized multichannel pulse sequences, pulse parametrization, real-time classical calculations, complex flow control with real-time decision-making, and ultra-low latency feedback.

## Quantum Machine

A **Quantum Machine (QM)** is created with a **controller configuration**—a Python dictionary that defines the physical hardware resources such as controllers, octaves, and mixers, along with their associated idle values.
This configuration determines which resources the QM will reserve. 
Once opened, the QM locks these physical resources so no other QM can use them, enforces default outputs idle state (e.g. DC offsets) which are set between jobs, and manages a job queue to prevent conflicts between concurrent executions.

The **logical configuration** defines abstract, program-level elements such as pulses, waveforms, oscillators, and measurement definitions.
This configuration is typically needed when executing a job, but can also be supplied to the QM, alongside the physical controller config, as a convenience for simple or single-user workflows.

Read more on the [config page](config.md).

## QUA Language


Our programing language, **Quantum Universal Abstraction** (**QUA**), allows programming complex protocols that run in **real-time** on the Quantum Machine.
Real-time execution of **QUA Programs** is made possible thanks to the QOP's unique compiler and FPGA-based Pulse Processor, thus saving huge amounts of time and resources, improving performance, and opening new possibilities in quantum experiments.

Read more on the [QUA page](qua_overview.md).

## QUA Development Environment

On the client's computer, the quantum developer communicates with the QOP using a [Python package available on PyPi](https://pypi.org/project/qm-qua/), 
the [source code is available here](https://github.com/qm-labs/qm-qua-sdk-public), and the [latest changes can be found here](../Releases/qm_qua_releases.md).

Via the desktop app, the user finds the orchestrator on the network, initializes communication with it, and manages QM's software versions and updates.

The Python package is used by the quantum developer to:

- Instantiate quantum machines and communicate with them (via the quantum machine API).
- Write QUA programs and execute them on quantum machines.
- Execute and simulate Qua programs.


## Multi Quantum Machine Orchestration

As shown in the figure below, QOP can support many Quantum Machines in the same platform in a seamless way:

The quantum machines create an abstraction layer, which allows QUA developers to send programs from any client computer to be executed on any of the quantum machines.
Multiple QUA developers can work in parallel from one or more client interfaces.

<figure markdown>
  ![multi_machine1](assets/multi_machine1.png)
  <figcaption>Scaled-up: multiple quantum machines, OPXs per machine, developers</figcaption>
</figure>

## Scalable Architecture

Multiple OPXs can be connected to a single quantum system, to allow working with a large number of qubits, while the software interface and, in particular, programing QUA programs, remain the same.

## Stack Overview

The execution of a program involves a seamless flow, starting from its definition on your lab PC, through the compilation in the OPX and ending in pulse transmission to the quantum hardware.
This flow can be seen in the figure below.

<figure markdown>
  ![Overview of QOP stack for a single OPX+](assets/QOP_stack_overview.png)
  <figcaption>Overview of QOP stack for a single OPX+</figcaption>
</figure>


### PC to QPU Flow 

The first step in executing a program is writing a configuration file and a QUA program in your lab pc.
When executing it, the program is sent to the SOM inside the OPX+. The compiler, inside the SOM, is responsible for converting the QUA into low-level instructions
and sending them to the FPGA. Inside the FPGA are multiple cores designed to generate pulses which are then modulated by the internal oscillators.
The pulses are converted to analog signals using DACs and output through the front panel's analog ports.

### QPU to PC Flow

In addition to pulse transmission, the system can measure and analyze incoming pulses from the quantum hardware.
These pulses enter the analog input ports on the front panel and digitized by the ADCs. Then, a mathematical computation is performed on the signals and the relevant data, e.g., the demodulation results, is saved to the on-board memory.
Furthermore, the measurement results can be sent to the stream processing module, on the SOM, for further data manipulation and in turn are sent to the client PC.
