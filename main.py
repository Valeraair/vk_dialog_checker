from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

start = datetime.datetime.now()
print('Время старта: ' + str(start))
driver = webdriver.Firefox()
options = webdriver.FirefoxOptions()
wait = WebDriverWait(driver, 20, 1)
log_locator = ('id', 'index_email')
dialog_name_locator = ('xpath', '//div[@class="nim-dialog--name"]')
dialog_head_locator = ('xpath', '//div[@class="_im_dialog_title"]')
chat_name_locator = ('xpath', '//h3[@class="ChatSettingsInfo__title"]')
last_obj = open('last_obj.txt', 'r',  encoding='utf-8')   # position[0] -- номер диалога; position[0] -- номер аккаунта из input.txt


def auth(login, password):
    try:
        log = wait.until(EC.presence_of_element_located(log_locator))  # Поле для ввода логина
        log.clear()
        log.send_keys(login)
        log.send_keys(Keys.ENTER)  # Ввели логин и переходим на следующую страницу для ввода пароля
    except TimeoutException:
        print(f'Ошибка авторизации логина, {TimeoutException}')
    time.sleep(5)
    if len(driver.find_elements('xpath', '//span[@class="vkuiButton__in"]')) < 1:
        return False  # Проверяем, можно ли войти по паролю
    alternative_auth = wait.until(EC.element_to_be_clickable(driver.find_element('xpath', '//span['
                                                                                          '@class="vkuiButton__in"]')))
    # Находим кнопку для выбора способа входа
    alternative_auth.click()
    time.sleep(3)
    if len(driver.find_elements('xpath', '//div[@data-test-id="verificationMethod_password"]')) < 1:
        return False
    psw_button = wait.until(EC.element_to_be_clickable(driver.find_element('xpath', '//div[@data-test-id'
                                                                                    '="verificationMethod_password"]')))
    # Ждём, когда станет активной кнопка "пароль"
    psw_button.click()  # Переходим на страницу ввода пароля
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
        time.sleep(3)
        # Вычисляем новую высоту прокрутки и сравниваем с последней высотой прокрутки.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def dialog_checker(id):
    dialog_len = len(driver.find_elements(*dialog_name_locator))  # Находит количество бесед
    output_file = open(f'{id} all chats.txt', 'a+')
    dialog_current_position = last_obj.readlines()
    for j in range(int(dialog_current_position[1]), dialog_len):
        f = open('last_obj.txt', 'w')
        f.write(f'{i}\n{j}')    # записываем текущие координаты, чтобы при перезапуске не выставлять их вручную
        f.close()
        dialog_len_check = len(driver.find_elements(*dialog_name_locator))
        while dialog_len_check < dialog_len:  # Проверяем, что отображаются все диалоги
            page_scroll()
        driver.find_elements(*dialog_name_locator)[j].click()  # Начали шерстить беседы
        dialog_link = driver.current_url
        try:
            time.sleep(1)
            wait.until(EC.visibility_of_element_located(dialog_head_locator))
            driver.find_element(*dialog_head_locator).click()
            print('dialog head check')
            chat_name = wait.until(EC.visibility_of_element_located(chat_name_locator))
            print('chat name check')
        except:
            dialog_head = driver.find_element('xpath', '//a[@class="im-page--title-main-inner _im_page_peer_name"]')
            dialog_head.click()
            time.sleep(2)
            chat_name = driver.find_element('xpath', '//h3[@class="ChatSettingsInfo__title"]')
            print("got chat info exception")
        output_file.write(f'{id}${dialog_link}${chat_name.text}\n')
        time.sleep(1)
        driver.get('https://vk.com/im?tab=all')
        time.sleep(1)
        page_scroll()
        time.sleep(1)
        page_scroll()
        print(f"{j + 1}/{dialog_len} COMPLETE")
    output_file.close()


with open('input.txt', 'r', encoding='utf-8') as input_data:  # Main script
    full = input_data.readlines()
    id_current_position = last_obj.readline(1)
    for i in range(15, len(full)):
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
            page_scroll()
            time.sleep(5)
            dialog_checker(lgn)
