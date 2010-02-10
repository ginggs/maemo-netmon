# -*- coding: utf-8 -*-
import dbus

def BatteryInterfaceConnect():
	bus = dbus.SystemBus()
	hal_object = bus.get_object ('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
	hal_interface = dbus.Interface (hal_object, 'org.freedesktop.Hal.Manager')
	hal_devices = hal_interface.FindDeviceByCapability('battery')
	hal_device = hal_devices[0]
	hal_object = bus.get_object ('org.freedesktop.Hal', hal_device)
	return hal_object


def BatteryLevelState():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.charge_level.capacity_state')

	return hal_return

def BatteryLevelCurrent():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.charge_level.current')

	return hal_return

def BatteryLevelDesign():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.charge_level.design')

	return hal_return

def BatteryLevelFull():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.charge_level.last_full')

	return hal_return

def BatteryLevelUnit():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.charge_level.unit')

	return hal_return

def BatteryPercent():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.charge_level.percentage')

	return hal_return

def BatteryPresent():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.present')

	return hal_return

def BatteryRechargeable():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.is_rechargeable')

	return hal_return

def BatteryCharging():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.rechargeable.is_charging')

	return hal_return

def BatteryDischarging():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.rechargeable.is_discharging')

	return hal_return


def BatteryReportingDesign():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.reporting.design')

	return hal_return

def BatteryReportingCurrent():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.reporting.current')

	return hal_return

def BatteryReportingFull():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.reporting.last_full')

	return hal_return

def BatteryReportingUnit():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.reporting.unit')

	return hal_return

def BatteryVoltageDesign():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.voltage.design')

	return hal_return

def BatteryVoltageCurrent():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.voltage.current')

	return hal_return

def BatteryVoltageUnit():
	hal_object = BatteryInterfaceConnect()
	hal_return = hal_object.GetProperty('battery.voltage.unit')

	return hal_return
	