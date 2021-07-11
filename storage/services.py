from requests import get, post
from json import load
from json.decoder import JSONDecodeError

from sys import path

path.append("../")

from storage.settings import OPTION_PATH, OPTION_LINKS_PATH, APPLICATION_URL, BASE_HEADERS
from storage.models import Option


def init_option_storage():
    data = Option(type="Storage", data=APPLICATION_URL)

    with open(OPTION_LINKS_PATH, "r", encoding="utf-8-sig") as inp:
        option_links = load(inp)

    def _parse_option(order_i: int, option: Option, form={}):
        if len(option_links["order"]) <= order_i:
            return

        link_key = option_links["order"][order_i]
        link = option_links[link_key]
        if order_i:
            options = get_options("post", link, data=form)
        else:
            options = get_options("get", link)
        for option_text in options:
            option.next.append(Option(type=link_key, data=option_text))

        for child in option.next:
            form[link_key] = child.data
            _parse_option(order_i + 1, child, form)

    _parse_option(0, data)

    with open(OPTION_PATH, "w", encoding="utf-8") as out:
        print(data.json(indent=4, ensure_ascii=False), file=out)


def get_options(type_r: str, url: str, *args, **kwargs) -> list:
    print(type_r, url)
    if type_r == "get":
        response = get(url, headers=BASE_HEADERS, *args, **kwargs)
    elif type_r == "post":
        response = post(url, headers=BASE_HEADERS, *args, **kwargs)

    if response.status_code != 200:
        print("ERROR", response.status_code)
        print(response.text)
        return []

    try:
        result: dict = response.json()

    except JSONDecodeError as e:
        print("ERROR", e)
        return []

    if result["status"] != "success":
        print("ERROR", result)
        return []
    print("200")
    return result["data"]


if __name__ == '__main__':
    init_option_storage()
    # get_options("https://www.dvfu.ru/bitrix/services/main/ajax.php?mode=class&c=dvfu:admission.spd&action=getAdmissionCampaignTypeList")
