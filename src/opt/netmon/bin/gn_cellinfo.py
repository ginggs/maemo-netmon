# -*- coding: utf-8 -*-
import dbus

service_types = { \
	'GPRS':  0x01,\
	'CS':	 0x02,\
	'EGPRS': 0x04,\
	'HSDPA': 0x08,\
	'HSUPA': 0x10
}

network_types = { \
	'HOME':      0,\
	'PREFERRED': 1,\
	'FORBIDDEN': 2,\
	'OTHER':     3,\
	'NOT_AVAIL':  4 \
}

net_registration_status = { \
	'HOME':                 0x00,\
	'ROAM':                 0x01,\
	'ROAM_BLINK':           0x02,\
	'NOSERV':               0x03,\
	'NOSERV_SEARCHING':     0x04,\
	'NOSERV_NOTSEARCHING':  0x05,\
	'NOSERV_NOSIM':         0x06,\
	'POWER_OFF':            0x08,\
	'NSPS':                 0x09,\
	'NSPS_NO_COVERAGE':     0x0A,\
	'SIM_REJECTED':         0x0B \
}

def CellInterfaceConnect():
	bus = dbus.SystemBus()
	dbus_object = bus.get_object('com.nokia.phone.net', '/com/nokia/phone/net')
	dbus_interface = dbus.Interface(dbus_object, 'Phone.Net')
	return dbus_interface

def SignalStrength():
	dbus_interface = CellInterfaceConnect()
	dbus_return = dbus_interface.get_signal_strength()
	return dbus_return

def RegStatus():
	dbus_interface = CellInterfaceConnect()
	dbus_return = dbus_interface.get_registration_status()

	return dbus_return
