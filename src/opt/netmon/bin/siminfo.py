# -*- coding: utf-8 -*-
# NetMon SIM Info Module
# Copyright 2010 by P. Kozak <maemo@golwen.net>
# http://netmon.golwen.net/
# This software is provided under an open source license - use at your own risk.

import dbus

class SimInfo():

	def __init__(self):
		bus = dbus.SystemBus()
		dbus_object = bus.get_object('com.nokia.phone.SIM', '/com/nokia/phone/SIM')
		self.siminfo = dbus.Interface(dbus_object, 'Phone.Sim')

	def provider_name(self):
		return self.siminfo.get_service_provider_name()
		