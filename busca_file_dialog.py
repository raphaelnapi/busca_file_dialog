import requests
import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
from colorama import Fore, Style

urls_para_visitar = []
urls_visitadas = []

url_inicial = ''
phpsessid = ''
netloc = ""

excludentes = []

def trata_argumentos():
	global url_inicial
	global url_para_visitar
	global phpsessid
	global netloc
	wordlist_file = ''

	for i in range(1, len(sys.argv)):
		if sys.argv[i] == '-u':
			url_inicial = sys.argv[i + 1]
			netloc = urlparse(url_inicial).netloc
			i = i + 1
		elif sys.argv[i] == '-list' or sys.argv[i] == '-file':
			wordlist_file = sys.argv[i + 1]
			with open(wordlist_file, 'r') as arq:
				urls_para_visitar.append(arq.readlines())
			i = i + 1
		elif sys.argv[i] == '-phpsessid':
			phpsessid = sys.argv[i + 1]
			i = i + 1
		elif sys.argv[i] in ['-h', '/?', '-help', 'man', '--help']:
			help()
			sys.exit(0)
		elif sys.argv[1] in ['-v', '--version', '-version']:
			print('busca_file_dialog.py 1.0')
			sys.exit(0)

	if url_inicial == "" and wordlist_file == "":
		help()
		sys.exit(0)

def help():
	print('busca_file_dialog.py    1.2')
	print('Script escrito em Python para identificar páginas com FileDialog (<input type=\"file\") em uma aplicação Web.')
	print()
	print('Uso:')
	print('python3 busca_file_dialog -u http://example_url')
	print('python3 busca_file_dialog -u http://example_url -phpsessid xxxxxxxxx')
	print('python3 busca_file_dialog -list url_list_filepath')
	print('python3 busca_file_dialog -file url_list_filepath')
	print()
	print('Parâmetros:')
	print('-u [url] \t\t Informa a URL que será base para a busca por FileDialog')
	print('-phpsessid [phpsessid] \t Informa o ID de sessão PHP para buscar em aplicação que necessita login')
	print('-file [url list]')
	print('-list [url list] \t Informa caminho do arquivo lista de URL que contém uma URL por linha')

def busca_file_dialog(url):
	global urls_para_visitar
	global urls_visitadas
	global phpsessid

	if url in urls_visitadas:
		return

	urls_visitadas.append(url)

	cookies = {}

	if phpsessid != '':
		cookies['PHPSESSID'] = phpsessid

	response = requests.get(url, cookies=cookies, headers={"Accept-Encoding": "identity"})
	soup = BeautifulSoup(response.text, 'html.parser')

	a_list = soup.find_all('a')
	for a in a_list:
		uri_relativa = a.get('href')
		if uri_relativa == None:
			continue

		#remove excludentes
		if any(exc in uri_relativa  for exc in excludentes):
			continue

		nova_url = urljoin(response.url, uri_relativa)
		
		#remove URL fora do dominio
		target_netloc = urlparse(nova_url).netloc
		if target_netloc != netloc:
			continue

		if not nova_url in urls_para_visitar:
			urls_para_visitar.append(nova_url)

	print(f'{url:<50}\t', end='')
	if 'type="file"' in response.text:
		print(Fore.BLUE + '\033[1mPossui FileDialog' + Style.RESET_ALL)
	else:
		print(Fore.RED + 'Não possui FileDialog' + Style.RESET_ALL)

trata_argumentos()

if url_inicial != "":
	busca_file_dialog(url_inicial)

for url in urls_para_visitar:
	try:
		busca_file_dialog(url)
	except:
		continue
