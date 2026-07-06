from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

user = ""
password = ""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://alunos.cefet-rj.br/")

    page.locator("#j_username").fill(user)
    page.locator("#j_password").fill(password)
    page.locator('input[type="submit"]').click()

    page.locator('[original-title="Minhas Notas"]').click()

    page.locator('table.table-turmas tbody > tr').first.wait_for()

    # Apenas as linhas das disciplinas
    rows = page.locator("table.table-turmas tbody > tr")

    for i in range(rows.count()):

        row = rows.nth(i)

        # Nome da disciplina
        materia = row.locator("td").nth(0).inner_text().split("(")[0].strip()

        # Link do botão "Ver Notas" dessa disciplina
        href = row.locator('a[title="Ver Notas"]').get_attribute("href")

        if not href:
            continue

        # Extrai a URL do loadDialog(...)
        match = re.search(r"'([^']+)'", href)
        if not match:
            continue

        url = match.group(1)

        # Requisição do conteúdo do modal
        response = page.request.get(
            "https://alunos.cefet-rj.br" + url
        )

        soup = BeautifulSoup(response.text(), "html.parser")

        nota1 = "-"
        nota2 = "-"
        media = "-"
        exame = "-"
        media_final = "-"
        faltas = "-"
        situacao = "Sem notas"

        tabela = soup.find("table", class_="nota")

        if tabela:

            linha = tabela.find("tbody").find("tr")
            colunas = linha.find_all("td", recursive=False)

            # Nota 1
            valores = [
                div.get_text(strip=True)
                for div in colunas[0].find_all("div")
                if div.get_text(strip=True)
            ]

            if len(valores) >= 2:
                nota1 = valores[1]
            elif len(valores) == 1:
                nota1 = valores[0]

            # Nota 2
            valores = [
                div.get_text(strip=True)
                for div in colunas[1].find_all("div")
                if div.get_text(strip=True)
            ]

            if len(valores) >= 2:
                nota2 = valores[1]
            elif len(valores) == 1:
                nota2 = valores[0]

            # Média / Exame / Média Final
            valores = [
                div.get_text(strip=True)
                for div in colunas[2].find_all("div")
                if div.get_text(strip=True)
            ]

            if len(valores) >= 1:
                media = valores[0]

            if len(valores) >= 2:
                exame = valores[1] if valores[1] else "-"

            if len(valores) >= 3:
                media_final = valores[2]

        # Situação / Média Final / Faltas
        info = soup.find("div", class_="divInfo")

        if info:

            blocos = info.find_all("div", recursive=False)

            if len(blocos) >= 2:

                dados = [
                    div.get_text(strip=True)
                    for div in blocos[1].find_all("div", recursive=False)
                ]

                if len(dados) >= 3:
                    situacao = dados[0]
                    media_final = dados[1]
                    faltas = dados[2]

        print("=" * 60)
        print(f"Matéria     : {materia}")
        print(f"Nota 1      : {nota1}")
        print(f"Nota 2      : {nota2}")
        print(f"Média       : {media}")
        print(f"Exame       : {exame}")
        print(f"Média Final : {media_final}")
        print(f"Faltas      : {faltas}")
        print(f"Situação    : {situacao}")

    input("\nPressione ENTER para fechar...")
    browser.close()