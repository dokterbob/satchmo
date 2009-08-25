from decimal import Decimal    
from django.test import TestCase
from satchmo_utils.numbers import round_decimal, RoundedDecimalError, trunc_decimal

class TestRoundedDecimals(TestCase):
    
    def testRoundingDecimals(self):
        """Test Partial Unit Rounding Decimal Conversion behavior"""
        val = round_decimal(val=3.40, places=5, roundfactor=.5, normalize=True)
        self.assertEqual(val, Decimal("3.5"))
        
        val = round_decimal(val=3.40, places=5, roundfactor=-.5, normalize=True)
        self.assertEqual(val, Decimal("3"))
        
        val = round_decimal(val=0, places=5, roundfactor=-.5, normalize=False)
        self.assertEqual(val, Decimal("0.00000"))
        
        val = round_decimal(0, 5, -.5, False)
        self.assertEqual(val, Decimal("0.00000"))
        
        val = round_decimal(0)
        self.assertEqual(val, Decimal("0"))
        
        val = round_decimal(3.23,4,-.25)
        self.assertEqual(val, Decimal("3"))
        
        val = round_decimal(-3.23,4,-.25)
        self.assertEqual(val, Decimal("-3"))
        val = round_decimal(-3.23,4,.25)
        self.assertEqual(val, Decimal("-3.25"))
        
        val = round_decimal(3.23,4,.25)
        self.assertEqual(val, Decimal("3.25"))
        
        val = round_decimal(3.23,4,.25,False)
        self.assertEqual(val, Decimal("3.2500"))
        
        val = round_decimal(3.23,1,.25,False)
        self.assertEqual(val, Decimal("3.2"))
        
        val = round_decimal(2E+1, places=2)
        self.assertEqual(val, Decimal('20.00'))

    def testTruncDecimal(self):
        """Test trunc_decimal's rounding behavior."""
        # val = trunc_decimal("0.004", 2)
        # self.assertEqual(val, Decimal("0.00"))
        val = trunc_decimal("0.005", 2)
        self.assertEqual(val, Decimal("0.01"))
        val = trunc_decimal("0.009", 2)
        self.assertEqual(val, Decimal("0.01"))

        val = trunc_decimal("2E+1", places=2)
        self.assertEqual(val, Decimal('20.00'))
        
        val = trunc_decimal(2.1E+1, places=2)
        self.assertEqual(val, Decimal('21.00'))

        val = trunc_decimal(2.1223E+1, places=2)
        self.assertEqual(val, Decimal('21.23'))

        val = trunc_decimal("2.1223E+1", places=2)
        self.assertEqual(val, Decimal('21.23'))
