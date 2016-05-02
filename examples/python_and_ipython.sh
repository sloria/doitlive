echo 'Lets run some python'

```python
fruits = ['Banana', 'Apple', 'Lime']
loud_fruits = [fruit.upper() for fruit in fruits]
```

echo 'We can also run in ipython mode'

```ipython
def fib(n):
    a, b = 0, 1
    while a < n:
        print(a, end=' ')
        a, b = b, a+b
    print()

# Magic!
% time fib(100)

```
