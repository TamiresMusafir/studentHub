from playwright.sync_api import sync_playwright

user = ""
password = ""


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://alunos.cefet-rj.br/")

    page.locator("#j_username").fill(user)
    page.locator("#j_password").fill(password)

    page.locator('input[type="submit"]').click()

    page.locator('[original-title="Minhas Notas"]').wait_for()
    page.locator('[original-title="Minhas Notas"]').click()

    rows = page.locator("tbody tr")

    for row in rows.all():

        row.locator('a[title="Ver Notas"]').click()

        page.locator("#ui-dialog-title-dialog").wait_for()

        materia = page.locator("#ui-dialog-title-dialog").inner_text()
        print("Matéria: ", materia.strip())

        page.keyboard.press("Escape")
            
    input("Pressione ENTER para fechar...")
    browser.close()

    