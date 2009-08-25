from django import forms
from django.db.models.query import EmptyQuerySet 
from shipping.modules.tieredweight.models import Carrier, Zone


class CarrierAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CarrierAdminForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            tmp_qs = self.fields['default_zone'].queryset
            self.fields['default_zone'].queryset = tmp_qs.filter(carrier=kwargs['instance'])
        else:
            self.fields['default_zone'].queryset = EmptyQuerySet()

    class Meta:
        model = Carrier


class ZoneAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ZoneAdminForm, self).__init__(*args, **kwargs)
        zones = None
        if 'instance' in kwargs:
            carrier = kwargs['instance'].carrier.pk
            zones = Carrier.objects.get(pk=carrier).zones.exclude(pk=kwargs['instance'].pk)
        else:
            try:
                carrier = args[0]['carrier']
                if carrier:
                    zones = Carrier.objects.get(pk=carrier).zones.all()
            except IndexError:
                pass

        if zones:
            used_countries = []
            for zone in zones:
                for country in zone.countries.all():
                    used_countries.append(country.name)
            tmp_qs = self.fields['countries'].queryset
            self.fields['countries'].queryset = tmp_qs.exclude(name__in=used_countries)

    class Meta:
        model = Zone