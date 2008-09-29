from django import forms
from satchmo.contact import signals
import logging

log = logging.getLogger('contact.listeners')

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
