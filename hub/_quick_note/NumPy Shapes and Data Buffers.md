> Source: [Stack Overflow – Difference between numpy.array shape (R, 1) and (R,)](https://stackoverflow.com/questions/18691084/difference-between-numpy-array-shape-r-1-and-r)

The best way to think about NumPy arrays is that they consist of two parts:

1. A **data buffer** – a block of raw elements
2. A **view** – a description of how to interpret that buffer

---

## Example: One-Dimensional Array

```python
>>> a = numpy.arange(12)
>>> a
array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11])
```

Data buffer:

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│  0 │  1 │  2 │  3 │  4 │  5 │  6 │  7 │  8 │  9 │ 10 │ 11 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
```

Metadata:

```python
>>> a.flags
  C_CONTIGUOUS : True
  F_CONTIGUOUS : True
  OWNDATA : True
  WRITEABLE : True
  ALIGNED : True
  UPDATEIFCOPY : False
>>> a.dtype
dtype('int64')
>>> a.itemsize
8
>>> a.strides
(8,)
>>> a.shape
(12,)
```

Indexing layout:

```
i = 0   1   2   3   4   5   6   7   8   9  10  11
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│11│
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

---

## Reshaping the View

```python
>>> b = a.reshape((3, 4))
```

Now `b` is indexed with `b[i, j]`:

```
i = 0   0   0   0   1   1   1   1   2   2   2   2
j = 0   1   2   3   0   1   2   3   0   1   2   3
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│11│
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

```python
>>> b[2,1]
9
```

---

## Column-Major Order (`order='F'`)

```python
>>> c = a.reshape((3, 4), order='F')
```

```
i = 0   1   2   0   1   2   0   1   2   0   1   2
j = 0   0   0   1   1   1   2   2   2   3   3   3
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│11│
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

```python
>>> c[2,1]
5
```

---

## Shape with One Dimension of Size 1

```python
>>> d = a.reshape((12, 1))
```

```
i = 0   1   2   3   4   5   6   7   8   9  10  11
j = 0   0   0   0   0   0   0   0   0   0   0   0
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│11│
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

```python
>>> d[10, 0]
10
```

---

## Higher Dimensional Reshape

```python
>>> e = a.reshape((1, 2, 1, 6, 1))
```

```
i = 0   0   0   0   0   0   0   0   0   0   0   0
j = 0   0   0   0   0   0   1   1   1   1   1   1
k = 0   0   0   0   0   0   0   0   0   0   0   0
l = 0   1   2   3   4   5   0   1   2   3   4   5
m = 0   0   0   0   0   0   0   0   0   0   0   0
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│11│
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

```python
>>> e[0, 1, 0, 0, 0]
6
```

---

## Summary

- **`.reshape()`** creates a **new view**, not a copy.
- Dimensions of length 1 are flexible and allow high-dimensional reshaping.
- Indexing logic follows row-major (`C`) or column-major (`F`) depending on the `order` argument.

Use `reshape` freely—it's a safe and powerful tool for reinterpreting array structures without moving data.
