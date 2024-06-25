from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait

start = datetime.datetime.now()
print('Время старта: ' + str(start))
driver = webdriver.Firefox()
options = webdriver.FirefoxOptions()
wait = WebDriverWait(driver, 5, 0.1)


def auth(login, password):
    log = driver.find_element('id', 'index_email')
    time.sleep(2)
    log.clear()
    log.send_keys(login)
    log.send_keys(Keys.ENTER)  # Ввели логин и переходим на следующую страницу для ввода пароля
    time.sleep(10)
    if len(driver.find_elements('xpath', '//span[@class="vkuiButton__in"]')) < 1:
        return False
    alternative_auth = driver.find_element('xpath', '//span[@class="vkuiButton__in"]')  # Находим кнопку
    # для выбора способа входа
    alternative_auth.click()
    time.sleep(3)
    if len(driver.find_elements('xpath', '//div[@data-test-id="verificationMethod_password"]')) < 1:
        return False
    psw_button = driver.find_element('xpath', '//div[@data-test-id="verificationMethod_password"]')
    psw_button.click()
    time.sleep(3)
    psw = driver.find_element('xpath', '//input[@name="password"]')
    psw.send_keys(password)
    psw.send_keys(Keys.ENTER)
    time.sleep(3)
    return True


def page_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Прокрутка вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Пауза, пока загрузится страница.
        time.sleep(2)
        # Вычисляем новую высоту прокрутки и сравниваем с последней высотой прокрутки.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def dialog_checker(id):
    dialog_len = len(driver.find_elements('xpath', '//div[@class="nim-dialog--name"]'))
    output_file = open(f'{id} all chats.txt', 'a+')
    for j in range(dialog_len):
        driver.find_elements('xpath', '//div[@class="nim-dialog--name"]')[j].click()    # Начали шерстить беседы
        time.sleep(5)
        dialog_link = driver.current_url
        dialog_head = driver.find_element('xpath', '//a[@class="im-page--title-main-inner _im_page_peer_name"]')
        dialog_head.click()
        time.sleep(5)
        dialog_name = driver.find_element('xpath', '//h3[@class="ChatSettingsInfo__title"]').text
        output_file.write(f'{id}${dialog_link}${dialog_name}\n')
        time.sleep(3)
        driver.get('https://vk.com/im?tab=all')
        time.sleep(3)
        page_scroll()
        time.sleep(3)
    output_file.close()


with open('input.txt', 'r', encoding='utf-8') as input_data:  # Main script
    full = input_data.readlines()
    for i in range(1, len(full)):  # ИСПРАВИТЬ, ЧТОБЫ ПЕРЕБОР АККАУНТОВ НАЧИНАЛСЯ С НАЧАЛА ФАЙЛА
        data = full[i].split(';')
        lgn = data[0]  # Логин для авторизации
        psw = data[1]  # Пароль для авторизации
        driver.get('https://vk.com/')  # Заходим на страницу с авторизацией
        time.sleep(4)
        if not auth(lgn, psw):
            print(f'{lgn} Не удалось войти в аккаунт')
            continue
        else:
            print(f'{lgn} AUTH COMPLETE')
            driver.get('https://vk.com/im')
            time.sleep(5)
            page_scroll()
            time.sleep(5)
            dialog_checker(lgn)
