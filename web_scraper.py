import socket
import sys
import argparse
import requests
from bs4 import BeautifulSoup

LHOST = '127.0.0.1'
LPORT = 4567
MAX_BYTES = 65535

class Server:

	def __init__(self,host,port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def listen(self):
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host,self.port))
		self.sock.listen(1)
		print("[+][SERVER] waiting for connection at ",self.sock.getsockname())

		while True:
			sckt,sockname=self.sock.accept()
			print("*"*80)
			print("[+][SERVER] accepted a connection from ",sockname)
			print("*"*80)
			data=sckt.recv(MAX_BYTES)
			print(f"[+][URL]:{data.decode('utf-8')} will be processed by [SERVER]")
			URLdata=data.decode('utf-8')
			print("="*80)
			img_count=self.count_img(URLdata)
			leaf_count=self.leaf(URLdata)
			
			data="The number of '<img>' tags is:"+"\n"+str(img_count)+"\n"+"The number of '<p>' tags is:"+"\n"+str(leaf_count)
			sckt.sendall(data.encode('utf-8'))
			sckt.close()


	def count_img(self,url):
		page=requests.get(url)
		
		soup=BeautifulSoup(page.text,'html.parser')
		count=0
		imgs=soup.find_all("img")
		
		for i in imgs:
			count+=1
		return count

	def leaf(self,url):
		page=requests.get(url)
		soup=BeautifulSoup(page.text,'html.parser')
		count=0
		lf=soup.find_all('p')

		for i in lf:
			if not i.find_all('p'):
				count+=1
		return count


class Client:
	def __init__(self,host,port):
		self.host=host
		self.port=port
		self.sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	def connect(self,url_addr):

		self.sc.connect((self.host,self.port))

		print("[+][CLIENT] socket created at ",self.sc.getsockname())
		self.sc.sendall(url_addr.encode('utf-8'))
		result=self.sc.recv(MAX_BYTES).decode("utf-8")

		print(result)
		self.sc.close()

def main():
    parser = argparse.ArgumentParser(description="Web Page Scrapper")
    roles = {'client': Client, 'server': Server}

    parser.add_argument("role", choices=roles, help="role choices: server or client")
    if sys.argv[1] == 'client':
        parser.add_argument('-p', metavar='PAGE', type=str, help='URL address of the web page')
    args = parser.parse_args()

    if args.role == 'server':
        Server(LHOST, LPORT).listen()
    elif args.role == 'client':
        Client(LHOST, LPORT).connect(args.p if "http://" in args.p or "https://" in args.p else f"https://{args.p}")

if __name__ == "__main__":
    main()
