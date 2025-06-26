# Real-Time Communication and Feedback

The OPX makes it seamless to pass data between different controllers/FEM (Front End Module in the OPX1000), and to perform feedback based on that information.

## Variables

=== "OPX1000"

    {{ requirement("QOP", "3.3") }}

    Variables are generally available for all elements, and the user does not need to worry about assigning them to specific elements.
    However, when performing measurements, the result value is only saved for the element that is being measured.
    When the user attempts to use this variable for feedback purposes, it is automatically passed to any element that needs it.
    
    ### Broadcast Operations
    
    When operating with a multi-qubit system, the logical AND, OR or XOR between the state of all qubits is often needed for feedback purposes.
    The `broadcast` operations allow to pass this information from one element to all other elements in a more efficient way:

    - [`Broadcast.and_()`][qm.qua._dsl.Broadcast.and_]: Performs a logical AND operation on boolean variables and broadcasts the result to all elements. Can take any number of boolean variables or arrays as input.
    - [`Broadcast.or_()`][qm.qua._dsl.Broadcast.or_]: Performs a logical OR operation on boolean variables and broadcasts the result to all elements. Can take any number of boolean variables or arrays as input.
    - [`Broadcast.xor_()`][qm.qua._dsl.Broadcast.xor_]: Performs a logical XOR operation on a boolean variables and broadcasts the result to all elements. Can take any number of boolean variables or arrays as input.

    !!! Note
    
        When working in a multi-controller system, the `broadcast` operations are required and the feedback operation would give an error if not used.
    
    === "Example - 2 Qubits Active Reset"
        
        ```python
        I1 = declare(fixed)
        I2 = declare(fixed)
        s1 = declare(bool)
        s2 = declare(bool)
        feedback_cond = declare(bool, value=True)
        
        with while_(feedback_cond):  # Looping until the feedback condition is met (repeat until success)
            measure('readout', 'resonator1', None, dual_demod.full('cos', 'sin', I1))
            measure('readout', 'resonator2', None, dual_demod.full('cos', 'sin', I2))
    
            assign(s1, I1 > th1)  # Assigning the condition (qubit state) to a boolean variable
            assign(s2, I2 > th2)  # Assigning the condition (qubit state) to a boolean variable
            assign(feedback_cond, ~broadcast.and_(s1, s2))  # Combining the states using logical AND, and broadcasting the result
        
            play('pi', 'qubit1', condition=broadcast.and_(s1))  # Using the broadcasted boolean variable in the conditional play command
            play('pi', 'qubit2', condition=s2)  # Using the boolean variable directly in the conditional play command, this would do an implicit broadcast
        ```
    
=== "OPX+"

    Variables are generally available for all elements, and the user does not need to worry about assigning them to specific elements.
    However, when performing measurements, the result value is only saved for the element that is being measured.
    When the user attempts to use this variable for feedback, it is automatically passed to any element that needs it.

    === "Example - 2 Qubits Active Reset"

        ```python
        from qm.qua import *
        I1 = declare(fixed)
        I2 = declare(fixed)
        s1 = declare(bool)
        s2 = declare(bool) 
        feedback_cond = declare(bool, value=True)
        
        with while_(feedback_cond):  # Looping until the feedback condition is met (repeat until success)
            measure('readout', 'resonator1', None, dual_demod.full('cos', 'sin', I1))
            measure('readout', 'resonator2', None, dual_demod.full('cos', 'sin', I2))
        
            assign(s1, I1 > th1)  # Assigning the condition (qubit state) to a boolean variable
            assign(s2, I2 > th2)  # Assigning the condition (qubit state) to a boolean variable
            assign(feedback_cond, s1 & s2)  # Combining the states using logical AND
        
            play('pulse', 'qubit', condition=I1>th1)  # Directly using the variable and threshold (qubit state) in the conditional play command
            play('pulse', 'qubit', condition=s2)  # Using the boolean variable in the conditional play command
        ```

!!! Note
    The example above uses a conditional play command to demonstrate how to use variables for feedback purposes
    The same rules apply for any other command that would requires usage of a variable obtained from a measurement