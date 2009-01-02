from django import forms
from satchmo_store.contact import signals
import logging

log = logging.getLogger('contact.listeners')

def au_postcode_validator(sender, postcode=None, country=None, **kwargs):
    if country.iso2_code == 'AU':
        from l10n.validators import aupostcode
        try:
            pc = aupostcode.validate(postcode)
            return pc
        except ValueError, ve:
            raise forms.ValidationError('Please enter a valid Australian postal code.')
signals.validate_postcode.connect(au_postcode_validator)


def ca_postcode_validator(sender, postcode=None, country=None, **kwargs):
    if country.iso2_code == 'CA':
        from l10n.validators import capostcode
        try:
            pc = capostcode.validate(postcode)
            return pc
        except ValueError, ve:
            raise forms.ValidationError('Please enter a valid Canadian postal code.')
signals.validate_postcode.connect(ca_postcode_validator)

def uk_postcode_validator(sender, postcode=None, country=None, **kwargs):
    """Validates UK postcodes"""
    if country.iso2_code == 'GB':
        from l10n.validators import ukpostcode
        try:
            pc = ukpostcode.parse_uk_postcode(postcode)
        except ValueError, ve:
            log.debug('UK Postcode validator caught error: %s', ve)
            raise forms.ValidationError('Please enter a valid UK postcode.')
        return ' '.join(pc)

signals.validate_postcode.connect(uk_postcode_validator)

def us_postcode_validator(sender, postcode=None, country=None, **kwargs):
    if country.iso2_code == 'US':
        from l10n.validators import uspostcode
        try:
            pc = uspostcode.validate(postcode)
            return pc
        except ValueError, ve:
            raise forms.ValidationError('Please enter a valid US ZIP code.')
signals.validate_postcode.connect(us_postcode_validator)
