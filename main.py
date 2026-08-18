from scraper.tonamel import scrape
from ui.viewer import show
from notify.notify import send

results=scrape()

count=sum(

    len(x)

    for x in results.values()

)

send(
    f"{count}件見つかりました"
)

show(
    results
)