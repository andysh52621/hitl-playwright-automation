import time


def highlight(locator):
    locator.wait_for(state="visible", timeout=60000)
    locator.evaluate("element => element.scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' })")
    locator.evaluate("element => element.setAttribute('style', 'border: 4px solid orange;')")
    time.sleep(0.2)
    locator.evaluate("element => element.setAttribute('style', 'border: 5px solid red;')")
    time.sleep(0.1)
    locator.evaluate("element => element.setAttribute('style', 'border: none;')")
    time.sleep(0.2)
