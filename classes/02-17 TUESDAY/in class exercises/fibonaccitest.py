def fibonacci(n):
   
    fib = [0,1]
    for idx in range(2, n):
        fib.append(fib[idx - 2] + fib[idx - 1])
    print(fib)
    return fib[n-1]
    
    pass

print(fibonacci(5))

n = int(len(lst) ** 0.5)

if n * n != len(lst):

return [lst[i:i+n] for i in range(0, len(lst), n)]