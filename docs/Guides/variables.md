# Variables in QUA

The following page describes the three types of variables in QUA: Integers, fixed point numbers and booleans, and how Python and NumPy values convert into them.

## Definitions

### Integers

Integers in QUA are 32 bit, so their range is  $[-2^{31}, 2^{31}-1]$ which is roughly $\pm 2e9$.

To create an integer variable we {{f("qm.qua.declare")}} as follows:

```python
i = declare(int)  # creates a variable named "i" of type integer
```

!!! Warning
    If assigning a value outside the range, the variable will overflow. When a variable overflows, the value will "wrap around". For example:

    ```python
    big_number = declare(int)
    assign(big_number, 2**31-1)
    # big_number is now 2^31-1
    assign(big_number, big_number+1)
    # big_number is now -2^31
    ```

### Fixed point numbers

Fixed point numbers in QUA are in 4.28 format. There are 4 integer bits, including a sign bit, and 28 fractional bits.
Therefore, the range of the fixed point number is $[-8, 8)$ in steps of $2^{-28} = ~3.7e-9$.

To create a fixed variable we {{f("qm.qua.declare")}} as follows:

```python
i = declare(fixed)  # creates a variable named "i" of type fixed point
```

!!! Note
    If assigning a value larger than 8, the variable will overflow. When a variable overflows, the value will be the modulo 16 unsigned, i.e. $((x + 8) % 16) - 8$.
    In other words, the value will be wrapped around the range. For example:

    - $8.0 \rightarrow -8.0$
    - $9.0 \rightarrow -7.0$
    - $17.0 \rightarrow 1.0$
    - $100.0 \rightarrow 4.0$

### Booleans

To create a boolean variable we {{f("qm.qua.declare")}} as follows:

```python
b = declare(bool)  # creates a variable named "b" of type fixed boolean
```

## Casting from Python

When a Python value — an `int`, `float`, `bool`, or a NumPy scalar (`np.integer`, `np.floating`, `np.bool_`) — is used where a QUA value is expected (for example as the `value` argument of {{f("qm.qua.declare")}}, in {{f("qm.qua.assign")}}, or as an argument to a QUA function such as {{f("qm.qua.amp")}}), it is cast automatically to the corresponding QUA type. NumPy scalars are first converted to their Python primitive equivalent, and then follow the same conversion rules below.

### Casting to integers

Mixing arithmetics of a QUA integer with python literals of type float will keep the integer type.

```python
i = declare(int, value=3)  # creates a variable named "i" of type integer with value 3
assign(i, i + 0.7)  # i stays a QUA integer, 0.7 is rounded down, and the value of i remains 3
assign(i, 10 * (i + 1.2))  # i stays a QUA integer, 1.2 is rounded down to 1, and this results in "10 * 4"
# when the bracket is expanded it will yield a different result
assign(i, 10 * i + 10 * 1.2)  # "10 * 1.2" is being calculated first, so this results in "10 * i + 12"
```

### Casting to fixed point numbers

A Python float is converted to the fixed point representation as `int(round(f * 2**28))`. Rounding follows the same round-half-to-even convention as `numpy.round()` (IEEE 754), not round-half-away-from-zero.

!!! Note
    `np.float16` and `np.float32` values can convert to a different value than expected: converting a reduced-precision NumPy float to a Python `float` widens it rather than reproducing the original decimal value (for example, `np.float32(0.85)` becomes `0.8500000238418579`, not `0.85`). Use a native Python `float` or `np.float64` when the exact literal value matters.

### Casting to booleans

When assigning the truth value of the boolean, every non-zero value will be considered as true, and zero will be false. For example:

```python
b = declare(bool)

## True:
assign(b, True)
assign(b, 4<8)
assign(b, 2)
assign(b, 0.1)

## False:
assign(b, False)
assign(b, 4>8)
assign(b, 0)
assign(b, 0.0)
```

!!! Note
    This automatic conversion only applies to Python/NumPy values. QUA does not cast automatically between its own types — converting a QUA variable or expression from one type (`int`, `fixed`, `bool`) to another always requires an explicit call to the [Cast library](qua_ref.md#cast). See [Casting between QUA types](#casting-between-qua-types) below.

## Casting between QUA types

QUA enables casting between different types of variables using the [Cast library](qua_ref.md#cast).
There are three normal casting operations, two casting by multiplication operations and two "unsafe" casting operations.

We list a few things to note while casting from one type to another:

- Casting from int to fixed only gives an expected result when the integer is in the range \[-8,7\]. Otherwise, the result fixed variable will overflow.
- Casting to Boolean, will behave according to the examples above.
- The unsafe casting operation {{f("qm.qua.lib.Cast.unsafe_cast_fixed")}} treats the input, bitwise, as a fixed number. When applied to an integer, this is equivalent to a multiplication by $2^{-28}$.
- The unsafe casting operation {{f("qm.qua.lib.Cast.unsafe_cast_int")}} treats the input, bitwise, as an integer. When applied to a fixed number, this is equivalent to a multiplication by $2^{28}$.
