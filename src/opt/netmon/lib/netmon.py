#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time
import sys
import gtk
import hildon
import gn_battery
import gn_cellinfo

class ReadSensors(threading.Thread):
	global page, label1, label2, label3, label4, label5, label6

	def Cellular(self):
		regstatus = gn_cellinfo.RegStatus()
		signalstrength = gn_cellinfo.SignalStrength()

		if (regstatus[0] == 0): status = 'home'
		elif (regstatus[0] == 1): status = 'roam'
		elif (regstatus[0] == 2): status = 'roam_blink'
		elif (regstatus[0] == 3): status = 'no serv.'
		elif (regstatus[0] == 4): status = 'no serv. search'
		elif (regstatus[0] == 5): status = 'no serv. no search'
		elif (regstatus[0] == 6): status = 'no sim'
		elif (regstatus[0] == 8): status = 'power off'
		elif (regstatus[0] == 9): status = 'nsps'
		elif (regstatus[0] == 10): status = 'nsps no cover.'
		elif (regstatus[0] == 10): status = 'sim rejected'
		else: status = 'unknown'

		if (regstatus[5] == 0): network_type = 'home'
		elif (regstatus[5] == 1): network_type = 'preferred'
		elif (regstatus[5] == 2): network_type = 'forbidden'
		elif (regstatus[5] == 2): network_type = 'other'
		else: network_type = 'no network'
			
		label1.set_text("Network Status: %s  Type: %s" % (status, network_type))
		label2.set_text("Location Area Code: %i" % regstatus[1])
		label3.set_text("Cell ID: %i" % regstatus[2])
		label4.set_text("Mobile Country Code: %i  Mobile Network Code: %i" % (regstatus[4], regstatus[3]))

		services = ""
		if (regstatus[6] & 0x02): services += 'CS '
		if (regstatus[6] & 0x01): services += 'GPRS '
		if (regstatus[6] & 0x04): services += 'EGPRS '
		if (regstatus[6] & 0x08): services += 'HSDPA '
		if (regstatus[6] & 0x10): services += 'HSUPA'
			
		label5.set_text("Net Err: %i  Supported Services: %s" % (regstatus[7], services))
		label6.set_text("Signal Strength: %i dBm" % signalstrength[1] )

	def Battery(self):
		current = gn_battery.BatteryLevelCurrent()
		design = gn_battery.BatteryLevelDesign()
		full = gn_battery.BatteryLevelFull()
		unit = gn_battery.BatteryLevelUnit()

		label1.set_text("%s: %i of %i" % (unit.capitalize(), current, full))

		current = gn_battery.BatteryReportingCurrent()
		design = gn_battery.BatteryReportingDesign()
		full = gn_battery.BatteryReportingFull()
		if (full == 0): full = design
		unit = gn_battery.BatteryReportingUnit()
		label2.set_text("Percentage: %i %%" % gn_battery.BatteryPercent())
		label3.set_text("Capacity: %i %s of %i %s" % (current, unit, full, unit))

		current = gn_battery.BatteryVoltageCurrent()
		design = gn_battery.BatteryVoltageDesign()
		unit = gn_battery.BatteryVoltageUnit()

		label4.set_text("Voltage: %i %s of %i %s" % (current, unit, design, unit))

		if (gn_battery.BatteryCharging() == 0): charging = "no"
		else: charging = "yes"

		if (gn_battery.BatteryDischarging() == 0): discharging = "no"
		else: discharging = "yes"
			
		label5.set_text("Charging: %s  Discharging: %s" % (charging, discharging))

		if (gn_battery.BatteryPresent() == 0): present = "no"
		else: present = "yes"
				
		if (gn_battery.BatteryRechargeable() == 0): rechargeable = "no"
		else: rechargeable = "yes"
		
		label6.set_text("Battery Present: %s  Rechargeable: %s" % (present, rechargeable))

	def About(self):
		label1.set_text("")
		label2.set_text("NetMon Version 0.1")
		label3.set_text("")
		label4.set_text("Written by spag 2010")
		label5.set_text("netmon.garage.maemo.org")
		label6.set_text("")
		
	stopthread = threading.Event()

	def run(self):
		while not self.stopthread.isSet() :
			gtk.gdk.threads_enter()
			if (page == "Cellular"): self.Cellular()
			elif (page == "Battery"): self.Battery()
			else: self.About()
			gtk.gdk.threads_leave()

			time.sleep(3)

	def stop(self):
		self.stopthread.set()
	
def menu_button_clicked(button):
	global page
	
	buttonlabel = button.get_label()
	page = buttonlabel
	
def main_menu(label):
	menu = hildon.AppMenu()

	button = hildon.GtkRadioButton(gtk.HILDON_SIZE_AUTO, None)
	button.set_label("Cellular")
	button.connect("clicked", menu_button_clicked)
	menu.add_filter(button)
	button.set_mode(False)
	
	button = hildon.GtkRadioButton(gtk.HILDON_SIZE_AUTO, button)
	button.set_label("Battery")
	button.connect("clicked", menu_button_clicked)
	menu.add_filter(button)
	button.set_mode(False)
	
	button = hildon.GtkRadioButton(gtk.HILDON_SIZE_AUTO, button)
	button.set_label("About")
	button.connect("clicked", menu_button_clicked)
	menu.add_filter(button)
	button.set_mode(False)
	menu.show_all()
	
	return menu

def main_quit(obj, sensor_thread):
	sensor_thread.stop()
	gtk.main_quit()

def main():

	global page, label1, label2, label3, label4, label5, label6

	page = "Cellular"
	
	win = hildon.StackableWindow()
	win.set_title("NetMon")
	
	label1 = gtk.Label("label1")
	label2 = gtk.Label("label2")
	label3 = gtk.Label("label3")
	label4 = gtk.Label("label4")
	label5 = gtk.Label("label5")
	label6 = gtk.Label("label6")
	
	label1.set_justify(gtk.JUSTIFY_CENTER)
	label2.set_justify(gtk.JUSTIFY_CENTER)
	
	vbox = gtk.VBox(False, 10)
	
	vbox.pack_start(label1, True, True, 0)
	vbox.pack_start(label2, True, True, 0)
	vbox.pack_start(label3, True, True, 0)
	vbox.pack_start(label4, True, True, 0)
	vbox.pack_start(label5, True, True, 0)
	vbox.pack_start(label6, True, True, 0)
	
	menu = main_menu(label1)
	win.set_app_menu(menu)
	win.add(vbox)

	sensor_thread = ReadSensors()
	sensor_thread.start()

	win.connect("destroy", main_quit, sensor_thread)
	
	win.show_all()
	
	gtk.main()


gtk.gdk.threads_init()
if __name__ == "__main__":
	main()