# -*- coding: utf-8 -*-
# NetMon Battery Info Module
# Copyright 2010 by P. Kozak <maemo@golwen.net>
# http://netmon.golwen.net/
# This software is provided under an open source license - use at your own risk.

import dbus

class Battery():

	def __init__(self):
		bus = dbus.SystemBus()
		hal_object = bus.get_object ('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
		hal_interface = dbus.Interface (hal_object, 'org.freedesktop.Hal.Manager')
		hal_devices = hal_interface.FindDeviceByCapability('battery')
		hal_device = hal_devices[0]
		self.battery = bus.get_object ('org.freedesktop.Hal', hal_device)

	def level_state(self):
		return self.battery.GetProperty('battery.charge_level.capacity_state')

	def level_current(self):
		return self.battery.GetProperty('battery.charge_level.current')

	def level_design(self):
		return self.battery.GetProperty('battery.charge_level.design')

	def level_full(self):
		return self.battery.GetProperty('battery.charge_level.last_full')

	def level_unit(self):
		return self.battery.GetProperty('battery.charge_level.unit')

	def percent(self):
		return self.battery.GetProperty('battery.charge_level.percentage')

	def present(self):
		return self.battery.GetProperty('battery.present')

	def rechargeable(self):
		return self.battery.GetProperty('battery.is_rechargeable')

	def charging(self):
		return self.battery.GetProperty('battery.rechargeable.is_charging')

	def discharging(self):
		return self.battery.GetProperty('battery.rechargeable.is_discharging')

	def reporting_design(self):
		return self.battery.GetProperty('battery.reporting.design')

	def reporting_current(self):
		return self.battery.GetProperty('battery.reporting.current')

	def reporting_full(self):
		return self.battery.GetProperty('battery.reporting.last_full')

	def reporting_unit(self):
		return self.battery.GetProperty('battery.reporting.unit')

	def voltage_design(self):
		return self.battery.GetProperty('battery.voltage.design')

	def voltage_current(self):
		return self.battery.GetProperty('battery.voltage.current')

	def voltage_unit(self):
		return self.battery.GetProperty('battery.voltage.unit')
