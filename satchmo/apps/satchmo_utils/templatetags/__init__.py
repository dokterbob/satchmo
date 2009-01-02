def _stripquotes(val):
    stripping = True
    while stripping:
        stripping = False
        if val[0] in ('"', "'"):
            val = val[1:]
            stripping = True
        if val[-1] in ('"', "'"):
            val = val[:-1]
            stripping = True

    return val

def get_filter_args(argstring, keywords=(), intargs=(), boolargs=(), stripquotes=False):
    """Convert a string formatted list of arguments into a kwargs dictionary.
    Automatically converts all keywords in intargs to integers.

    If keywords is not empty, then enforces that only those keywords are returned.
    Also handles args, which are just elements without an equal sign

    ex:
    in: get_filter_kwargs('length=10,format=medium', ('length'))
    out: (), {'length' : 10, 'format' : 'medium'}
    """
    args = []
    kwargs = {}
    if argstring:
        work = [x.strip() for x in argstring.split(',')]
        work = [x for x in work if x != '']
        for elt in work:
            parts = elt.split('=', 1)
            if len(parts) == 1:
                if stripquotes:
                    elt=_stripquotes(elt)
                args.append(elt)

            else:
                key, val = parts
                val = val.strip()
                if stripquotes and val:
                    val=_stripquotes(val)

                key = key.strip()
                if not key: continue
                key = key.lower().encode('ascii')

                if not keywords or key in keywords:
                    if key in intargs:
                        try:
                            val = int(val)
                        except ValueError:
                            raise ValueError('Could not convert value "%s" to integer for keyword "%s"' % (val, key))
                    if key in boolargs:
                        val = val.lower()
                        val = val in (1, 't', 'true', 'yes', 'y', 'on')
                    kwargs[key] = val
    return args, kwargs


