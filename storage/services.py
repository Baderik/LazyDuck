from requests import get, post
from json import load
from json.decoder import JSONDecodeError
from pydantic.error_wrappers import ValidationError

from sys import path

path.append("../")

from storage.settings import OPTION_PATH, OPTION_LINKS_PATH, APPLICANT_URL, BASE_HEADERS, STORAGE_PATH, BEAUTIFUL_JSON
from storage.models import Option, ApplicantStorage, BaseApplicant


def init_option_storage() -> Option:
    data = Option(type="Storage", data=APPLICANT_URL)

    with open(OPTION_LINKS_PATH, "r", encoding="utf-8-sig") as inp:
        option_links = load(inp)

    def _parse_option(order_i: int, option: Option, form=None):
        if form is None:
            form = {}
        if len(option_links["order"]) <= order_i:
            return

        link_key = option_links["order"][order_i]
        link = option_links[link_key]
        if order_i:
            options = request_get_options("post", link, data=form)
        else:
            options = request_get_options("get", link)
        for option_text in options:
            option.next.append(Option(type=link_key, data=option_text))

        for child in option.next:
            form[link_key] = child.data
            _parse_option(order_i + 1, child, form)

    _parse_option(0, data)

    with open(OPTION_PATH, "w", encoding="utf-8") as out:
        if BEAUTIFUL_JSON:
            print(data.json(indent=4, ensure_ascii=False), file=out)
        else:
            print(data.json(), file=out)

    return data


def open_option_storage() -> Option:
    if OPTION_PATH.is_file():
        o_storage = Option.parse_file(OPTION_PATH)
        o_storage.parse_next(True)
        return o_storage

    return init_option_storage()


def request_get_options(type_r: str, url: str, *args, **kwargs) -> list:
    print(type_r, url)
    if type_r == "get":
        response = get(url, headers=BASE_HEADERS, *args, **kwargs)
    elif type_r == "post":
        response = post(url, headers=BASE_HEADERS, *args, **kwargs)
    else:
        print("ERROR wrong type of request")
        return []

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


def open_applicant_storage() -> ApplicantStorage:
    if STORAGE_PATH.is_file():
        a_storage = ApplicantStorage.parse_file(STORAGE_PATH)
        a_storage.parse_next(True)
        return a_storage
    return ApplicantStorage()


def request_get_table(url: str, *args, **kwargs) -> list:
    print("post", url)
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


def update_storage():
    print("Updating storage")
    a_storage: ApplicantStorage = open_applicant_storage()

    def assembling_links(option: Option, data=None) -> None:
        if data is None:
            data = {"consent": False}
        data[option.type] = option.data
        if option.type == "trainingDirection":
            print(data)
            result: list = request_get_table(data["Storage"], data=data)
            if not result:
                print("Error Empty table")
                return

            for el_i in range(len(result)):
                try:
                    result[el_i] = BaseApplicant.parse_obj(result[el_i])
                except ValidationError as e:
                    print(result[el_i])
                    raise e

            # result: List[BaseApplicant] = list(map(BaseApplicant.parse_obj, result))
            td = result[0].trainingDirection.split()
            td_code = td[0]
            td_name = " ".join(td[1:])
            education_direction = a_storage.get_education_direction(
                admission_campaign_type=result[0].admissionCampaignType,
                study_form=result[0].studyForm,
                td_code=td_code, td_name=td_name)
            education_direction.update(result)
            education_direction.update_service_information(result[0])
        else:
            for child in option.next:
                assembling_links(child, data)

    o_storage = open_option_storage()
    assembling_links(o_storage)
    print("update start")
    a_storage.update_student_names(True)
    print("update end")

    with open(STORAGE_PATH, "w", encoding="utf-8") as out:
        if BEAUTIFUL_JSON:
            print(a_storage.json(indent=4, ensure_ascii=False), file=out)
        else:
            print(a_storage.json(), file=out)


def find_applicant(name: str, fast: bool = True) -> str:
    if not fast:
        update_storage()
    a_storage = open_applicant_storage()
    if a_storage.is_empty():
        print("Storage is empty")
        update_storage()
        a_storage = open_applicant_storage()
    res = a_storage.find_applicant(name)
    return "\n".join(map(str, res))

