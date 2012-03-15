import diskcache

@diskcache.cache
def fib(n):
    "Return the nth Fibonacci number."
    if n in (0,1):
        return n
    return fib(n-1) + fib(n-2)

