from pathlib import Path

# DIRS
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_PATH = str(BASE_DIR / "storage.json")
OPTION_LINKS_PATH = str(BASE_DIR / "storage" / "option_links.json")
OPTION_PATH = str(BASE_DIR / "storage" / "option.json")

# REQUESTS
BASE_HEADERS = {"User-Agent": "PostmanRuntime/7.28.2"}
# LINKS
APPLICANT_URL = "https://www.dvfu.ru/bitrix/services/main/ajax.php?mode=class&c=dvfu:admission.spd&action=getStudents"

