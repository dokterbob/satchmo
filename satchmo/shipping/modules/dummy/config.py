# from satchmo.configuration import *
# 
# SHIP_MODULES = config_get('SHIPPING', 'MODULES')
# SHIP_MODULES.add_choice(('satchmo.shipping.modules.dummy', 'Dummy Shipping'))
# SHIPPING_GROUP = config_get_group('SHIPPING')
# 
# config_register_list(
# DecimalValue(SHIPPING_GROUP,
#     'FLAT_RATE',
#     description=_("Flat shipping"),
#     requires=SHIPPING_ACTIVE,
#     requiresvalue='satchmo.shipping.modules.flat',
#     default="4.00"),
# )
