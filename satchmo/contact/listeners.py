from django import forms
from satchmo.contact import signals
import logging

log = logging.getLogger('contact.listeners')

def ca_postcode_validator(sender, postcode=None, country=None, **kwargs):
    if country.iso2_code == 'CA':
        log.debug('Validating Canadian postal code')
        from satchmo.l10n.validators import capostcode
        try:
            pc = capostcode.validate(postcode)
            return pc
        except ValueError, ve:
            raise forms.ValidationError('Please enter a valid Canadian postal code.')
signals.validate_postcode.connect(ca_postcode_validator)

def uk_postcode_validator(sender, postcode=None, country=None, **kwargs):
    """Validates UK postcodes"""
    if country.iso2_code == 'GB':
        log.debug('Validating UK Postcode: %s', postcode)
        from satchmo.l10n.validators import ukpostcode
        try:
            pc = ukpostcode.parse_uk_postcode(postcode)
        except ValueError, ve:
            log.debug('UK Postcode validator caught error: %s', ve)
            raise forms.ValidationError('Please enter a valid UK postcode.')
        return ' '.join(pc)

signals.validate_postcode.connect(uk_postcode_validator)

def us_postcode_validator(sender, postcode=None, country=None, **kwargs):
    if country.iso2_code == 'US':
        log.debug('Validating US ZIP code')
        from satchmo.l10n.validators import uspostcode
        try:
            pc = uspostcode.validate(postcode)
            return pc
        except ValueError, ve:
            raise forms.ValidationError('Please enter a valid US ZIP code.')
signals.validate_postcode.connect(us_postcode_validator)
