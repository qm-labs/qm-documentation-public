# Classical Computations in QUA

This section describes standard syntax rules for classical computations in QUA.

## Arithmetic Expressions

Multiplication, addition and subtraction of fixed point variables is supported.

!!! Note
    division incurs a computational overhead of approximately 400 ns per operation.

| Operator       | Symbol | Example |
| :------------- | :----: | :-----: |
| multiplication | \*     | a * b   |
| division       | /      | a / b   |
| addition       | +      | a + b   |
| subtraction    | -      | a - b   |

```python
with program() as prog:

        a = declare(fixed)
        b = declare(int)
        c = declare(fixed, value=0.3)
        d = declare(fixed, value=-0.02)
        e = declare(int, value=3)
        f = declare(int, value=5)

        assign(a, c*d-d+c*0.25)
        assign(b, e+f*123*e-e)
        assign(c, d/c)

        save(a, "a")
        save(b, "b")
        save(c, "c")
```

The evaluation of each operator takes only a few clock cycles. For example, the addition (+) and subtraction (-) operations
each take 1 clock cycle to evaluate, i.e. 4 ns.
However, the compiler parallelize operations, resulting in a much reduced effective calculation time which will often be zero.

## Bitwise Operations

Left/right bitshifts and bitwise AND, OR, and XOR are supported.

| Operator       | Symbol | Usage    | Example      |
| -------------- | :----: | :------: | ------------ |
| left bitshift  | <<     | a << b   | 6\<\<5 = 192 |
| right bitshift | >>     | a >> b   | 6>>1 = 3     |
| bitwise AND    | &      | a & b    | 6&5 = 4      |
| bitwise OR     | \|     | a \| b   | 6\|5 = 7     |
| bitwise XOR    | ^      | a ^ b    | 6^5 = 3      |

!!! Note
    The bitwise NOT operation (~a) is not supported.

## Boolean Operations

Boolean operations can be used, but using the operators below ('&', '|', etc) and not with the Pythonic operators ('AND', 'OR', etc)

!!! warning
    Attempting to use Pythonic operators on QUA variables, or attempting to evaluate QUA variables directly
    (for example, in a Pythonic '`if`' statement), would result in an error.

| Operator | Symbol | Example |
| -------- | :----: | ------- |
| AND      | &      | a & b   |
| OR       | \|     | a \| b  |
| XOR      | ^      | a ^ b   |
| NOT      | ~      | ~a      |

Compounded boolean expressions are supported.

!!! Note
    It is necessary to wrap the atomic boolean expressions in parenthesis as seen in the example below,
    due to Python operator precedence rules.

Example:

```python
with if_( (~( a > b )) | ( c > d) ):
```

## Arrays

QUA arrays are defined and accessed as follows.

1. {{f("qm.qua._dsl.declare")}} a new array:

Syntax:

`declare(fixed/int/bool, size=N)` - Will create a QUA array of zeros with size `N`

`declare(fixed/int/bool, value=[…])` - Will create a QUA array with the values specified in the list  

### Examples:

#### Declaration:

```python
a1 = declare(int, size=3)
a2 = declare(int, value=[1,2,3])
```

!!! Note
    Specifying both the `size` and the `value` parameters is not supported.

!!! Important
    Array length is fixed and cannot be changed after declaration.

#### Access cell in array

```python
# syntax and examples
assign(a1[0], 5)
assign(b, a1[i]+6)
assign(a1[i+5], a2[i+4])
save(a1[2], "v1_2")
```

!!! Warning
    No validation is performed for reading/writing out of bounds.

#### Get array length

```python
# syntax and examples
length = declare(int)
assign(length, v1.length())
```

#### More examples:

```python
with program() as arrays_use:

  v1 = declare(int, value = [1, 2, 4, 8, 16])
  v2 = declare(int, size = 5) # will be initialized with zeros
  v3 = declare(fixed, size = 30)  # will be initialized with zeros
  i = declare(int)

  assign(v3[0], 16)

  with for_(i, 0, i < v2.length(), i + 1):
        assign(v2[i], i*2)

  with for_(i, 0, i < v1.length(), i + 1):
        assign(v2[i], v2[i] + v3[i])

  with for_(i, 0, i < v1.length(), i + 1):
        save(v1[i], "v1")
        save(v2[i], "v2")

  with for_(i, 0, i < v3.length(), i + 1):
        save(v3[i], "v3")
```

## Computational library functions

QUA allows the user the real time evaluation of several mathematical operators and functions.
Besides the standard mathematical operators (+, -, \*, /) the user can access various libraries including

- [Math](../API_references/qua/math.md#math-functions) - trigonometric functions, array reduction functions etc.
- [Random](../API_references/qua/random.md#random-numbers) - pseudo-random number generation.
- [Cast](../API_references/qua/cast.md#casting) - allows casting between QUA variable types.
- [Utility](../API_references/qua/util.md#utility) - Miscellaneous operators, including a hardware optimized conditional expression.

### Math

For a full description, please see the [Math library reference page](../API_references/qua/math.md#math-functions).

#### Trigonometric functions

- `Math.cos(x)` : Takes the cosine of a fixed in radians
- `Math.sin(x)` : Takes the sine of a fixed in radians
- `Math.cos2pi(x)` : Takes the cosine of a fixed in 2pi radians
- `Math.sin2pi(x)` : Takes the cosine of a fixed in 2pi radians

`cos2pi(x)` and `sin2pi(x)` are equivalent to `cos(2*pi*x)` and `sin(2*pi*x)` but saves a few clock cycles as the extra multiplication
stage required to calculate `2*pi` are removed by simply having `2*pi` stored in memory.
Moreover, these functions are immune to overflows.
So whenever working with radians we suggest using the former. The usage is straightforward, for example:

```python
amplitude = declare(fixed)
time = declare(int)
frequency = declare(int)
assign(amplitude, 1)
assign(frequency, 1e6)
with for_(time, 0, time<100, time+1):
    play('pulse_1' * amp(amplitude*Math.cos2pi(frequency*time)), 'element_1')
```

This program will play `pulse_1` for 100 iterations, where for each iteration the amplitude will be modulated by the envelope function `cos(2pi * frequency * time)`.
For evaluation of non-real time mathematical expressions one can always use standard python libraries such as numpy.

#### Array reduction

QUA provides several function to reduce arrays. These functions run more efficiently (with less latency) when compared to a manual implementing in QUA, as they use hardware optimizations.

- `Math.sum(x)` : sums an array. The result is of the same type as the input array.
- `Math.max(x)`, `Math.min(x)` : max,min an array. The result is of the same type as the input array.
- `Math.argmin(x)`/`Math.argmax(x)`: returns the index of the max/min
- `Math.dot(x,y)`: returns the dot product of two QUA arrays of the same size

#### Others

- `Math.abs(x)` : absolute value of a QUA variable

### Random number generator

For a full description, please see the [Random library reference page](../API_references/qua/random.md#random-numbers).

This class generates a pseudo-random number using a the [LCG algorithm](https://en.wikipedia.org/wiki/Linear_congruential_generator) with the following parameters: a = 137939405, c = 12345, m = 2\*\*28.

The class constructor optionally takes a seed number and can generate `int` or `fixed` values.

!!! Note
    Unless specified explicitly, the seed is selected in python using the [RNG module](https://docs.python.org/3/library/random.html). 
    The seed choice occurs when the program object is created, which means that if we execute a QUA program object several times, 
    the QUA random numbers sequence will be the same for all executions. To have a new seed, one needs to

```python
with program() as prog:
    r = Random()
    # you can set the seed:
    r.set_seed(123213)
    a = declare(int)
    b = declare(fixed)
    assign(a, r.rand_int(100)) # a will be a number between 0 and 99
    assign(b, r.rand_fixed()) # b will be a number between 0.0 and 1.0

```

### Cast

For a full description, please see the [Casting library reference page](../API_references/qua/cast.md#casting).

- `Cast.mul_fixed_by_int(x,y)`: Multiplies a fixed x by an int y, returning a fixed
- `Cast.mul_int_by_fixed(x,y)`:  Multiplies an int x by a fixed y, returning an int
- `Cast.to_int(x)`: Casts a variable to int. Supports int, fixed or bool
- `Cast.to_fixed(x)`:  Casts a variable to fixed. Supports int, fixed or bool
- `Cast.to_bool(x)`:  Casts a variable to bool. Supports int, fixed or bool

### Util

For a full description, please see the [Utility library reference page](../API_references/qua/util.md).

- `Util.cond(a,b,c)` : Quick conditional operation.

This is equivalent to a ternary operator available in some languages:
i.e. a ? b : c, meaning 'b' if 'a' is true, or 'c' if 'a' is false.
There is less computation overhead (less latency) when running this operation relative to the `if_` conditional

```python
assign(b, Util.cond(a > b, c, d))
```
