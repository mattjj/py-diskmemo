import os, shelve, inspect, functools

cache_dirname = 'cached_func_calls'

# TODO add support for varargs and kwargs
# TODO inspect.getcallargs in python27 would do the parsing stuff for me
# TODO add support for instance methods... do i need a class-based decorator?
# then i can't use functools.wraps
# TODO modulename.functionname instead of just functionname

def cache(f):
    if not os.path.isdir(cache_dirname):
        os.mkdir(cache_dirname)
        print 'Created cache directory %s' % os.path.join(os.getcwd(),cache_dirname)

    cachefilename = os.path.join(cache_dirname,f.__name__)
    cache = shelve.open(cachefilename,protocol=2)

    spec = inspect.getargspec(f)
    if spec.varargs is not None or spec.keywords is not None:
        print 'Warning: cannot disk cache %s because it has varargs or keyword args. Must improve implementation.' % f.__name__
        return f

    default_vals = spec.defaults if spec.defaults is not None else []
    default_args = dict((argname,val) for argname,val in zip(spec.args[-len(default_vals):],default_vals))

    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        full_arglist = list(args)
        for argname in spec.args[len(args):]:
            if argname in kwargs:
                full_arglist.append(kwargs[argname])
            elif argname in default_args:
                full_arglist.append(default_args[argname])
            else:
                raise TypeError, 'unexpected argument in %s: %s' % (f.__name__,argname)
        key = str(full_arglist)

        try:
            return cache[key]
        except KeyError:
            value = f(*args,**kwargs)
            cache[key] = value
            cache.sync()
            return value
        except TypeError:
            print 'Warning: could not disk cache call to %s because arguments could not be made into strings' % f.__name__
            return f(*args,**kwargs)
    return wrapper
