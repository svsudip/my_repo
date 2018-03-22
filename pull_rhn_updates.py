import time, sys, os
import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RHN():

	def __init__(self):
		self._rhn_user = "rhnuser"
		self._rhn_passwd = "xxxxxx"
		self._driver = None
		self._rhsa = None	
		self._rhsa_list = []
		self._phantomjs_bin_path = "/opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs"

	def __usage(self):
		hmsg = "Usage:\n"
		hmsg += "python %s <RHSA-xxx:xxx> . . . "%(sys.argv[0])
		print hmsg
		sys.exit()

	def __logme(self,msg):
		print "%s|%s%s"%(dt.datetime.now().strftime("%Y%m%d-%H%M%S"),
				"%s|"%(self._rhsa) if self._rhsa else '', msg)

	def __driver_initiate(self):
		self._driver = webdriver.PhantomJS(executable_path=self._phantomjs_bin_path)
		self._driver.set_window_size(1120, 550)

	def __login(self):
		self.__logme("Logging into RHN")
		self._driver.get("https://access.redhat.com/login")
		self._driver.find_element_by_id("username").send_keys(self._rhn_user)
		self._driver.find_element_by_id("password").send_keys(self._rhn_passwd)
		self._driver.find_element_by_id("_eventId_submit").click()

		elem = WebDriverWait(self._driver, 90).until(
			EC.element_to_be_clickable((By.ID, "accountUserName")))


		sp_uname = self._driver.find_element_by_id("accountUserName")
		if sp_uname.text != 'Spa User':
			self.__logme("Login failure, exiting..")
			sys.exit()
		else:
			self.__logme("Login successful !")
	

	def __fetch_packages(self):
		downloaded_rpms = []
		updated_rpms = []
		self.__logme("Checking updated packages")
		self._driver.get("https://access.redhat.com/errata/%s"%(self._rhsa))
		elem = WebDriverWait(self._driver, 90).until(
			EC.element_to_be_clickable((By.LINK_TEXT, "Updated Packages")))
		upd = self._driver.find_element_by_link_text('Updated Packages')
		upd.click()
		time.sleep(5)
		elems = self._driver.find_elements_by_xpath("//td[@class='name'][contains(text(),'rpm')]")
		for elem in elems:
			if elem.text in updated_rpms: continue
			self.__logme("Updated package: %s"%(elem.text))
			updated_rpms.append(elem.text)

		self.__logme("Checking for available rpm links")
		links = self._driver.find_elements_by_class_name("rpmLink")
		
		if not os.path.exists(self._rhsa):
			self.__logme("Creating folder %s"%(self._rhsa))
			os.mkdir(self._rhsa)

		if len(links) < 1: self.__logme("rpm download links are not available")
		for link in links:
			href =  link.get_attribute('href')
			rpmname = href.split('?')[0].split('/')[-1]
			if '.src.' in rpmname: 
				self.__logme("Excluding rpm download %s"%(rpmname))
				continue
			if rpmname in downloaded_rpms: continue
			self.__logme(href)
			self.__logme("Downloading rpm: %s"%(rpmname))
			curlcmd = "curl -s %s -o %s/%s"%(href,self._rhsa,rpmname)
			os.system(curlcmd)
			time.sleep(3)
			downloaded_rpms.append(rpmname)

	def __logout(self):
		self.__logme("Logging out user")
		self._driver.get("https://access.redhat.com/logout")
		time.sleep(10)

	def __teardown(self):
		self.__logme("Closing browser..")
		self._driver.quit()


	def run(self):
		if len(sys.argv) < 2 : 
			self.__logme("NO rhsa supplied, Exiting..")
			self.__usage()

		self.__logme(sys.argv)
		for x in sys.argv[1:]:	
			if x == '-h': self.__usage()
			if not x.startswith('RH'): continue
			else: self._rhsa_list.append(x)
		if not self._rhsa_list:
			self.__logme("No valid rhsa supplied, Exiting..")
			self.__usage()

		self.__driver_initiate()
		self.__login()
		for x in self._rhsa_list:
			self._rhsa = x
			self.__logme("Start")	
			self.__fetch_packages()
			self.__logme("Complete")	
			self._rhsa = None

		self.__logout()
		self.__teardown()

if __name__ == "__main__":
	rhn = RHN()
	rhn.run()
