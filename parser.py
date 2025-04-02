import os

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def save_page_content(page, page_number, page_dir):
    """Сохраняет содержимое страницы в файл"""
    html_content = page.content()
    output_file = Path(f"{page_dir}/page_{page_number}.html")
    output_file.write_text(html_content, encoding="utf-8")
    logging.info(f"Страница {page_number} сохранена в: {output_file}")


def process_pagination(page, page_dir):
    """Обрабатывает пагинацию и сохраняет все страницы"""
    page_number = 1

    while True:
        # Сохраняем текущую страницу
        save_page_content(page, page_number, page_dir)

        # Пытаемся найти активную кнопку "Следующая страница"
        try:
            next_button = page.wait_for_selector(
                '[title="Следующая страница"]:not([disabled])',
                state="visible",
                timeout=5000
            )

            # Человекоподобное взаимодействие
            next_button.scroll_into_view_if_needed()
            next_button.click(delay=150)

            # Ожидание обновления контента
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            page_number += 1

        except Exception as e:
            logging.info("Достигнута последняя страница или кнопка не найдена")
            break


def accept_consent_and_process_pages(url, page_dir):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # Загрузка страницы
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Обработка согласия
            consent_selectors = [
                'a:has-text("Согласен")',
                'button:has-text("Согласен")',
                '//*[contains(text(), "Согласен")]'
            ]

            for selector in consent_selectors:
                try:
                    element = page.wait_for_selector(selector, timeout=10000)
                    element.scroll_into_view_if_needed()
                    element.click(delay=100)
                    time.sleep(2)
                    break
                except:
                    continue

            # Обработка пагинации
            process_pagination(page, page_dir)

            return True

        except Exception as e:
            logging.error(f"Ошибка: {str(e)}")
            page.screenshot(path="error.png")
            return False
        finally:
            browser.close()


def load_all_pages_from_url(url, pages_dir):
    # url = "https://www.moex.com/ru/marketdata/#/mode=instrument&secid=TMOS&boardgroupid=57&mode_type=history&date_from=2020-08-26&date_till=2025-03-28"
    if not os.path.isdir(pages_dir):
        os.mkdir(pages_dir)
    if accept_consent_and_process_pages(url, pages_dir):
        logging.info("Все страницы успешно сохранены!")
    else:
        logging.error("Выполнение завершено с ошибками")
