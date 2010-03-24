import django.dispatch

#: Sent after a value from the configuration application has been changed.
#:
#: :param sender: The value that was changed
#: :type sender: ``livesettings.values.Value``
#:
#: :param old_value: The old value of the setting
#: :param new_value: The new value of the settings
#:
#: :param setting: The value that was changed
#: :type setting: ``livesettings.values.Value``
#:
#: .. Note:: *setting* is the same as *sender*.
configuration_value_changed = django.dispatch.Signal()
