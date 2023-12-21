import nmap
import sys


def portscan(ip, port):
	nm = nmap.PortScanner()
	arg = '-sV -p T:' + str(port)

	nm.scan(hosts=ip, arguments=arg)
	# print("IP Lists :", nm.all_hosts())
	scanner = {}
	sys.stdout.write("\033[F")
	print("+------------------------------+")
	print("| Port open list               |")
	print("+------------------+-----------+")
	print("|        IP        |    Port   |")
	print("+------------------+-----------+")

	all_port_open_count = 0
	for this_host in nm.all_hosts():
		host_port_open_count = 0
		print("|", ((15 - (len(this_host))) * " "), this_host, "|", end="")

		for this_protocol in nm[this_host].all_protocols():
			match this_protocol:
				case 'tcp':
					tmp_service = []
					for this_port in nm[this_host]['tcp'].keys():
						if nm[this_host][this_protocol][this_port]['state'] == "open":
							host_port_open_count += 1
							if host_port_open_count > 1:
								print("|                  | ", end="")
							else:
								print(" ", end="")
							for i in range(5 - len(str(this_port))):
								print(" ", end="")
							print("{}/tcp |".format(this_port))

							if this_port == 21:
								if nm[this_host][this_protocol][this_port]['product'] == 'vsftpd' and nm[this_host][this_protocol][this_port]['version'] == '2.3.4':
									tmp_service.append({'port': this_port, 'protocol': this_protocol, 'exploit': 'vsftpd 2.3.4'})
							if this_port == 22:
								if nm[this_host][this_protocol][this_port]['product'] == 'OpenSSH':
									tmp_service.append({'port': this_port, 'protocol': this_protocol, 'exploit': 'ssh server'})
							if this_port == 80:
								if nm[this_host][this_protocol][this_port]['product'] == 'alphapd':
									tmp_service.append({'port': this_port, 'protocol': this_protocol, 'exploit': 'ip cam web'})
								if nm[this_host][this_protocol][this_port]['product'] == 'Apache httpd':
									tmp_service.append({'port': this_port, 'protocol': this_protocol, 'exploit': 'apache web server'})
							if this_port == 554:
								if nm[this_host][this_protocol][this_port][
									'product'] == 'D-Link DCS-2130 or Pelco IDE10DN webcam rtspd':
									tmp_service.append({'port': this_port, 'protocol': this_protocol, 'exploit': 'ip cam rtsp'})

					scanner[this_host] = tmp_service

			if host_port_open_count == 0:
				print("     -      |")
			print("+------------------+-----------+")


		all_port_open_count += host_port_open_count
	if all_port_open_count == 0:
		print("| No open port                  |")
		print("+-------------------------------+")

	return scanner
