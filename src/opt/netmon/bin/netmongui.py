# -*- coding: utf-8 -*-
# NetMon GUI
# Copyright 2010 by P. Kozak <maemo@golwen.net>
# http://netmon.golwen.net/
# This software is provided under an open source license - use at your own risk.

import gtk
import dbus
import hildon
import dbus.mainloop.glib
import gobject
from threading import Thread
from time import sleep, time
from cellinfo import CellInfo
from battery import Battery
from siminfo import SimInfo
from sys import exit
from osso import Context, DeviceState

class StatusUpdates(Thread):
	global window
	
	def __init__(self):
		Thread.__init__(self)
		self.runthread = True
		self.cell = None
		self.battery = None
		
	def status_object_cell(self, cellstatus):
		self.cell = cellstatus

	def status_object_battery(self, batterystatus):
		self.battery = batterystatus

	def set_signal_strength(self, percent, decibel):
		self.cell['cellinfo']['signal']['value'].set_text('%d %%' % percent)
		fraction = 1.0 / 100 * percent
		text = " - %d dBm" % decibel
		self.cell['signalbar'].set_fraction(fraction)
		self.cell['signalbar'].set_text(text)

	def set_mnc(self, value):
		self.cell['cellinfo']['mnc']['value'].set_text('%d' % value)

	def set_mcc(self, value):
		self.cell['cellinfo']['mcc']['value'].set_text('%d' % value)

	def set_cell(self, value):
		cell_id = value & 65535
		cell_rnc = value >> 16
	
		self.cell['cellinfo']['cell']['value'].set_text('%d' % cell_id)
		self.cell['cellinfo']['rnc']['value'].set_text('%d' % cell_rnc)

	def set_lac(self, value):
		self.cell['cellinfo']['lac']['value'].set_text('%d' % value)

	def set_services(self, value):
		services = ''
		if (value & 0x02): services += 'CS '
		if (value & 0x01): services += 'GPRS '
		if (value & 0x04): services += 'EGPRS '
		if (value & 0x08): services += 'HSDPA '
		if (value & 0x10): services += 'HSUPA'

		self.cell['cellinfo']['services']['value'].set_text(services)

	def set_neterror(self, value):
		self.cell['cellinfo']['error']['value'].set_text('%d' % value)

	def set_nettype(self, value):
		if (value == 0): network_type = 'home'
		elif (value == 1): network_type = 'preferred'
		elif (value == 2): network_type = 'forbidden'
		elif (value == 2): network_type = 'other'
		else: value = 'no network'

		self.cell['cellinfo']['type']['value'].set_text(network_type)

	def set_netstatus(self, value):
		if (value == 0): status = 'home'
		elif (value == 1): status = 'roam'
		elif (value == 2): status = 'roam_blink'
		elif (value == 3): status = 'no serv.'
		elif (value == 4): status = 'no serv. search'
		elif (value == 5): status = 'no serv. no search'
		elif (value == 6): status = 'no sim'
		elif (value == 8): status = 'power off'
		elif (value == 9): status = 'NSPS'             # no service power save
		elif (value == 10): status = 'NSPS no cover.'
		elif (value == 11): status = 'sim rejected'
		else: status = 'unknown'

		self.cell['cellinfo']['status']['value'].set_text(status)

	def set_selectedradio(self, value):
		if (value == 0): technology = "DUAL"
		elif (value == 1): technology = "GSM"
		elif (value == 2): technology = "3G"
		else: technology = "?"

		self.cell['cellinfo']['selected']['value'].set_text(technology)

	def set_usedradio(self, value):
		if (value == 1): technology = "GSM"
		elif (value == 2): technology = "3G"
		else: technology = "?"	

		self.cell['cellinfo']['technology']['value'].set_text(technology)

	def set_operator(self, value):
		self.cell['cellinfo']['operator']['value'].set_text(value)

	def set_batt_presence(self, present, rechargeable):
		if (present == 0):
			presece = "not present"
		else:
			presence = "present"

		if (rechargeable == 0):
			rechargeable = "not rechargeable"
		else:
			rechargeable = "rechargeable"
	
		self.battery['presence']['value1'].set_text(presence)
		self.battery['presence']['value2'].set_text(rechargeable)

	def set_batt_charging(self, state, charging, discharging):
		self.battery['charging']['value1'].set_text(state)

		if (charging and discharging):
			charging_state = "charging+discharging"
		elif (charging):
			charging_state = "charging"
		elif (discharging):
			charging_state = "discharging"
		else:
			charging_state = "unknown"

		self.battery['charging']['value2'].set_text(charging_state)

	def set_batt_capacity(self, current, design, percent, unit, charging = False):

		self.battery['capacity']['value2'].set_text('%d %s' % (design, unit))

		if (charging):
			self.battery['capacity']['value1'].set_text('(%d %s)' % (current, unit))
			self.battery['capacity']['bar'].pulse()
			self.battery['capacity']['bar'].set_pulse_step(0.1)
			self.battery['capacity']['bar'].set_text("charging...")
		else:
			self.battery['capacity']['value1'].set_text('%d %s' % (current, unit))
			fraction = 1.0 / 100 * percent
			text = '%d %%' % percent
			self.battery['capacity']['bar'].set_fraction(fraction)
			self.battery['capacity']['bar'].set_text(text)
		

	def set_batt_voltage(self, current, design, unit):
		self.battery['voltage']['value1'].set_text('%d %s' % (current, unit))
		self.battery['voltage']['value2'].set_text('%d %s' % (design, unit))

		self.battery['voltage']['bar'].set_fraction(1.0 / design * current)
		text = " %d %%" % (100.0 / design * current)
		self.battery['voltage']['bar'].set_text(text)
		
	def set_batt_last(self, full, design, level, unit, levelunit):
		self.battery['last']['value1'].set_text('%d %s' % (full, unit))
		self.battery['last']['value2'].set_text('%d %s' % (level, levelunit))

		self.battery['last']['bar'].set_fraction(1.0 / design * full)
		text = " %d %%" % (100.0 / design * full)
		self.battery['last']['bar'].set_text(text)

	def run(self):
		cellinfo = CellInfo()
		battery = Battery()
		self.last = 0
		while self.runthread:
			read_data = 1
			now = int(time())

			if (window != None):
				if (window.get_stack() != None):
					title = window.get_title()
					if (title == 'NetMon Battery Status'):
						read_data = 2
						refresh = 2
					elif (title == 'NetMon About'):
						read_data = 0
						refresh = 30
					elif (title == 'NetMon Networks'):
						read_data = 0
						refresh = 30
				else:
					refresh = 30
			else:
				refresh = 30

			if ((self.last > 0) and (now < (self.last + refresh))):
				sleep(0.5)
				continue

			self.last = now

			if (read_data == 1):
				percent, decibel, nil = cellinfo.signal_strength()
				status, lac, cellid, mnc, mcc, nettype, netservices, neterror = cellinfo.registration_status()
				selectedradio, nil = cellinfo.selected_radio_rechnology()
				usedradio, nil = cellinfo.radio_technology()
				gtk.gdk.threads_enter()
				self.set_mnc(mnc)
				self.set_mcc(mcc)
				self.set_cell(cellid)
				self.set_lac(lac)
				self.set_services(netservices)
				self.set_neterror(neterror)
				self.set_nettype(nettype)
				self.set_netstatus(status)
				self.set_selectedradio(selectedradio)
				self.set_usedradio(usedradio)
				self.set_signal_strength(percent, decibel)
				gtk.gdk.threads_leave()

			elif (read_data == 2):
				gtk.gdk.threads_enter()
				charging = battery.charging()
				self.set_batt_presence(battery.present(), battery.rechargeable())
				self.set_batt_charging(battery.level_state(),
						charging,
						battery.discharging())
				self.set_batt_capacity(battery.reporting_current(),
						battery.reporting_design(),
						battery.percent(),
						battery.reporting_unit(),
						charging)
				self.set_batt_voltage(battery.voltage_current(),
						battery.voltage_design(),
						battery.voltage_unit())
				self.set_batt_last(battery.reporting_full(),
						battery.reporting_design(),
						battery.level_full(),
						battery.voltage_unit(),
						battery.level_unit())
				gtk.gdk.threads_leave()

			sleep(0.5)

		return 0

	def stop(self):
		self.runthread = False
		

def signal_registration_status_change(*regstatus):
	pass

def signal_signal_strength_change(*values):
	global status_updates

	#print "signal_signal_strength_change"
	#print values
	status_updates.set_signal_strength(values[0], values[1])

def signal_network_time_info_change(*values):
	#print "signal_network_time_info_change"
	#print values
	pass

def signal_cellular_system_state_change(*values):
	#print "signal_cellular_system_state_change"
	#print values
	status_updates.last = 0

def signal_radio_access_technology_change(*values):
	#print "signal_radio_access_technology_change"
	#print values
	status_updates.last = 0

def signal_radio_info_change(*values):
	#print "signal_radio_info_change"
	#print values
	status_updates.last = 0

def signal_cell_info_change(*values):
	#print "signal_cell_info_change"
	#print values

	status_updates.last = 0
	#status_updates.set_usedradio(values[0])
	#status_updates.set_cell(values[1])
	#status_updates.set_lac(values[2])
	#status_updates.set_mnc(values[3])
	#status_updates.set_mcc(values[4])
	
def signal_operator_name_change(*values):
	#print "signal_operator_name_change"
	#print values
	status_updates.set_operator(values[1])

def available_networks_set(*values):
		global networks
		global window

		store_networks = networks['gtklist']

		del store_networks[0]
		for network in range(0, len(values[1])):
			new_iter = store_networks.append()
			store_networks.set(new_iter, 0, str(network+1), 1, values[2][network], 2, str(int(values[1][network])), 3, values[3][network])
		hildon.hildon_gtk_window_set_progress_indicator(window, 0)
		networks['acquire'] = False
		
def available_networks_err(*values):
		print values

def battery_window(nope):
	global window
	global status_updates
	
	window = hildon.StackableWindow()
	window.set_title("NetMon Battery Status")

	battery = dict()
	battery['presence'] 	= { 'text': 'Battery Presence'}
	battery['charging'] 	= { 'text': 'Charging Status'}
	battery['capacity'] 	= { 'text': 'Capacity'}
	battery['voltage'] 	= { 'text': 'Voltage'}
	battery['last'] 	= { 'text': 'Last Full'}

	for entry in battery:
		battery[entry]['label'] = gtk.Label(battery[entry]['text'])
		battery[entry]['label'].set_alignment(0, 0.5)
		battery[entry]['value1'] = gtk.Label('?')
		battery[entry]['value1'].set_alignment(1, 0.5)
		battery[entry]['value2'] = gtk.Label('?')
		battery[entry]['value2'].set_alignment(1, 0.5)

	battery['capacity']['bar'] = gtk.ProgressBar(adjustment=None)
	battery['capacity']['bar'].set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
	battery['capacity']['bar'].set_text("acquiring battery info...")

	battery['voltage']['bar'] = gtk.ProgressBar(adjustment=None)
	battery['voltage']['bar'].set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
	battery['voltage']['bar'].set_text("acquiring battery info...")

	battery['last']['bar'] = gtk.ProgressBar(adjustment=None)
	battery['last']['bar'].set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
	battery['last']['bar'].set_text("acquiring battery info...")
	
	table = gtk.Table(12,20,True)

	table.attach(battery['presence']['label'], 1, 7, 1, 2)
	table.attach(battery['presence']['value1'], 7, 12, 1, 2)
	table.attach(battery['presence']['value2'], 12, 19, 1, 2)

	table.attach(battery['charging']['label'], 1, 7, 2, 3)
	table.attach(battery['charging']['value1'], 7, 12, 2, 3)
	table.attach(battery['charging']['value2'], 12, 19, 2, 3)

	table.attach(battery['capacity']['label'], 1, 7, 3, 4)
	table.attach(battery['capacity']['value1'], 7, 12, 3, 4)
	table.attach(battery['capacity']['value2'], 12, 19, 3, 4)
	table.attach(battery['capacity']['bar'], 1, 19, 4, 6)
	
	table.attach(battery['voltage']['label'], 1, 7, 6, 7)
	table.attach(battery['voltage']['value1'], 7, 12, 6, 7)
	table.attach(battery['voltage']['value2'], 12, 19, 6, 7)
	table.attach(battery['voltage']['bar'], 1, 19, 7, 9)

	table.attach(battery['last']['label'], 1, 7, 9, 10)
	table.attach(battery['last']['value1'], 7, 12, 9, 10)
	table.attach(battery['last']['value2'], 12, 19, 9, 10)
	table.attach(battery['last']['bar'], 1, 19, 10, 12)

	status_updates.status_object_battery(battery)
	window.add(table)
	window.show_all()

def networks_window(myobject):
	global window
	global networks
	
	if (not networks or not networks['acquire']):
		cellinfo = CellInfo()
		cellinfo.available_network(available_networks_set, available_networks_err)
		status, lac, cellid, mnc, mcc, nettype, netservices, neterror = cellinfo.registration_status()

		siminfo = SimInfo()
		provider_name, nil, nil, nil = siminfo.provider_name()

		store_networks = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		store_networks.set(store_networks.append(), 0, '1', 1, mcc, 2, mnc, 3, provider_name)
		if (not networks):
			networks = {}
		networks['gtklist'] = store_networks
		networks['acquire'] = True

	else:
		store_networks = networks['gtklist']

	window = hildon.StackableWindow()
	window.set_title("NetMon Networks")
	hildon.hildon_gtk_window_set_progress_indicator(window, 1)

	selector = hildon.TouchSelector()
	renderer = gtk.CellRendererText()

	column = selector.append_column(store_networks, renderer)
	column.set_attributes(renderer, text=0)

	renderer = gtk.CellRendererText()
	renderer.set_property('xalign', 0)

	column.pack_start(renderer, 1)
	column.set_attributes(renderer, text=1)

	renderer = gtk.CellRendererText()
	renderer.set_property('xalign', 0)

	column.pack_start(renderer, 2)
	column.set_attributes(renderer, text=2)

	renderer = gtk.CellRendererText()
	renderer.set_property('xalign', 0)

	column.pack_start(renderer, 3)
	column.set_attributes(renderer, text=3)

	selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
	column.set_property("text-column", 0)

	label1 = gtk.Label("Index")
	label2 = gtk.Label("MCC")
	label3 = gtk.Label("MNC")
	label4 = gtk.Label("Operator")
	label1.set_alignment(0, 0)
	label2.set_alignment(0, 0)
	label3.set_alignment(0, 0)
	label4.set_alignment(0, 0)
	table = gtk.Table(1,4,True)
	table.attach(label1, 0, 1, 0, 1)
	table.attach(label2, 1, 2, 0, 1)
	table.attach(label3, 2, 3, 0, 1)
	table.attach(label4, 3, 4, 0, 1)
	vbox = gtk.VBox(False, 0)
	vbox.pack_start(table, False, False, 0)
	vbox.pack_end(selector, True, True, 0)
	window.add(vbox)
	
	window.show_all()
	
	
def about_window(myobject):
	global window
	version = "0.8"

	window = hildon.StackableWindow()
	window.set_title("NetMon About")

	text = 'NetMon Cellular Network Monitor\nVersion %s\n(c) Copyright by Peter \'spag\' Kozak  (maemo@golwen.net) 2010\nUse at your own risk!' % version
	label = gtk.Label(text)
	window.add(label)
	window.show_all()

def main_menu():
	menu = hildon.AppMenu()

	button1 = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
	button1.set_label("Battery")
	button1.connect("clicked", battery_window)
	menu.append(button1)

	button2 = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
	button2.set_label("Networks")
	button2.connect("clicked", networks_window)
	menu.append(button2)

	button3 = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
	button3.set_label("About")
	button3.connect("clicked", about_window)
	menu.append(button3)
	menu.show_all()

	return menu

def main_quit(obj, status_updates, loop):
	status_updates.stop()
	sleep(1)
	loop.quit()

def displaystate_change( value ):
	global status_updates
	
	if (value == "off"):
		status_updates.stop()
		remove_signals()

	elif (value == "on"):
		preserve_cell = status_updates.cell
		preserve_battery = status_updates.battery
		del(status_updates)
		status_updates = StatusUpdates()
		status_updates.status_object_cell(preserve_cell)
		status_updates.status_object_battery(preserve_battery)
		status_updates.start()
		add_signals()

def add_signals():
	global bus
	
	bus.add_signal_receiver(signal_registration_status_change, dbus_interface = "Phone.Net", signal_name = "registration_status_change")
	bus.add_signal_receiver(signal_signal_strength_change, dbus_interface = "Phone.Net", signal_name = "signal_strength_change")
	bus.add_signal_receiver(signal_network_time_info_change, dbus_interface = "Phone.Net", signal_name = "network_time_info_change")
	bus.add_signal_receiver(signal_cellular_system_state_change, dbus_interface = "Phone.Net", signal_name = "cellular_system_state_change")
	bus.add_signal_receiver(signal_radio_access_technology_change, dbus_interface = "Phone.Net", signal_name = "radio_access_technology_change")
	bus.add_signal_receiver(signal_radio_info_change, dbus_interface = "Phone.Net", signal_name = "radio_info_change")
	bus.add_signal_receiver(signal_cell_info_change, dbus_interface = "Phone.Net", signal_name = "cell_info_change")
	bus.add_signal_receiver(signal_operator_name_change, dbus_interface = "Phone.Net", signal_name = "operator_name_change")


def remove_signals():
	global bus

	bus.remove_signal_receiver(signal_registration_status_change, dbus_interface = "Phone.Net", signal_name = "registration_status_change")
	bus.remove_signal_receiver(signal_signal_strength_change, dbus_interface = "Phone.Net", signal_name = "signal_strength_change")
	bus.remove_signal_receiver(signal_network_time_info_change, dbus_interface = "Phone.Net", signal_name = "network_time_info_change")
	bus.remove_signal_receiver(signal_cellular_system_state_change, dbus_interface = "Phone.Net", signal_name = "cellular_system_state_change")
	bus.remove_signal_receiver(signal_radio_access_technology_change, dbus_interface = "Phone.Net", signal_name = "radio_access_technology_change")
	bus.remove_signal_receiver(signal_radio_info_change, dbus_interface = "Phone.Net", signal_name = "radio_info_change")
	bus.remove_signal_receiver(signal_cell_info_change, dbus_interface = "Phone.Net", signal_name = "cell_info_change")
	bus.remove_signal_receiver(signal_operator_name_change, dbus_interface = "Phone.Net", signal_name = "operator_name_change")

def main():
	global status_updates
	global window
	global bus
	global networks
	
	gtk.gdk.threads_init()
	window = None
	cell = dict()
	networks = None

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()
	add_signals()

	busobj = bus.get_object('com.nokia.mce', '/com/nokia/mce/signal')
	busiface = dbus.Interface(busobj, 'com.nokia.mce.signal')
	busiface.connect_to_signal('display_status_ind', displaystate_change)

	loop = gobject.MainLoop()
	prog = hildon.Program.get_instance()

	win = hildon.StackableWindow()
	win.set_title("NetMon Cell Info")

	cell['signalbar'] = gtk.ProgressBar(adjustment=None)
	cell['signalbar'].set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
	cell['signalbar'].set_text("acquiring signal strength...")
	cell['cellinfo'] = dict()
	cell['cellinfo']['signal'] 	= { 'text': 'Signal'}
	cell['cellinfo']['mcc'] 	= { 'text': 'Mobile Country Code'}
	cell['cellinfo']['mnc'] 	= { 'text': 'Mobile Network Code'}
	cell['cellinfo']['lac'] 	= { 'text': 'Location Area Code'}
	cell['cellinfo']['cell'] 	= { 'text': 'Cell ID'}
	cell['cellinfo']['rnc'] 	= { 'text': 'RNC ID'}
	cell['cellinfo']['status'] 	= { 'text': 'Status'}
	cell['cellinfo']['technology'] 	= { 'text': 'Technology'}
	cell['cellinfo']['type'] 	= { 'text': 'Network Type'}
	cell['cellinfo']['selected'] 	= { 'text': 'Selected'}
	cell['cellinfo']['error'] 	= { 'text': 'Network Error'}
	cell['cellinfo']['services'] 	= { 'text': 'Supported Services'}
	cell['cellinfo']['operator'] 	= { 'text': 'Operator'}

	for entry in cell['cellinfo']:
		cell['cellinfo'][entry]['label'] = gtk.Label(cell['cellinfo'][entry]['text'])
		cell['cellinfo'][entry]['label'].set_alignment(0, 0.5)
		cell['cellinfo'][entry]['value'] = gtk.Label('?')
		cell['cellinfo'][entry]['value'].set_alignment(1, 0.5)

	table = gtk.Table(15,20,True)
	table.attach(cell['cellinfo']['mcc']['label'], 1, 7, 1, 2)
	table.attach(cell['cellinfo']['mcc']['value'], 8, 10, 1, 2)

	table.attach(cell['cellinfo']['mnc']['label'], 1, 7, 2, 3)
	table.attach(cell['cellinfo']['mnc']['value'], 8, 10, 2, 3)

	table.attach(cell['cellinfo']['operator']['label'], 11, 15, 2, 3)
	table.attach(cell['cellinfo']['operator']['value'], 15, 19, 2, 3)

	table.attach(cell['cellinfo']['lac']['label'], 1, 7, 4, 5)
	table.attach(cell['cellinfo']['lac']['value'], 8, 10, 4, 5)

	table.attach(cell['cellinfo']['cell']['label'], 1, 7, 5, 6)
	table.attach(cell['cellinfo']['cell']['value'], 8, 10, 5, 6)

	table.attach(cell['cellinfo']['rnc']['label'], 11, 14, 5, 6)
	table.attach(cell['cellinfo']['rnc']['value'], 15, 19, 5, 6)

	table.attach(cell['cellinfo']['type']['label'], 1, 6, 6, 7)
	table.attach(cell['cellinfo']['type']['value'], 6, 10, 6, 7)

	table.attach(cell['cellinfo']['status']['label'], 11, 16, 6, 7)
	table.attach(cell['cellinfo']['status']['value'], 15, 19, 6, 7)

	table.attach(cell['cellinfo']['technology']['label'], 1, 7, 7, 8)
	table.attach(cell['cellinfo']['technology']['value'], 8, 10, 7, 8)

	table.attach(cell['cellinfo']['selected']['label'], 11, 16, 7, 8)
	table.attach(cell['cellinfo']['selected']['value'], 15, 19, 7, 8)

	table.attach(cell['cellinfo']['error']['label'], 1, 7, 9, 10)
	table.attach(cell['cellinfo']['error']['value'], 7, 19, 9, 10)

	table.attach(cell['cellinfo']['services']['label'], 1, 7, 10, 11)
	table.attach(cell['cellinfo']['services']['value'], 6, 19, 10, 11)

	table.attach(cell['cellinfo']['signal']['label'], 1, 7, 11, 13)
	table.attach(cell['cellinfo']['signal']['value'], 6, 19, 11, 13)
	table.attach(cell['signalbar'], 0, 20, 13, 16)
	
	table.set_col_spacing(1, 20)
	
	win.add(table)

	menu = main_menu()
	win.set_app_menu(menu)

	status_updates = StatusUpdates()
	status_updates.status_object_cell(cell)
	status_updates.start()

	win.connect("destroy", main_quit, status_updates, loop)
	win.show_all()
	loop.run()
	
if (__name__ == "__main__"):
	ret = main()
	exit(ret)
	