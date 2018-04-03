from gm import Gmail
import time, sys, os
import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CI():

	def __init__(self):
		self._driver = None
		self._scr = None
		self._scr_list = []
		self._tab_text = 'teststasdta'
		self._sym_file = "%s.syms"%(dt.datetime.now().strftime("%Y%m%d"))
		self._symbols = []
		self._new_syms = False
		self._phantomjs_bin_path = "/opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs"

	def __usage(self):
		hmsg = "Usage:\n"
		hmsg += "python %s <screener> . . . "%(sys.argv[0])
		print hmsg
		sys.exit()

	def __logme(self,msg):
		print "%s|%s%s"%(dt.datetime.now().strftime("%Y%m%d-%H%M%S"),
				"%s|"%(self._scr) if self._scr else '', msg)

	def __driver_initiate(self):
		self._driver = webdriver.PhantomJS(executable_path=self._phantomjs_bin_path)
		#self._driver = webdriver.Firefox()
		self._driver.set_window_size(1120, 550)

	def __read_symbols(self):
		if not os.path.exists(self._sym_file): return
		with open(self._sym_file,'r') as f1:
			for line in f1.readlines():
				line = line.strip()
				if line not in self._symbols: self._symbols.append(line)

	def __save_symbols(self):
		with open(self._sym_file,'w') as f1:
			for sym in self._symbols: f1.write(sym+"\n")
		
	def __poll_screener(self):
		#https://chartink.com/screener/copy-supertrend-positive-breakout-1652
		self.__logme("Checking screener")
		self._driver.get("https://chartink.com/screener/%s"%(self._scr))
		#elem = WebDriverWait(self._driver, 90).until(
		#	EC.element_to_be_clickable((By.LINK_TEXT, "Updated Packages")))
		#upd = self._driver.find_element_by_link_text('Updated Packages')
		#upd.click()
		time.sleep(5)
		tab = self._driver.find_element_by_id("DataTables_Table_0")
		self._tab_text = tab.get_attribute('innerHTML')
	  	tt = []	
		thead = ''
		trs = tab.find_elements_by_tag_name('tr')
		for tr in trs:
			if tr.find_elements_by_tag_name('th'): thead = tr
			elems = tr.find_elements_by_tag_name('a')
			for elem in elems:
				hrf = elem.get_attribute('href')
				#print hrf
				#if elem.get_attribute('href').contains('/stocks'):
				if '/stocks' in hrf:
					sym = hrf.split('/')[-1].split('.')[0]
					if sym not in self._symbols:
						self.__logme(sym)
						self._symbols.append(sym)
						self._new_syms = True
						tt.append(tr)
		if self._new_syms:
			tt.insert(0, thead)
			self._tab_text = '\n'.join('<tr>'+x.get_attribute('innerHTML')+'</tr>' for x in tt)
			
	def __teardown(self):
		self.__logme("Closing browser..")
		self._driver.quit()

	def __send_msg(self):
		Gmail().send_message('[%s] ST bull'%(dt.datetime.now().strftime("%Y%m%d-%H%M%S")), self._tab_text)



	def run(self):
		if len(sys.argv) < 2 : 
			self.__logme("NO screener supplied, Exiting..")
			self.__usage()

		self.__logme(sys.argv)
		for x in sys.argv[1:]:	
			if x == '-h': self.__usage()
			self._scr_list.append(x)
		if not self._scr_list:
			self.__logme("No valid screener supplied, Exiting..")
			self.__usage()

		self.__driver_initiate()
		for x in self._scr_list:
			self._scr = x
			self.__logme("Start")	
			self.__read_symbols()
			self.__poll_screener()
			#print self._tab_text
			self.__logme("Complete")	
			self._scr = None	
		if self._new_syms:
			self.__save_symbols()
			self.__send_msg()
		self.__teardown()

if __name__ == "__main__":

	ci = CI()
	ci.run()
