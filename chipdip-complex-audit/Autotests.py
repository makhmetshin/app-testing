import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True — без окна браузера
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    return page


def test_cart_flow(page):

    # добавляем товар
    page.goto("https://www.chipdip.ru/product/adm2481brwz")
    page.click("button.add2cart")

    page.wait_for_selector("button.add2cart:has-text('Перейти в корзину')")
    page.goto("https://www.chipdip.ru/cart")
    assert "ADM2481BRWZ-RL7" in page.inner_text(".link.name")

    # удаляем товар
    page.click("text=Удалить выбранные")
    page.click("#fancyConfirm_ok")
    page.wait_for_timeout(1000)

    # добавляем товар снова
    page.goto("https://www.chipdip.ru/product/adm2481brwz")
    page.click("button.add2cart")
    page.wait_for_timeout(1000)
    page.wait_for_selector("button.add2cart:has-text('Перейти в корзину')")
    page.goto("https://www.chipdip.ru/cart")
    assert "ADM2481BRWZ-RL7" in page.inner_text(".link.name")

    # оформление заказа
    page.click("text=К оформлению")
    page.wait_for_timeout(1000)
    #       вход
    page.fill("input[name='login']", "samplebuzz")
    page.fill("input[name='pwd']", "zx1235zx")
    page.click("button:has-text('Войти')")
    page.wait_for_timeout(1000)
    assert page.locator("h3:has-text('Доставка')").is_visible(), "Блок 'Доставка' не найден"
    assert page.locator("h3:has-text('Оплата')").is_visible(), "Блок 'Оплата' не найден"

    # переходим на страницу товара из корзины
    page.goto("https://www.chipdip.ru/cart")
    page.click("text=ADM2481BRWZ-RL7") # ADM2481BRWZ-RL7
    assert "ADM2481BRWZ-RL7" in page.content()

def test_profile_and_order(page):
    page.goto("https://www.chipdip.ru")
    page.click("text=Вход")
    page.fill("input[name='login']", "samplebuzz")
    page.fill("input[name='pwd']", "zx1235zx")
    page.click("button:has-text('Войти')")
    page.wait_for_timeout(1000)

    page.click("a.account-idx-item-orders:has-text('Заказы')")
    assert "Пока нет заказов" in page.content()

    page.goto("https://www.chipdip.ru/account")
    page.click("a.account-idx-item-notifications")
    assert "Нет новых уведомлений" in page.content()

    page.goto("https://www.chipdip.ru/account")
    page.click("a.account-idx-item-promocodes")
    assert "Как воспользоваться промокодом?" in page.content()

    # добавляем в избранное и в конце подчищаем убираем из избранного
    page.goto("https://www.chipdip.ru/product/adm2481brwz")
    page.click("button.add2fav")
    page.goto("https://www.chipdip.ru/account")
    page.click("a.account-idx-item-favorites")
    page.wait_for_timeout(2000)
    assert "ADM2481BRWZ-RL7" in page.content()
    page.click("text=Очистить «Избранное»")
    page.click("#fancyConfirm_ok") #


    # спецификации
    page.click("text=BOM ")
    page.click("text=Новая спецификация")
    # page.click("text=Покажите мне пример")
    page.fill("#specs", "MMDT3904\t60\n781324\t9")
    page.click("text=Импорт")
    page.wait_for_timeout(1000)
    page.click("text=Импорт")
    page.click("text=Начать обработку")
    page.wait_for_timeout(2000)
    assert "MMDT3904" in page.content()

    # добавление тоавара из спецификации в корзину
    checkbox = page.locator("tr:has-text('MMDT3904') input[type='checkbox']").first
    checkbox.click(force=True)
    page.wait_for_timeout(1000)
    page.click("text=Добавить в корзину")
    page.wait_for_timeout(1000)
    page.goto("https://www.chipdip.ru/cart")
    assert "MMDT3904" in page.content()


def test_search(page):
    # поиск через строку
    page.goto("https://www.chipdip.ru")
    page.fill("input[name='searchtext']", "ADM2481BRWZ - RL7")
    page.click("button.header__search-button")
    page.wait_for_timeout(1000)
    assert "ADM2481BRWZ - RL7" in page.content()

    # поиск по категориям
    page.goto("https://www.chipdip.ru")
    page.click("text=Каталог товаров")
    page.click("text=Электронные компоненты")
    page.click("text=AC-DC Преобразователи, Off-Line коммутаторы")
    assert "https://www.chipdip.ru/catalog/ic-ac-dc-converters" == page.url

    page.locator("tr.with-hover a.link").first.click()
    assert "www.chipdip.ru/product" in page.url


    # добавим в сравнение
    page.click("button.add2compare")
    good_name = page.locator("h1[itemprop='name']").inner_text()
    print(good_name)
    page.click("text=Сравнить")
    assert good_name in page.content()
    page.click("text=Очистить список")

    # рекомендованные товары
    page.goto("https://www.chipdip.ru/product/adm2481brwz")
    # наличие рекомендованных товаров
    assert page.locator(".product__group_g").count() > 0, "Блок рекомендованных групп товаров не найден"
    # наличие хоть одного товара
    assert page.locator(".product__group_g .product_simple").count() > 0, "Нет рекомендованных товаров в блоке"


    page.goto("https://www.chipdip.ru/product/adm2481brwz")

    # рекомендованные товары
    assert page.locator(".product__group_g").count() > 0, "Блок рекомендованных групп товаров не найден"
    # наличие хоть одного товара
    assert page.locator(".product__group_g .product_simple").count() > 0, "Нет рекомендованных товаров в блоке"

    # похожие товары
    assert page.locator(".product__group").count() > 0, "Блок похожих товаров не найден"
    # Проверка наличия хотя бы одного похожего товара
    assert page.locator(".product__group .product_simple").count() > 0, "Нет похожих товаров в блоке"

    # Документация
    assert page.locator(".product__documentation").count() > 0, "Блок технической документации не найден"
    # Проверка наличия хотя бы одной ссылки на PDF-документ
    assert page.locator(".product__documentation a[href$='.pdf']").count() > 0, "Нет ссылки на тех. документацию (PDF)"

    # Документация
    desc = page.locator(".showhide.item_desc").first
    assert desc.is_visible(), "Блок описания не отображается"
    assert desc.text_content().strip() != "", "Описание товара отсутствует или пустое"

    # ТХ
    assert page.locator(".product__params-w").count() > 0, "Блок технической документации не найден"
    # Проверка наличия хотя бы одной ссылки на PDF-документ
    assert page.locator(".product__params").count() > 0, "Нет ТХ"

    # отображается ли наличие
    availability = page.locator(".item__avail").first
    assert availability.is_visible(), "Информация о наличии не отображается"
    assert availability.text_content().strip() != "", "Информация о наличии отсутствует или пустая"


def test_share(page):
    # товаром можно поделиться через вк
    page.goto("https://www.chipdip.ru/product/adm2481brwz")

    page.click(".ya-share2__icon_more")
    with page.context.expect_page() as vk_page_info:
        page.click("text=Вконтакте")
    vk_page = vk_page_info.value
    vk_page.wait_for_load_state()
    assert "vk" in vk_page.url
    vk_page.close()

    page.click(".ya-share2__icon_more")
    with page.context.expect_page() as ok_page_info:
        page.click("text=Одноклассники")
    ok_page = ok_page_info.value
    ok_page.wait_for_load_state()
    assert "ok" in ok_page.url
    ok_page.close()

    page.click(".ya-share2__icon_more")
    with page.context.expect_page() as telegram_page_info:
        page.click("text=Telegram")
    telegram_page = telegram_page_info.value
    # telegram_page.wait_for_load_state()
    assert "t.me" in telegram_page.url
    telegram_page.close()

    # page.wait_for_timeout(1000)
    # page.click(".ya-share2__icon_more")
    # with page.context.expect_page() as skype_page_info:
    #     page.click("text=Skype")
    # skype_page = skype_page_info.value
    # telegram_page.wait_for_load_state()
    # assert "skype" in skype_page.url
    # skype_page.close()

    page.click(".ya-share2__icon_more")
    with page.context.expect_page() as whatsapp_page_info:
        page.click("text=WhatsApp")
    whatsapp_page = whatsapp_page_info.value
    # whatsapp_page.wait_for_load_state()
    assert "whatsapp" in whatsapp_page.url
    whatsapp_page.close()

    page.click(".ya-share2__icon_more")
    with page.context.expect_page() as livejournal_page_info:
        page.click("text=LiveJournal")
    livejournal_page = livejournal_page_info.value
    # whatsapp_page.wait_for_load_state()
    assert "livejournal" in livejournal_page.url
    livejournal_page.close()

def test_price_filter(page):

    page.goto("https://www.chipdip.ru/catalog-show/scopemeters")
    page.click("text=Цена,")

    page.wait_for_timeout(1000)
    page.fill("#input_prices_min", "300")
    page.fill("#input_prices_max", "50000")
    page.wait_for_timeout(1000)

    page.click("button:has-text('Показать')")

    page.wait_for_timeout(1000)

    price_elements = page.locator(".price__value").all()
    for idx, element in enumerate(price_elements):

        raw_price = element.inner_text().replace(" ", "").replace(" ", "")
        price = int(raw_price)
        assert price <= 50000, f"Товар {idx + 1} превышает цену: {price} > {50000}"

def test_brand_filter(page):
    page.goto("https://www.chipdip.ru/catalog-show/scopemeters")

    # Найдём все чекбоксы брендов, исключим disabled
    checkboxes = page.query_selector_all('div.filter_selector_checkboxes input[type="checkbox"]')

    brands = []
    # Прожимаем первые 5
    for checkbox in checkboxes[:5]:
        checkbox.click(force=True)
        label = checkbox.evaluate_handle("node => node.closest('label')")
        brand_name = label.query_selector(".l-name").inner_text().strip()
        brands.append(brand_name)
    print(brands)
    page.wait_for_timeout(1000)
    page.click("button:has-text('Показать')")  # Или точный селектор, если нужен
    page.wait_for_timeout(5000)

    # проверяем товары что все имеют соответствующий бренд
    items = page.query_selector_all(".item")

    for idx, item in enumerate(items):
        # Находим элемент с названием бренда
        brand_elem = item.query_selector(".item__mnf")
        brand_name = brand_elem.inner_text().strip()
        assert brand_name in brands, f"Товар {idx + 1} с брендом '{brand_name}' не входит в выбранные бренды {brands}"

def test_sort_price(page):
    page.goto("https://www.chipdip.ru/catalog-show/scopemeters")

    # по убыванию
    page.click("text=Дороже")
    previous_price = 0
    price_elements = page.locator(".price__value").all()
    for idx, element in enumerate(price_elements):

        raw_price = element.inner_text().replace(" ", "").replace(" ", "")
        price = int(raw_price)
        print(price)
        assert price >= previous_price, f"Товар {idx + 1}  имеет цену: {price} > предыдущей цены {previous_price}"
    page.wait_for_timeout(1000)
    # по возрастанию
    page.click("text=Дешевле")


    previous_price = 100_000_000
    price_elements = page.locator(".price__value").all()
    for idx, element in enumerate(price_elements):

        raw_price = element.inner_text().replace(" ", "").replace(" ", "")
        price = int(raw_price)
        assert price <= previous_price, f"Товар {idx + 1}  имеет цену: {price} < предыдущей цены {previous_price}"

def test_sort_amount(page):
    page.goto("https://www.chipdip.ru/catalog-show/scopemeters")
    page.click("text=Количество")
    page.wait_for_timeout(1000)
    quantity_elements = page.query_selector_all(".item__avail .nw:last-child")
    # Извлекаем и обрабатываем значения
    previous_quantity = 10_000_000

    for idx, el in enumerate(quantity_elements):
        text = el.inner_text().replace("\xa0", "").replace(" ", "").strip()
        quantity = int(''.join(filter(str.isdigit, text)))
        assert quantity <= previous_quantity, f"Товар {idx + 1}  имеет количество: {quantity} < предыдущего количества {previous_quantity}"

def test_favourite(page):
    page.goto("https://www.chipdip.ru")
    page.click("text=Вход")
    page.fill("input[name='login']", "samplebuzz")
    page.fill("input[name='pwd']", "zx1235zx")
    page.click("button:has-text('Войти')")

    page.wait_for_timeout(1000)
    page.goto("https://www.chipdip.ru/product/lti-120-0.5l")
    page.click("button.add2fav")

    page.goto("https://www.chipdip.ru/product/skf-fksp-1l")
    page.click("button.add2fav")

    page.goto("https://www.chipdip.ru/product/sh-1.6-black")
    page.click("button.add2fav")

    page.goto("https://www.chipdip.ru/account")
    page.click("a.account-idx-item-favorites")

    page.click(".fav-sort-select-control")
    # page.wait_for_selector(".fav-sort-select-options")
    page.wait_for_timeout(1000)
    page.click('div.fav-sort-select-item[data-value="name"]')

    titles = page.query_selector_all('table#itemlist a.link')
    names = [title.inner_text().strip() for title in titles]
    assert names == sorted(names), "Товары не отсортированы"

    page.click("text=Очистить «Избранное»")
    page.click("#fancyConfirm_ok")






