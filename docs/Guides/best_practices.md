# QUA "Best Practice" Guide

This article showcases best practices when writing in QUA to optimize user readability and performance. 
However, in certain situations, there is a clear tradeoff between the two. These cases will be noted to optimize your QUA program.

QUA is a new language that keeps evolving, and as a result, we expect this guide to evolve as well. 
Therefore, we would be happy to receive any comments or suggestions.

## General

- Pulse amplitude and duration should be set in the configuration whenever possible. 
  The reason being that modifying pulses in the program (i.e., `* amp()` and
  `duration`) requires real-time computation, which can introduce time gaps in the program's execution. 
  For example, If you require two different amplitudes, define two different operations.
  Ideally, real-time modification of pulses should only be used when sweeping parameters, either dynamically in QUA or manually.

- Beware of accumulated errors when using [sticky elements](features.md#sticky-element) and when using [frame rotations](../Introduction/qua_overview.md#updating-the-frame-phase). Make sure to reset the
  values using {{f("qm.qua._dsl.ramp_to_zero")}} and {{f("qm.qua._dsl.reset_frame")}}.

- Only define QUA variables for parameters you want to sweep or change in real-time. Otherwise, use Python variables.

- Always simulate your program to make sure that you are getting the correct behavior. If added gaps are problematic,
  the simulator can also be used to check the exact timing of pulses.

- There are issues that can occur in real time and produce unexpected output from the OPX, for example:

    - A division by zero
    - An overflow of a QUA variable
    - Trying to access an array out of bounds
    - Trying to play a pulse (or wait) for a duration \< 4 cycles

## Loops

- Iterating with {{f("qm.qua._dsl.for_each_")}} loops adds a small overhead compared to using {{f("qm.qua._dsl.for_")}} loops.
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
