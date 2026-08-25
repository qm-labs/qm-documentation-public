# QUA "Best Practice" Guide

This article showcases best practices when writing in QUA to optimize user readability and performance. 
However, in certain situations, there is a clear tradeoff between the two. These cases will be noted to optimize your QUA program.

QUA is a new language that keeps evolving, and as a result, we expect this guide to evolve as well. 
Therefore, we would be happy to receive any comments or suggestions.

## General

- Pulse amplitude and duration should be set in the configuration whenever possible. 
  The reason being that modifying pulses in the program (i.e., `* amp()` and
  `duration`) requires real-time computation, which can introduce time gaps in the program's execution. 
  For example, if you require two different amplitudes, define two different operations.
  Ideally, real-time modification of pulses should only be used when sweeping parameters, either dynamically in QUA or manually.
  When troubleshooting timing for a sequence that uses values changed in real-time, the [QOP simulator](../Guides/simulator.md) is a valuable tool for predicting and verifying pulse timing. Alternatively, one can use [timestamp streams](features.md#timestamp-stream) during execution to record the actual start time of selected {{f("qm.qua.play")}} or {{f("qm.qua.measure")}}
  commands (see example below). 

    ??? "Timestamp stream example"

        ```python
        with program() as prog:
            delay = declare(int)
            wait_duration = declare(int)
            pulse_1_timestamp = declare_stream()
            pulse_2_timestamp = declare_stream()
            with for_each_(delay, debug_delays):
                assign(wait_duration, delay)
                play('x180', 'qubit', timestamp_stream=pulse_1_timestamp)
                wait(wait_duration, 'qubit')
                play('y90', 'qubit', timestamp_stream=pulse_2_timestamp)
            with stream_processing():
                pulse_1_timestamp.save_all("first_pulse")
                pulse_2_timestamp.save_all("second_pulse")
        ```

    After execution, fetch both timestamp streams and subtract paired entries on the client side to check whether a gap was introduced. **Use timestamp streams for debugging only**. Do not leave them enabled for long-running programs unless the timestamps are part of the required data, because they can add unnecessary stream-processing load.

- When several elements play to the same output port at the same time, their waveforms are
  [summed at the output](../Introduction/qua_overview.md#analog-waveform-manipulations). Keep the
  combined signal within the port's output range — if the sum of the simultaneous amplitudes exceeds
  full scale, the output overflows and is clipped.

- Beware of accumulated errors when using [sticky elements](features.md#sticky-element) and when using [frame rotations](../Introduction/qua_overview.md#updating-the-frame-phase). Make sure to reset the
  values using {{f("qm.qua.ramp_to_zero")}} and {{f("qm.qua.reset_frame")}}.

- Only define QUA variables for parameters you want to sweep or change in real-time. Otherwise, use Python variables.

- Always simulate your program to make sure that you are getting the correct behavior. If added gaps are problematic,
  the simulator can also be used to check the exact timing of pulses.

- There are issues that can occur in real time and produce unexpected output from the OPX, for example:

    - A division by zero
    - An overflow of a QUA variable
    - Trying to access an array out of bounds
    - Trying to play a pulse (or wait) for a duration \< 4 cycles

## Loops

- Use a different iterator variable for each flow-control loop (for example, {{f("qm.qua.for_")}} and {{f("qm.qua.for_each_")}}) whenever possible. Reusing the same iterator across many loops increases the compiler workload, which can lead to significantly longer compilation times, compilation timeouts, or, in extreme cases, the cluster becoming unresponsive. Additionally, reusing iterator variables across loops that were supposed to run in parallel, can cause the threads to be interlaced and break the intended parallelism. 

- Iterating with {{f("qm.qua.for_each_")}} loops adds a small overhead compared to using {{f("qm.qua.for_")}} loops.
  In addition, they require saving the entire array into the memory, resulting in a limited array length.

- Beware of fixed/floating point inaccuracies. In the following example, it is unclear whether 1.0 would be included
  in the sweep or not: `with for_(a, 0, a < 1.0, a + 0.1)`.
  Recommended practice to avoid that:

    - Define the sweep parameters and sweep array in advance:
  
      ```python
      # For floating/fixed:
      a_min = 0
      a_max = 1.0
      da = 0.1
      a_vec = np.arange(a_min, a_max + da/2, da)  # This includes a_max, use -da/2 to not include it
  
      # For integers:
      t_min = 10
      t_max = 100
      dt = 3
      t_vec = np.arange(t_min, t_max + 0.1, dt)  # This includes t_max, use t_max - 0.1 to not include it
      ```
  
    - When sweeping a fixed point number, use the same syntax `with for_(a, a_min, a < a_max + da/2, a + da)`.
  
    - When sweeping an integer, use `<` or `<=`: `with for_(t, t_min, t <= t_max, t + dt)`

## Macros

- Use macros the same way you would use functions in python - To allow reuse of code
  ([DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)) and to simplify the main code readability.

- QUA variables are always global. This means that you can use variables without passing them as an input and that
  any variable which is changed inside the macro, **regardless of whether it was given as an input or not**, will
  also be changed outside of the macro.
  This is sometimes known as `pass-by-reference` as opposed to `pass-by-value`. In other words, QUA variables should
  be treated as pointers to the real, hidden, variables.

- In order make it a bit more clear, we recommend the following:

    - If there are external QUA variables which are needed in the macro, they should be passed as variables to the
      macro.
    - Any other QUA variable used by the macro should be declared inside the macro.
    - If a QUA variable, given as an input to the macro, is to be changed **and we do not want the change to happen externally**,
      then the variable should be assigned to a local variable.
    - Any QUA variable, which is declared/changed inside the macro, and is needed in the external program, should be
      returned by the macro.

  For example:

  ```python
  def some_macro(qubit_state, var_for_calculation)  # Two variables coming from the outside
      temp = declare(fixed)  # Local variable only for this macro
      important_var = declare(bool, value=False)  # Local variable declared inside, but then passed back outside
      ...
      assign(temp, temp * var_for_calculation)  # Notice we do not change var_for_calculation, but declare a local variable "temp"
      with if_((temp > 0.1) & (qubit_state == 1)):
          ...
          assign(important_var, True)
          assign(qubit_state, 0)

      return qubit_state, important_var  # We send back qubit_state and important_var

  with program() as example_prog:
      ...
      qubit1_state, b_happened = some_macro(qubit1_state, i)
      ...
  ```
