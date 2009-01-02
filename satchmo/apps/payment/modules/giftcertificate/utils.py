import random
from livesettings import config_value

def generate_certificate_code():
    """Creates a code, formatted according to the shop owner's preference as set in the config system."""
    charset = config_value('PAYMENT_GIFTCERTIFICATE', 'CHARSET')
    format = config_value('PAYMENT_GIFTCERTIFICATE', 'FORMAT')
    return generate_code(charset, format)

def generate_code(charset, format):
    """Creates the actual code.  Split out for ease of testing."""
    
    out = []
    for c in format.strip():
        if c=="^":
            out.extend(random.sample(charset, 1))
        else:
            out.append(c)
    
    return "".join(out)