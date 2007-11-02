r"""
>>> import datetime
>>> from satchmo.discount.models import *

# Create a basic discount
>>> start = datetime.date(2006, 10, 1)
>>> end = datetime.date(5000, 10, 1)
>>> disc1 = Discount.objects.create(description="New Sale", code="BUYME", amount="5.00", allowedUses=10,
... numUses=0, minOrder=5, active=True, startDate=start, endDate=end, freeShipping=False)
>>> disc1.isValid()
(True, u'Valid.')

#Change start date to the future
>>> start = datetime.date(5000, 1, 1)
>>> disc1.startDate = start
>>> disc1.save()
>>> disc1.isValid()
(False, u'This coupon is not active yet.')

#Change end date to the past
>>> start = datetime.date(2000, 1, 1)
>>> end = datetime.date(2006, 1, 1)
>>> disc1.startDate = start
>>> disc1.endDate = end
>>> disc1.save()
>>> disc1.isValid()
(False, u'This coupon has expired.')

#Make it invalid
>>> disc1.startDate = datetime.date(2006, 12, 1)
>>> disc1.endDate = datetime.date(5000, 12, 1)
>>> disc1.active = False
>>> disc1.save()
>>> disc1.isValid()
(False, u'This coupon is disabled.')
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
