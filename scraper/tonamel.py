from playwright.sync_api import sync_playwright
from config import *


# ==========================================
# 募集状態
# ==========================================

def classify_status(text):

    if "募集前" in text:
        return "募集前"

    if "募集中" in text or "開催中" in text:
        return "募集中"

    if "結果発表" in text:
        return "結果発表"

    return "その他"


# ==========================================
# オンライン・オフライン
# ==========================================

def classify_place(text):

    if "オンライン" in text:
        return "オンライン"

    return "オフライン"


# ==========================================
# シングル・ダブル
# ==========================================

def classify_battle(text):

    if "ダブルバトル" in text:
        return "ダブル"

    if "シングルバトル" in text:
        return "シングル"

    return "その他"


# ==========================================
# URL
# ==========================================

def make_url(href):

    if not href:
        return None

    if href.startswith("http"):
        return href

    return "https://tonamel.com" + href


# ==========================================
# 最後までスクロール
# ==========================================

def scroll_bottom(page):

    before = 0
    same = 0

    while True:

        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        page.wait_for_timeout(1500)

        now = page.evaluate(
            "document.body.scrollHeight"
        )

        if now == before:
            same += 1
        else:
            same = 0

        if same >= 3:
            break

        before = now


# ==========================================
# Pokemon Champions検索
# ==========================================

def search_game(page):

    search = page.get_by_role(
        "textbox",
        name="ゲーム名で検索"
    )

    search.wait_for(
        timeout=30000
    )

    search.click()

    search.fill(
        KEYWORD
    )

    game_button = page.get_by_role(
        "button",
        name="Pokémon Champions"
    )

    game_button.wait_for(
        timeout=30000
    )

    game_button.click()

    # 検索結果の更新を待つ
    page.wait_for_timeout(
        10000
    )


# ==========================================
# ブラウザ起動
# ==========================================

def open_browser():

    p = sync_playwright().start()

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )

    context = browser.new_context(
        viewport={
            "width": 1920,
            "height": 1080
        }
    )

    page = context.new_page()

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    return p, browser, context, page


# ==========================================
# 大会カード取得
# ==========================================

def get_cards(page):

    cards = []
    used = set()

    # 大会一覧が読み込まれるまで待機
    try:

        page.wait_for_selector(
            "a[href*='/competition/']",
            timeout=30000
        )

    except Exception:

        return cards


    locators = page.locator(
        "a[href*='/competition/']"
    )

    count = locators.count()

    for i in range(count):

        try:

            card = locators.nth(i)

            href = card.get_attribute(
                "href"
            )

            url = make_url(
                href
            )

            if not url:
                continue

            if url in used:
                continue

            used.add(url)

            title = card.inner_text().strip()

            if not title:
                continue

            texts = card.locator(
                "*"
            ).all_inner_texts()

            card_text = "\n".join(
                texts
            )

            cards.append({

                "title": title,

                "url": url,

                "card_text": card_text

            })

        except Exception:

            continue

    return cards


# ==========================================
# 詳細ページ全文取得
# ==========================================

def get_detail(context, url):

    page = context.new_page()

    try:

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(
            1500
        )

        text = page.locator(
            "body"
        ).inner_text()

    except Exception:

        text = ""

    finally:

        page.close()

    return text


# ==========================================
# カード解析
# ==========================================

def analyze_card(context, card):

    title = card["title"]
    url = card["url"]
    card_text = card["card_text"]

    status = classify_status(
        card_text
    )

    place = classify_place(
        card_text
    )

    detail_text = get_detail(
        context,
        url
    )

    battle = classify_battle(
        detail_text
    )

    return {

        "title": title,

        "url": url,

        "status": status,

        "place": place,

        "battle": battle

    }


# ==========================================
# 全大会解析
# ==========================================

def analyze_all(context, cards):

    results = []

    for card in cards:

        try:

            data = analyze_card(
                context,
                card
            )

            results.append(
                data
            )

        except Exception:

            continue

    return results


# ==========================================
# メイン
# ==========================================

def scrape():

    results = {

        "募集前": [],
        "募集中": [],
        "結果発表": [],
        "その他": [],
        "オンライン": [],
        "オフライン": [],
        "シングル": [],
        "ダブル": []

    }

    p = None
    browser = None
    context = None

    try:

        p, browser, context, page = open_browser()

        search_game(
            page
        )

        scroll_bottom(
            page
        )

        cards = get_cards(
            page
        )

        datas = analyze_all(
            context,
            cards
        )

        for data in datas:

            title = data["title"]
            url = data["url"]
            status = data["status"]
            place = data["place"]
            battle = data["battle"]

            results[status].append(
                (title, url)
            )

            results[place].append(
                (title, url)
            )

            if battle != "その他":

                results[battle].append(
                    (title, url)
                )

        return results

    finally:

        if context is not None:
            context.close()

        if browser is not None:
            browser.close()

        if p is not None:
            p.stop()