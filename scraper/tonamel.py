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
# オンライン
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

        page.wait_for_timeout(1200)

        now = page.evaluate(
            "document.body.scrollHeight"
        )

        print(
            f"現在のページ高さ: {now}",
            flush=True
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

    print(
        "ゲーム検索開始",
        flush=True
    )

    search = page.get_by_role(
        "textbox",
        name="ゲーム名で検索"
    )

    search.wait_for(
        timeout=30000
    )

    search.click()

    print(
        f"検索ワード入力: {KEYWORD}",
        flush=True
    )

    search.fill(
        KEYWORD
    )

    # Pokémon Championsの候補を待つ
    game_button = page.get_by_role(
        "button",
        name="Pokémon Champions"
    )

    game_button.wait_for(
        timeout=30000
    )

    print(
        "Pokemon Champions候補を発見",
        flush=True
    )

    game_button.click()

    print(
        "Pokemon Champions選択完了",
        flush=True
    )

    # ページの大会一覧が読み込まれるのを待つ
    page.wait_for_timeout(5000)

    print(
        "検索結果読み込み待機完了",
        flush=True
    )


# ==========================================
# ブラウザ起動
# ==========================================

def open_browser():

    print(
        "Playwright起動",
        flush=True
    )

    p = sync_playwright().start()

    print(
        "Chromium起動",
        flush=True
    )

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

    print(
        f"ページ移動: {URL}",
        flush=True
    )

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print(
        "ページ移動完了",
        flush=True
    )

    return p, browser, context, page


# ==========================================
# 大会カード取得
# ==========================================

def get_cards(page):

    print(
        "大会一覧取得開始",
        flush=True
    )

    cards = []

    used = set()

    # 大会リンクが出現するまで少し待つ
    try:

        page.wait_for_selector(
            "a[href*='/competition/']",
            timeout=15000
        )

        print(
            "大会リンクを検出",
            flush=True
        )

    except Exception:

        print(
            "大会リンクの待機時間が終了しました",
            flush=True
        )


    locators = page.locator(
        "a[href*='/competition/']"
    )

    count = locators.count()

    print(
        f"{count}件検出",
        flush=True
    )

    for i in range(count):

        try:

            card = locators.nth(i)

            href = card.get_attribute(
                "href"
            )

            if not href:

                continue

            url = make_url(
                href
            )

            if url in used:

                continue

            used.add(
                url
            )

            title = card.inner_text().strip()

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

        except Exception as e:

            print(
                f"カード取得エラー: {e}",
                flush=True
            )

            continue


    print(
        f"{len(cards)}件取得完了",
        flush=True
    )

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

    except Exception as e:

        print(
            f"詳細取得エラー: {url} / {e}",
            flush=True
        )

        text = ""

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

    total = len(
        cards
    )

    for index, card in enumerate(
        cards,
        1
    ):

        print(
            f"[{index}/{total}] {card['title']}",
            flush=True
        )

        try:

            data = analyze_card(
                context,
                card
            )

            results.append(
                data
            )

        except Exception as e:

            print(
                f"解析エラー: {e}",
                flush=True
            )

    return results


# ==========================================
# メイン
# ==========================================

def scrape():

    print(
        "========== スクレイピング開始 ==========",
        flush=True
    )

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


        print(
            "スクロール開始",
            flush=True
        )

        scroll_bottom(
            page
        )


        cards = get_cards(
            page
        )


        print(
            f"取得カード数: {len(cards)}",
            flush=True
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


        print(
            "========== 完了 ==========",
            flush=True
        )


        for category, events in results.items():

            print(
                f"{category}: {len(events)}件",
                flush=True
            )


        return results


    except Exception as e:

        print(
            f"スクレイピング全体エラー: {e}",
            flush=True
        )

        raise


    finally:

        if context is not None:

            context.close()

        if browser is not None:

            browser.close()

        if p is not None:

            p.stop()