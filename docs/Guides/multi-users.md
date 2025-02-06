
# Job Queue and Multiple Users

The Quantum Orchestration Platform offers the ability for multiple users to work simultaneously.
There are two possibilities for multiple users who wish to use the OPX together - Working with multiple [quantum machine](../Introduction/qop_overview.md#quantum-machine)
(hereafter, `qm`) instances or using the job queue.

!!! important
    The subject is also relevant for a single user who wishes to work with multiple programs simultaneously.

The following guide will describe the relevant considerations for when and how to use each method.


## Multiple QMs

Working in the multi-`qm` method is advisable for multiple users who **don't** work on the same quantum system
but would like to share the QOP. For example, it can be helpful when several setups are connected to the same QOP.

In that case, each setup will have its unique configuration, and define its own `qm`.

Once the multiple `qms` are open, the users can simultaneously and seamlessly execute programs on their `qm`, as long as there are enough resources.
That means, for example, that the total number of [threads](features.md#threads) in use across all programs can't exceed the total number of threads in the system.

To use multiple `qms` simultaneously, each `qm` needs to have a unique configuration and they should not share ports.
By default, opening a `qm` closes any existing `qms`.
This has to be changed in order for multiple users to be able to work together. For example:

```python
qmm = QuantumMachinesManager()

config_1 = {...}
config_2 = {...}

qm1 = qmm.open_qm(config1, close_other_machines=False)
qm2 = qmm.open_qm(config2, close_other_machines=False)
```

We can then send programs for execution on both `qms` regularly. At the end of the script, it is advisable to close the `qms`, using:

```python
qm1.close()
qm2.close()
```

!!! Note
    If the users work on different client computers, each script will open its own `qm`.

### Multi-QMs with shared ports

In {{ requirement("QOP", "2") }}, multiple `qms` are allowed to share ports. The port sharing must be explicitly defined in **both** configurations.
Sharing ports between `qms` allows two users (or two experiments) to access the resources, which
could be useful for multiplexing or for monitoring.
To enable port sharing, you need to add `"shareable": True` in the port's dictionary. For example:

```python
'analog_outputs': {
    1: {'offset': 0.1, "shareable": True},
    },
'analog_inputs': {
    1: {'offset': 0, "shareable": True},
    2: {'offset': 0},
```

!!! Note
    Port sharing is possible between any number of multiple `qms`.

!!! warning
    Sharing ports mean that one `qm` could interfere with the experiment running in another `qm`
    in multiple ways:

    1. Direct interference - For example, both `qms` applying operations on the same qubit.
    2. If both `qms` are playing at the same time, overflows might occur even if each `qm` by itself doesn't cause an overflow.
    3. A `qm` saving too much data (mostly ADC traces at a fast rate), could crash the QOP.

## Job Queue

The queue system enables users to send multiple jobs to the orchestration platform, which are then run in turn.
It provides tools to add and remove jobs from the queue as well as receive additional information such
as the identity of the initiating user and the job start time.

If several users wish to work with **the same qm**, then the job queue is the preferred method. For example, it can be useful
when there's a single setup and several users would like to execute different programs on it, using a single configuration.

!!! tip
    In addition, the job queue can be used to send [pre-compiled programs](features.md#precompile-jobs) to the `QOP`,
    enabling fast execution of repeated programs.

### Multiple Users Interaction with the Queue

In the scenario of multiple users who wish to work with the job queue, one user will open a `qm` locally, and the rest will use it by getting a local instance from the `qmm`.
For example, user #1 works on his script and opens a `qm`:

```python
qmm = QuantumMachinesManager()
qm = qmm.open_qm(config)

>>> qm.id
>>> 'qm-1658058752694'
```

Then, another user will work on his script, and access the "active" `qm`:

```python
qmm = QuantumMachinesManager()
qm_list =  qmm.list_open_quantum_machines()
qm = qmm.get_qm(qmm_list[0])

>>> qm.id
>>> 'qm-1658058752694'
```

Both users now have a local instance of the same `qm` and can use the queue to send jobs.

### Adding to Queue

The queue is accessed by member functions of {{f("qm.api.v2.qm_api.QmApi")}}.
The following adds a job to the queue:

```python
# Adding to the queue
qm.queue.add(program)  # adds at the end of the queue
qm.queue.add_to_start(program)  # adds at the start of the queue
```

### Inspecting the Queue

You can observe the queue and get the number of currently pending jobs as follows:

```python
qm.queue.count  # number of items in the queue.
len(qm.queue) # same as count
```

The queue can be queried by either `job_id` or by position in queue.
The queue is composed of instances of the {{f("qm.jobs.pending_job.QmPendingJob")}} object, so queries return such instances.

Important note: The queue is 1-based

```python
qm.queue.pending_jobs  # returns the list of jobs ids in the queue by the order they are in it (a list of QmPendingJob)
qm.queue.get_at(position)  # returns a QmPendingJob object
qm.queue[position] # the QmPendingJob at position
qm.queue.get(job_id) # returns a QmPendingJob object
qm.queue.get_by_user_id(user_id) # returns a QmPendingJob object
```

### Interacting with a Pending Job Object

A pending job object allows access to its run state and other information.
This, for example allows to perform a blocking wait until the job completes:

```python
pending_job = qm.queue.get_at(2)
pending_job.user_added  # user who executed
pending_job.position_in_queue() # return the current position in the queue
pending_job.time_added  # when the job was added to the queue
pending_job.wait_for_execution()  # waits until the job is executed (or aborted) and returns a QmJob.
```

### Removing Pending Jobs from Queue

Jobs can be removed from the queue by `job_id`, position or `user_id`.
Note that any user can remove any job from the queue.
There is no facility to protect jobs from accidental removal.
Also note that removing a job by position in queue can be unpredictable as the position of jobs change with time
and so calling the remove by position function may remove a different job to that intended.

```python
pending_job = qm.queue[2]
pending_job.cancel()  # remove from the queue
# Or
qm.queue.remove_by_id(job_id)  # removes by the job_id
qm.queue.remove_by_position(position)  # removes by the position in the queue. Might be dangerous because position can change during the request
qm.queue.remove_by_user_id(user_id)  # removes all jobs that belong to the user
```

### Job Queue API

See [the job queue API](../API_references/qm_api.md#queue-api) for a full list of commands.
