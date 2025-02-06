# Variables in QUA

The following page describes the three types of variables in QUA: Integers, fixed point numbers and booleans.

## Definitions

### Integers

Integers in QUA are 32 bit, so their range is  $[-2^{31}, 2^{31}-1]$ which is roughly $\pm 2e9$.

To create an integer variable we {{f("qm.qua._dsl.declare")}} as follows:

```python
i = declare(int)  # creates a variable named "i" of type integer
```

!!! warning
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

To create a fixed variable we {{f("qm.qua._dsl.declare")}} as follows:

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

To create a boolean variable we {{f("qm.qua._dsl.declare")}} as follows:

```python
b = declare(bool)  # creates a variable named "b" of type fixed boolean
```

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

## Casting

QUA enables casting between different types of variables using the [Cast library](qua_ref.md#cast).
There are three normal casting operations, two casting by multiplication operations and two "unsafe" casting operations.

We list a few things to note while casting from one type to another:

- Casting from int to fixed only gives an expected result when the integer is in the range \[-8,7\]. Otherwise, the result fixed variable will overflow.
- Casting to Boolean, will behave according to the examples above.
- The unsafe casting operation {{f("qm.qua.lib.Cast.unsafe_cast_fixed")}} treats the input, bitwise, as a fixed number. When applied to an integer, this is equivalent to a multiplication by $2^{-28}$.
- The unsafe casting operation {{f("qm.qua.lib.Cast.unsafe_cast_int")}} treats the input, bitwise, as an integer. When applied to a fixed number, this is equivalent to a multiplication by $2^{28}$.
