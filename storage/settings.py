from pathlib import Path

# DIRS
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_PATH = BASE_DIR / "storage" / "storage.json"
OPTION_LINKS_PATH = str(BASE_DIR / "storage" / "option_links.json")
OPTION_PATH = BASE_DIR / "storage" / "option.json"
LOGURU_DIR = BASE_DIR / "storage" / "logs"
LOGURU_PATH = LOGURU_DIR / "updater.log"

# REQUESTS
BASE_HEADERS = {"User-Agent": "PostmanRuntime/7.28.2"}
# LINKS
APPLICANT_URL = "https://www.dvfu.ru/bitrix/services/main/ajax.php?mode=class&c=dvfu:admission.spd&action=getStudents"

# CONST
BEAUTIFUL_JSON = True
