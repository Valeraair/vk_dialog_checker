from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains as AC

start = datetime.datetime.now()
print('Время старта: ' + str(start))
driver = webdriver.Firefox()
action = AC(driver)
options = webdriver.FirefoxOptions()
options.page_load_strategy = 'eager'
options.add_argument('--disable-cache')
wait = WebDriverWait(driver, 20, 0.1)
stop_words_list = ['чат ', 'проспект ', 'улица ', 'группа', 'двор']  # Используется для функции delete_invalid_chats
log_locator = ('id', 'index_email')
dialog_name_locator = ('xpath', '//div[@class="nim-dialog--name"]')
dialog_head_locator = (
    'xpath', '//span[@class="im-page--title-main-in"]')  # //a[@class="im-page--title-main-inner _im_page_peer_name"]
dialog_options_locator = ('xpath', '//div[@onmouseover="window.uiActionsMenu && uiActionsMenu.show(this);"]'
                                   '//div[@aria-label="Действия"]')
dialog_delete_history_locator = ('xpath', '//a[@class="ui_actions_menu_item im-action im-action_clear _im_action"]')
dialog_delete_confirm_locator = ('xpath', '//button[@class="FlatButton FlatButton--primary FlatButton--size-m"]')
chat_name_locator = ('xpath', '//h3[@class="ChatSettingsInfo__title"]')
profile_menu_locator = ('xpath', '')
last_chat = open('last_chat.txt', 'r', encoding='utf-8')
last_acc = open('last_acc.txt', 'r', encoding='utf-8')


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
        time.sleep(1)
        # Вычисляем новую высоту прокрутки и сравниваем с последней высотой прокрутки.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def delete_invalid_chats():
    page_scroll()
    dialog_len = len(driver.find_elements(*dialog_name_locator))  # Находит количество бесед
    dialog_len_checker = dialog_len
    print(f'Диалогов к сканированию: {dialog_len}')
    for k in range(dialog_len - 1, 0, -1):
        page_scroll()
        time.sleep(1)
        page_scroll()
        try:
            driver.find_elements(*dialog_name_locator)[k].click()  # Начали шерстить беседы
        except:
            action.scroll_by_amount(0, -300)
            action.pause(1)
            action.perform()
            driver.find_elements(*dialog_name_locator)[k].click()
        time.sleep(1)
        wait.until(EC.visibility_of_element_located(dialog_head_locator))
        chat_head = driver.find_element(*dialog_head_locator).text.lower()
        if 'Чат ' not in driver.find_element(*dialog_head_locator).text and 'Двор ' not in driver.find_element(*dialog_head_locator).text and 'Проспект ' not in driver.find_element(*dialog_head_locator).text and 'Группа ' not in driver.find_element(*dialog_head_locator).text:    # Перемудрил. ПЕРЕПИСАТЬ ПО-ЧЕЛОВЕЧЕСКИ
            time.sleep(5)
            action.move_to_element(driver.find_element(*dialog_options_locator))
            action.pause(1)
            action.move_to_element(driver.find_element(*dialog_delete_history_locator))
            action.pause(1)
            action.click()
            action.pause(1)
            action.perform()
            wait.until(EC.element_to_be_clickable(dialog_delete_confirm_locator)).click()
            dialog_len -= 1
        else:
            driver.get('https://vk.com/im?tab=all')
    print(f'{dialog_len_checker - dialog_len} бесед удалено, осталось {dialog_len} бесед')


def dialog_checker(id):
    page_scroll()
    time.sleep(1)
    page_scroll()
    dialog_len = len(driver.find_elements(*dialog_name_locator))  # Находит количество бесед
    output_file = open(f'{i}. {id} all chats.txt', 'a+')
    try:
        dialog_current_position = int(last_chat.readline())
    except:
        dialog_current_position = 0
    for j in range(int(dialog_current_position), dialog_len):
        f = open('last_chat.txt', 'w')
        f.write(f'{j}')  # записываем текущие координаты, чтобы при перезапуске не выставлять их вручную
        f.close()
        # dialog_len_check = len(driver.find_elements(*dialog_name_locator))
        # while dialog_len_check < dialog_len:  # Проверяем, что отображаются все диалоги
        #    page_scroll()  #ПОКА ЗАКОМЕНТИЛ, ТАК КАК УХОДИТ В ВЕЧНЫЙ ЦИКЛ
        try:
            driver.find_elements(*dialog_name_locator)[j].click()  # Начали шерстить беседы
        except:
            action.scroll_by_amount(0, -300)
            action.pause(1)
            action.perform()
            driver.find_elements(*dialog_name_locator)[j].click()
        dialog_link = driver.current_url
        time.sleep(1)
        wait.until(EC.visibility_of_element_located(dialog_head_locator)).click()
        try:
            chat_name = wait.until(EC.visibility_of_element_located(chat_name_locator))
        except:
            driver.refresh()
            time.sleep(3)
            wait.until(EC.visibility_of_element_located(dialog_head_locator)).click()
            chat_name = wait.until(EC.visibility_of_element_located(chat_name_locator))
        output_file.write(f'{id}${dialog_link}${chat_name.text}\n')
        time.sleep(1)
        driver.get('https://vk.com/im?tab=all')
        time.sleep(1)
        page_scroll()
        time.sleep(1)
        page_scroll()
        print(f"{j + 1}/{dialog_len} COMPLETE")
    output_file.close()


def log_out():
    pass


with open('input.txt', 'r', encoding='utf-8') as input_data:  # Main script
    full = input_data.readlines()
    id_current_position = int(last_acc.readline())
    for i in range(id_current_position, len(full)):
        f = open('last_acc.txt', 'w')
        f.write(f'{i}')  # записываем текущие координаты, чтобы при перезапуске не выставлять их вручную
        f.close()
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
            time.sleep(3)
            driver.get('https://vk.com/im')
            page_scroll()
            dialog_delete_flag = input('Проверять невалидные диалоги? (y/n) ')
            time.sleep(1)
            page_scroll()
            time.sleep(1)
            if dialog_delete_flag == 'y':
                delete_invalid_chats()
                driver.get('https://vk.com/im')
                time.sleep(1)
                page_scroll()
            dialog_checker(lgn)
            driver.delete_all_cookies()
            v = open('last_chat.txt', 'w')
            v.write('0')
            v.close()
            driver.get('https://vk.com/')
