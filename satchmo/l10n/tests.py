from django.test import TestCase
from satchmo.l10n.validators import aupostcode, capostcode, uspostcode

class AUPostCodeTest(TestCase):
    def test_valid(self):
        code = aupostcode.validate("2000")
        self.assertEqual('2000', code)
        code = aupostcode.validate(" 2000 ")
        self.assertEqual('2000', code)
    
    def test_invalid(self):
        try:
            code = capostcode.validate("")
            self.fail('Invalid blank postal code not caught')
        except:
            pass
        
        try:
            code = capostcode.validate("no")
            self.fail('Invalid postal code "no" not caught')
        except:
            pass
        
class CAPostCodeTest(TestCase):
    def test_valid(self):
        code = capostcode.validate("M5V2T6")
        self.assertEqual('M5V2T6', code)
        code = capostcode.validate("m5v2t6")
        self.assertEqual('M5V2T6', code)
    
    def test_invalid(self):
        try:
            code = capostcode.validate("")
            self.fail('Invalid blank postal code not caught')
        except:
            pass
        
        try:
            code = capostcode.validate("no")
            self.fail('Invalid postal code "no" not caught')
        except:
            pass
        
        try:
            code = capostcode.validate("M5V M5V")
            self.fail('Invalid postal code "M5V M5V" not caught')
        except:
            pass
        
        try:
            code = capostcode.validate("D5V 2T6")
            self.fail('Invalid postal code "D5V 2T6" not caught -- "D" is not a valid major geographic area or province.')
        except:
            pass

class USPostCodeTest(TestCase):
    def test_five_digit(self):
        zipcode = uspostcode.validate("66044")
        self.assertEqual('66044', zipcode)
        try:
            zipcode = uspostcode.validate(" 66044 ")
            self.fail("Invalid postal code not caught")
        except:
            pass

    def test_nine_digit(self):
        zipcode = uspostcode.validate("94043-1351")
        self.assertEqual('94043-1351', zipcode)
        try:
            zipcode = uspostcode.validate(" 94043-1351 ")
            self.fail('Invalide postal code not caught')
        except:
            pass
    
    def test_invalid(self):
        try:
            code = uspostcode.validate("")
            self.fail('Invalid blank postal code not caught')
        except:
            pass
        
        try:
            zipcode = uspostcode.validate("no")
            self.fail('Invalid ZIP code "no" not caught')
        except:
            pass
