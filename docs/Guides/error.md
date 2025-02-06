# Messages and Errors

The following section describe how to manage the outputted level of messages to the console, as well as common runtime errors.

## Messages control

As part of the normal program flow, there are messages which are outputted into the python console. There are four
different level of messages:

1. Debug - Debug messages, off by default.
2. Info - Normal OPX status, mainly when executing a program.
3. Warnings - Important warnings, such as client version does not match server version.
4. Errors - Error messages, usually compilation errors.

It is possible to change the level which is outputted by adding it to the `QuantumMachinesManager` object:

```python
from qm import QuantumMachinesManager

qmm = QuantumMachinesManager(host='...', port=..., log_level=level)
```

Where *level* can be either *'DEBUG'*, *'INFO'*, *'WARNING'* or *'ERROR'*.

After the `QuantumMachinesManager` object is created, it is possible to change the level of the messages by using the following command:
```python
from qm.logging_utils import set_logging_level
set_logging_level(level)
```

!!! Note
    We do not recommend setting the level to *'ERROR'*, as important warning messages might be missed.

!!! Note
    It is possible to disable the output of the logger into the stdout by adding an environment variable named
    `QM_DISABLE_STREAMOUTPUT` to the OS

## Runtime Errors

When running a QUA program, run-time errors may occur. In this section we address all common error
types and explain how they are handled. We also explain how to send error logs to QM for support
and debugging purposes.

Runtime errors can be indicated in one of two ways:

1. When fetching results, if a runtime error occurred, a warning message will be printed
2. by calling `QmJob.execution_report()` and querying its output.

Below we outline different runtime error types and what do they mean.

### Analog output overflow

Indicates if the value played to an analog output at any sample is outside the range -0.5 to $0.5 - 2^{-16}$,
which causes an output overflow.

!!! Note
    It is possible for an overflow to occur with no indication. Therefore when in doubt, it always smart to double check
    using a scope or a simulation.

### Error code 10201

The error message says: "General error in inter-controller communication detected on the sending/receiving side in controller XXX - please gather logs and report to QM"
This is a known false error and can be ignored. If you encounter in addition any data integrity issues, please report to us.

<!-- % **Detailed explanation**

%

% The :math:`I` and :math:`Q` waveforms undergo multiplication by

% an amplitude scaling matrix (see :ref:`Amplitude transformations`), then by

% the IF rotation + frame matrix waveform matrix and finally

% by the mixer correction matrix (see :ref:`Mixed Inputs Element`). The waveform signal is then

% added to the DC offset values, and this is output to the analog output. Overflow errors can occur anywhere within

% the signal chain and are hard to catch. This error type will indicate if such an overflow

% error occurred anywhere during the runtime of the program.

%

% .. note::

%

% Starting from version 0.6, the behavior of the analog output when an overflow is that the output

% will be clipped to the maximal value rather than wrap-around (e.g 0.5 will not be wrapped around to -0.5

% but will instead be clipped to 0.5 - 2^-16).

%

% *********************

% Demodulation overflow

% *********************

%

% Indicates if an overflow occurred in the signal demodulation chain.

%

% **Detailed explanation**

%

% When using the integration and demodulation features of the :func:`~qm.qua._dsl.measure` statement,

% a complex :ref:`Demodulation and measurement<demodulation>` sequence occurs in the controller. It is

% crucial to select the integration weights so that overflow will not occur within the process, using the

% following rule of thumb:

%

% *make sure the integration weights are such that when they multiply the raw ADC data, scaled to between -0.5 and 0.5, the result is between -2 and 2.*

%

% For additional details how to avoid demodulation overflow errors, refer to :ref:`Fixed point format`.

%

% ************

% Amp overflow

% ************

%

% Indicates an overflow error in `* amp()`, for values outside -8 to 8 - 2^-28 (see :ref:`Amplitude transformations`).

%

% For example:

%

% .. code-block:: python

%

% x = declare(fixed)

% assign(x, 13.4)

% play('pulse1' * amp(x), 'qe1')

%

% *************************

% Update frequency overflow

% *************************

%

% TODO

%

% **************************

% Correction matrix overflow

% **************************

%

% Indicates an overflow in the correction matrix used to output a pulse, for values outside -2 to 2 - 2^-16.

% Relevant for correction matrices set in the configuration or in :func:`~qm.qua._dsl.update_correction`.
%
% ******************************
% Out of bounds array read/write
% ******************************
%
% .. warning::
%
%     Currently errors are *not indicated* for out of bounds array read/write and this is the responsibility of the user.
%
% ********************************
% Invalid wait time/pulse duration
% ********************************
%
% .. warning::
%
%     Valid wait times/pulse durations are between 4 clock cycles (16 nsec) to 2^24 clock cycles (2^26 nsec).
%     Runtime values outside this range are *not indicated* and may lead to unexpected results.
%
% ********************
% Invalid calculations
% ********************
%
% .. warning::
%
%     Invalid calculations, such as division by 0 or calculations which leads to overflows, are *not indicated*. -->
