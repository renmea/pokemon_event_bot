from scraper.tonamel import scrape


def run():

    results = scrape()

    count = sum(
        len(x)
        for x in results.values()
    )

    return results, count


if __name__ == "__main__":

    results, count = run()

    print(
        f"{count}件見つかりました"
    )