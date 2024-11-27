import functools

#Memoization is an optimization technique that stores the results of expensive function calls 
#and returns the cached result when the same inputs occur again.
def memoize(method):
    @functools.wraps(method)
    def memoizer(*args, **kwargs):
        method._cache = getattr(method, '_cache', {})
        key = args
        if key not in method._cache:
            method._cache[key] = method(*args, **kwargs)
        return method._cache[key]
    return memoizer
