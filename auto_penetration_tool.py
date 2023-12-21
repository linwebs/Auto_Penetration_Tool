#!/usr/bin/env python
import sys
import ipaddress
import argparse

from src.vsftpd_exploit.exploit import ExploitFTP
from ipcam import *
from portscanner import *

DEFAULT_IP_RANGE = '10.81.1.0/29'
PROGRAM_NAME = 'Auto penetration tool'


def ip_cam():
	#
	return


def ftp_server(ip, port):
	# vsftpd rce
	print("vsftpd RCE", ip, port)

	if len(sys.argv) == 3:
		exploit = ExploitFTP(ip, port)
	else:
		exploit = ExploitFTP(ip)

	exploit.trigger_backdoor()
	exploit.get_shell()
	return


def web_server():
	# wp
	# survey
	# sqlmap
	return


def ask_question(can_choose):
	user_choose = input()

	try:
		choose = int(user_choose)
	except ValueError:
		print("Error: Your input not in list")
		return False

	if choose < 1 or choose > can_choose:
		print("Error: Your input not in list")
		return False

	return choose


def attack_service(services):
	item_turn = 0
	print("")
	print("+------+------------------+---------+-----------------------+")
	print("| Can Exploit list                                          |")
	print("+------+------------------+---------+-----------------------+")
	print("|    # | IP               | Port    | Service               +")
	print("+------+------------------+---------+-----------------------+")
	for host in services:
		for service in services[host]:
			if service['exploit'] in ['vsftpd_2_3_4', 'apache', 'ip_cam_rtsp']:
				item_turn += 1
				print("|", (3 - len(str(item_turn))) * " ", item_turn, end=" ")
				print("|", ((15 - len(host)) * " "), host, end=" ")
				print("|", ((5 - len(str(service['port']))) * " "), service['port'], " |", end=" ")
				print(service['exploit'], (20 - len(service['exploit'])) * " ", "|")
				print("+------+------------------+---------+-----------------------+")

	if item_turn == 0:
		print("| Not found any exploit                                     |")
		print("+------+------------------+---------+-----------------------+")
	else:
		print("Which do you want to exploit: ", end="")
		choose = ask_question(item_turn)

		if choose:
			print("Your choose:", choose)
	return


def main():
	parser = argparse.ArgumentParser(description=PROGRAM_NAME + ' by 112 HTCF course group 8')
	parser.add_argument("-i", "--ip", action="store", help="specify IP address or IP range")
	parser.add_argument("-p", "--port", action="store", help="specify port")

	args = parser.parse_args()

	ip_address = DEFAULT_IP_RANGE

	if args.ip is not None:
		try:
			ipaddress.ip_address(args.ip)
			ip_address = args.ip
		except ValueError:
			try:
				ipaddress.ip_network(args.ip)
				ip_address = args.ip
			except ValueError:
				print('Error: Your IP address or range is not valid')
				return

	if args.port is None:
		port = '21,22,80,554'
	else:
		arr = args.port.split(',')
		for i in arr:
			try:
				port_check = int(i)
			except ValueError:
				print("Error: Port is invalid")
				return

			if port_check <= 0 or port_check > 65535:
				print("Error: Port is invalid")
				return
		port = args.port

	column_max_len = len(ip_address)
	if len(str(port)) > column_max_len:
		column_max_len = len(str(port))

	print("+-----------+-{}--+".format(column_max_len * "-"))
	print("| {}{} |".format(PROGRAM_NAME, (column_max_len + 13 - len(PROGRAM_NAME)) * " "))
	print("+-----------+-{}--+".format(column_max_len * "-"))
	print("| Scan IP   |", ((column_max_len - len(ip_address)) * " "), ip_address, "|")
	print("| Scan port |", ((column_max_len - len(str(port))) * " "), str(port), "|")
	print("+-----------+-{}--+".format(column_max_len * "-"))
	print("")
	print("Scanning...")

	attack_service(portscan(ip_address, port))


if __name__ == '__main__':
	main()
