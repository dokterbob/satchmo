from django import template

register = template.Library()

def template_range(value):
    """Return a range 1..value"""
    return range(1, value + 1)
    
register.filter('template_range', template_range)

def force_space(value, chars=40):
    """Forces spaces every `chars` in value"""

    chars = int(chars)
    if len(value) < chars:
        return value
    else:    
        out = []
        start = 0
        end = 0
        looping = True
        
        while looping:
            start = end
            end += chars
            out.append(value[start:end])
            looping = end < len(value)
    
    return ' '.join(out)

def break_at(value,  chars=40):
    """Force spaces into long lines which don't have spaces"""
    
    chars = int(chars)
    if len(value) < chars:
        return value
    else:
        out = []
        line = value.split(' ')
        for word in line:
            if len(word) > chars:
                out.append(force_space(word, chars))
            else:
                out.append(word)
                
    return " ".join(out)

    
register.filter('break_at', break_at)