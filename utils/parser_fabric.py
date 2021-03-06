from fake_useragent import UserAgent
from selenium import webdriver
from seleniumwire import webdriver
from utils import system_utils


def create_driver():
    return _create_driver_firefox_marionette()


def _create_driver_only_headless():
    user_agent = UserAgent().firefox
    # if available_proxy is None:
    #     self.proxy_list = read_proxy_json(PROXY_PATH, PROXY_TYPE, PROXY_API)
    #     self.proxy = choice(self.proxy_list)
    # else:
    #     self.proxy = available_proxy

    extensions_path = system_utils.get_firefox_addons_dir()

    options = webdriver.FirefoxOptions()
    # options.add_argument("--disable-extensions")
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-application-cache')
    # options.add_argument('--disable-gpu')
    # options.add_argument("--disable-dev-shm-usage")
    options.headless = True

    sw_options = {
        # 'proxy': {
        #     'http': self.proxy,
        #     'https': self.proxy.replace('http', 'https')
        # },
        'user-agent': {
            user_agent,
        },
    }

    if options:
        driver = webdriver.Firefox(options=options, seleniumwire_options=sw_options)
    else:
        driver = webdriver.Firefox()

    driver.install_addon(f'{extensions_path}ublock_origin.xpi', )
    # self.driver.set_page_load_timeout(40)
    # self.driver.implicitly_wait(5)

    driver.set_window_size(1200, 1200)
    return driver


def _create_driver_firefox_marionette():
    # путь для расширений Firefox
    extensions_path = 'firefox_addons/ublock_origin.xpi'

    # юзер агент и прокси
    user_agent = UserAgent().firefox
    # self.proxy_list = read_proxy_json(PROXY_PATH, PROXY_TYPE, PROXY_API)
    # self.proxy = choice(self.proxy_list)
    # test_proxy(self.proxy, self.URL)
    caps = webdriver.DesiredCapabilities().FIREFOX
    caps["marionette"] = True
    # caps['handleAlerts'] = True
    # caps['acceptSslCerts'] = False
    # caps['acceptInsecureCerts'] = F
    # caps['security.mixed_content.use_hstsc'] = False

    options = webdriver.FirefoxOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--ignore-certificate-errors')
    options.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.http.use-cache', False)
    profile.accept_untrusted_certs = True
    profile.set_preference("javascript.enabled", True)
    profile.set_preference("security.mixed_content.use_hstsc", False)
    profile.add_extension(extension=extensions_path)
    # настройки для seleniumwire
    sw_options = {
        # 'proxy': {
        #     'http': self.proxy,
        #     'https': self.proxy.replace('http', 'https')
        # },
        'user-agent': {
            user_agent,
        },
    }
    driver = webdriver.Firefox(options=options,
                               seleniumwire_options=sw_options,
                               desired_capabilities=caps,
                               firefox_profile=profile)
    # self.driver = webdriver.Firefox()#seleniumwire_options=options)
    # self.driver.set_page_load_timeout(40)

    driver.install_addon(f'{extensions_path}')
    driver.set_window_size(1200, 1200)

    return driver
