# -*- coding: utf-8 -*-
# NetMon Cell Info Module
# Copyright 2010 by P. Kozak <maemo@golwen.net>
# http://netmon.golwen.net/
# This software is provided under an open source license - use at your own risk.

import dbus

class CellInfo():

	service_types = { \
		'GPRS':  		0x01,
		'CS':	 		0x02,
		'EGPRS': 		0x04,
		'HSDPA':		0x08,
		'HSUPA': 		0x10
	}

	network_types = { \
		'HOME':      		0,
		'PREFERRED': 		1,
		'FORBIDDEN': 		2,
		'OTHER':     		3,
		'NOT_AVAIL': 		4 
	}

	net_registration_status = { \
		'HOME':                 0x00,
		'ROAM':                 0x01,
		'ROAM_BLINK':           0x02,
		'NOSERV':               0x03,
		'NOSERV_SEARCHING':     0x04,
		'NOSERV_NOTSEARCHING':  0x05,
		'NOSERV_NOSIM':         0x06,
		'POWER_OFF':            0x08,
		'NSPS':                 0x09,
		'NSPS_NO_COVERAGE':     0x0A,
		'SIM_REJECTED':         0x0B 
	}

	selected_technology = { \
		'DUAL':    		0, 
		'GSM':    		1, 
		'3G':      		2, 
		'NUM':     		3  
	}

	def __init__(self):
		bus = dbus.SystemBus()
		dbus_object = bus.get_object('com.nokia.phone.net', '/com/nokia/phone/net')
		self.cellinfo = dbus.Interface(dbus_object, 'Phone.Net')

	def signal_strength(self):
		return self.cellinfo.get_signal_strength()

	def registration_status(self):
		return self.cellinfo.get_registration_status()

	def selected_radio_rechnology(self):
		return self.cellinfo.get_selected_radio_access_technology()

	def radio_technology(self):
		return self.cellinfo.get_radio_access_technology()
		