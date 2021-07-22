from requests import get, post
from json import load
from json.decoder import JSONDecodeError
from pydantic.error_wrappers import ValidationError
from loguru import logger

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


def _processing_fefu_response(response):
    logger.debug(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logger.error(response.text)
        return []

    try:
        result: dict = response.json()

    except JSONDecodeError:
        logger.exception("Wrong json")
        return []

    logger.debug(f"Response status: {result['status']}")
    if result["status"] != "success":
        logger.error(result)
        return []
    return result["data"]


def request_get_options(type_r: str, url: str, *args, **kwargs) -> list:
    logger.debug(f"{type_r} {url}")
    if type_r == "get":
        response = get(url, headers=BASE_HEADERS, *args, **kwargs)
    elif type_r == "post":
        response = post(url, headers=BASE_HEADERS, *args, **kwargs)
    else:
        logger.error("Wrong type of request")
        return []

    return _processing_fefu_response(response)


def open_applicant_storage() -> ApplicantStorage:
    if STORAGE_PATH.is_file():
        a_storage = ApplicantStorage.parse_file(STORAGE_PATH)
        a_storage.parse_next(True)
        return a_storage
    return ApplicantStorage()


def request_get_table(url: str, *args, **kwargs) -> list:
    logger.debug(f"Send post request {url}")
    response = post(url, headers=BASE_HEADERS, *args, **kwargs)
    return _processing_fefu_response(response)


def update_storage():
    logger.info("Update storage start")
    a_storage: ApplicantStorage = open_applicant_storage()

    def assembling_links(option: Option, data=None) -> None:
        if data is None:
            data = {"consent": False}
        data[option.type] = option.data
        if option.type == "trainingDirection":
            logger.debug(data)
            result: list = request_get_table(data["Storage"], data=data)
            if not result:
                logger.debug("Table is empty")
                return

            for el_i in range(len(result)):
                try:
                    result[el_i] = BaseApplicant.parse_obj(result[el_i])
                except ValidationError:
                    logger.exception("Is not a BaseApplicant")

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
    a_storage.update_student_names(True)

    with open(STORAGE_PATH, "w", encoding="utf-8") as out:
        if BEAUTIFUL_JSON:
            print(a_storage.json(indent=4, ensure_ascii=False), file=out)
        else:
            print(a_storage.json(), file=out)

    logger.info("Update storage finish")


def find_applicant(name: str, fast: bool = True, multi: bool = True) -> str:
    if not fast:
        update_storage()
    a_storage = open_applicant_storage()
    if a_storage.is_empty():
        logger.debug("Storage is empty")
        if multi:
            return "Хранилище обновляется, попробуйте позже"
        update_storage()
        a_storage = open_applicant_storage()
    res = a_storage.find_applicant(name)
    return "\n".join(map(str, res))

