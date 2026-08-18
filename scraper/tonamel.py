from playwright.sync_api import sync_playwright
from config import *

import time


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

    return "https://tonamel.com"+href


# ==========================================
# 最後までスクロール
# ==========================================

def scroll_bottom(page):

    before=0
    same=0

    while True:

        page.evaluate(
            "window.scrollTo(0,document.body.scrollHeight)"
        )

        page.wait_for_timeout(1200)

        now=page.evaluate(
            "document.body.scrollHeight"
        )

        if now==before:

            same+=1

        else:

            same=0

        if same>=3:

            break

        before=now


# ==========================================
# Pokemon Champions検索
# ==========================================

def search_game(page):

    print("ゲーム検索")

    search = page.get_by_role(
        "textbox",
        name="ゲーム名で検索"
    )

    search.click()

    search.fill(
        KEYWORD
    )

    # 候補が出るまで待機
    page.get_by_role(
        "button",
        name="Pokémon Champions"
    ).wait_for(
        timeout=10000
    )

    # 候補クリック
    page.get_by_role(
        "button",
        name="Pokémon Champions"
    ).click()

    print("Pokemon Champions選択完了")

    page.wait_for_timeout(2000)


# ==========================================
# ブラウザ起動
# ==========================================

def open_browser():

    p=sync_playwright().start()

    browser=p.chromium.launch(
        headless=HEADLESS
    )

    context=browser.new_context()

    page=context.new_page()

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    return p,browser,context,page

# ==========================================
# 大会カード取得
# ==========================================

def get_cards(page):

    print("大会一覧取得")

    cards=[]

    used=set()

    locators=page.locator(
        "a[href*='/competition/']"
    )

    count=locators.count()

    print(f"{count}件検出")

    for i in range(count):

        try:

            card=locators.nth(i)

            href=card.get_attribute("href")

            if not href:
                continue

            url=make_url(href)

            if url in used:
                continue

            used.add(url)

            title=card.inner_text().strip()

            texts=card.locator("*").all_inner_texts()

            card_text="\n".join(texts)

            cards.append({

                "title":title,

                "url":url,

                "card_text":card_text

            })

        except Exception:

            continue

    print(f"{len(cards)}件取得")

    return cards


# ==========================================
# 詳細ページ全文取得
# ==========================================

def get_detail(context,url):

    page=context.new_page()

    try:

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(1500)

        text=page.locator(
            "body"
        ).inner_text()

    except Exception:

        text=""

    page.close()

    return text


# ==========================================
# カード解析
# ==========================================

def analyze_card(context,card):

    title=card["title"]

    url=card["url"]

    card_text=card["card_text"]


    status=classify_status(
        card_text
    )


    place=classify_place(
        card_text
    )


    detail_text=get_detail(
        context,
        url
    )


    battle=classify_battle(
        detail_text
    )


    return {

        "title":title,

        "url":url,

        "status":status,

        "place":place,

        "battle":battle

    }


# ==========================================
# 全大会解析
# ==========================================

def analyze_all(context,cards):

    results=[]

    total=len(cards)

    for index,card in enumerate(cards,1):

        print(

            f"[{index}/{total}]",

            card["title"]

        )

        try:

            data=analyze_card(

                context,

                card

            )

            results.append(data)

        except Exception as e:

            print(e)

    return results

# ==========================================
# メイン
# ==========================================

def scrape():

    results={

        "募集前":[],

        "募集中":[],

        "結果発表":[],

        "その他":[],

        "オンライン":[],

        "オフライン":[],

        "シングル":[],

        "ダブル":[]

    }

    p,browser,context,page=open_browser()

    try:

        print("ゲーム検索開始")

        search_game(page)

        print("スクロール")

        scroll_bottom(page)

        cards=get_cards(page)

        print(f"{len(cards)}件取得")

        datas=analyze_all(

            context,

            cards

        )

        for data in datas:

            title=data["title"]

            url=data["url"]

            status=data["status"]

            place=data["place"]

            battle=data["battle"]

            results[status].append(

                (title,url)

            )

            results[place].append(

                (title,url)

            )

            if battle!="その他":

                results[battle].append(

                    (title,url)

                )

        print()

        print("========== 完了 ==========")

        print()

        print(

            "募集前",

            len(results["募集前"])

        )

        print(

            "募集中",

            len(results["募集中"])

        )

        print(

            "結果発表",

            len(results["結果発表"])

        )

        print(

            "その他",

            len(results["その他"])

        )

        print()

        print(

            "オンライン",

            len(results["オンライン"])

        )

        print(

            "オフライン",

            len(results["オフライン"])

        )

        print()

        print(

            "シングル",

            len(results["シングル"])

        )

        print(

            "ダブル",

            len(results["ダブル"])

        )

        return results

    finally:

        context.close()

        browser.close()

        p.stop()

