import time
import pickle
# import selenium.webdriver
from seleniumwire import webdriver as webdriver_sw
from selenium import webdriver

# URL_PASSPORT = 'https://service.nalog.ru/inn.do'
URL = 'https://росреестр-выписка.онлайн/search'

profile = webdriver_sw.FirefoxProfile()

profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.manager.useWindow", True)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf;")
profile.set_preference("pdfjs.disabled", True)
profile.set_preference('security.insecure_field_warning.contextual.enabled', False)
profile.set_preference('security.certerrors.permanentOverride', False)
profile.set_preference('network.stricttransportsecurity.preloadlist', False)
profile.set_preference("security.enterprise_roots.enabled", True)
profile.accept_untrusted_certs = True

capabilities = webdriver.DesiredCapabilities().FIREFOX
capabilities['acceptInsecureCerts'] = True
capabilities['marionette'] = True

driver = webdriver.Firefox(firefox_profile=profile, desired_capabilities=capabilities)
driver.get(URL)
time.sleep(40)

pickle.dump( driver.get_cookies() , open("cookies","wb"))

driver.quit()
