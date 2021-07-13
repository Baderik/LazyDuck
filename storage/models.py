from datetime import datetime
from pydantic import BaseModel, Field, validator
from json import loads
from typing import List, Set


class ApplicantResult(BaseModel):
    text: str
    position: int
    quota: int


class IntermediateResult(BaseModel):
    text: str
    next: list = Field(default_factory=list)


class Applicant(BaseModel):
    id: int
    name: str
    examinationsless: bool
    preemptiveRight: bool
    consent: bool
    enrolled: int
    test1score: int
    test2score: int
    test3score: int
    test4score: int = Field(default=0, ge=0, le=100)
    ordinaturePriority: float
    personal: int
    scoreSum: int

    def __lt__(self, other) -> bool:
        if self.examinationsless:
            if other.examinationsless:
                return self.scoreSum < other.scoreSum
            return False

        elif other.examinationsless:
            return True
        return self.scoreSum < other.scoreSum

    def __bool__(self) -> bool:
        return True


class BaseApplicant(BaseModel):
    id: int
    name: str
    date: datetime
    admissionCampaignType: str
    financingSource: str
    studyForm: str
    implementationPlace: str
    trainingDirection: str
    category: str
    examinationsless: bool
    preemptiveRight: bool
    consent: bool
    base: str
    enrolled: int
    test1: str
    test1score: int
    test2: str
    test2score: int
    test3: str
    test3score: int
    test4: str = Field(default="")
    test4score: int = Field(default=0)
    ordinaturePriority: float
    personal: int
    scoreSum: int
    scoreAvg: int
    bm: int
    cq: int
    oq: int
    dm: int

    def compress(self) -> Applicant:
        return Applicant.parse_obj(self)

    @validator("examinationsless", "preemptiveRight", "consent", pre=True)
    def normalizing_bool(cls, value):
        if isinstance(value, str):
            if value == "+":
                return 1
            elif value == "-":
                return 0
        return value

    @validator("enrolled", "test1score", "test2score", "test3score", "test4score", "personal", "scoreSum", "scoreAvg", pre=True)
    def normalizing_int(cls, value):
        try:
            return int(value)
        except ValueError:
            return 0

    @validator("*", pre=True)
    def remove_none(cls, value):
        if value is None:
            return ""
        return value


class EducationDirection(BaseModel):
    code: str
    name: str
    datetime_update: datetime = Field(default_factory=lambda: datetime(1, 1, 1))
    budget_quota: int = Field(0, ge=0)
    company_quota: int = Field(0, ge=0)
    special_quota: int = Field(0, ge=0)
    finance_quota: int = Field(0, ge=0)
    budget_list: List[Applicant] = Field(default_factory=list)
    company_list: List[Applicant] = Field(default_factory=list)
    special_list: List[Applicant] = Field(default_factory=list)
    finance_list: List[Applicant] = Field(default_factory=list)
    student_names: Set[str] = Field(default_factory=set)

    def find_applicant(self, name: str) -> IntermediateResult:
        result: IntermediateResult = IntermediateResult(text=self.name)

        args = ((self.budget_list, "На общих основаниях", self.budget_quota),
                (self.company_list, "Целевой приём", self.company_quota),
                (self.special_list, "Особая квота", self.special_quota),
                (self.finance_list, "Полное возмещение затрат", self.finance_quota))
        for arg in args:
            if res := _search_in_applicant_list(name, *arg):
                result.next.append(res)

        return result

    def update(self, applicants: List[BaseApplicant]) -> None:
        if not applicants:
            print("LOG ed did not update")
            return

        list_updated = {"На общих основаниях": self.budget_list,
                        "Без вступительных испытаний": self.budget_list,
                        "Имеющие особое право": self.special_list,
                        "Целевой прием": self.company_list,
                        "Полное возмещение затрат": self.finance_list}
        is_updated = {"На общих основаниях": False,
                      "Без вступительных испытаний": False,
                      "Имеющие особое право": False,
                      "Целевой прием": False,
                      "Полное возмещение затрат": False}
        for applicant in applicants:
            if applicant.financingSource == "Бюджетная основа":
                type_applicant = applicant.category
            else:
                type_applicant = applicant.financingSource

            if not is_updated[type_applicant]:
                list_updated[type_applicant].clear()
                is_updated[type_applicant] = True
            list_updated[type_applicant].append(applicant.compress())

        for key, value in is_updated.items():
            if value:
                list_updated[key].sort(reverse=True)

    def update_service_information(self, b_applicant: BaseApplicant) -> None:
        self.datetime_update = b_applicant.date
        self.budget_quota = b_applicant.bm
        self.finance_quota = b_applicant.dm
        self.special_quota = b_applicant.oq
        self.company_quota = b_applicant.cq


class Intermediate(BaseModel):
    name: str
    stage: str
    next: list = Field(default_factory=list)
    next_keys: dict = Field(default_factory=dict)
    student_names: Set[str] = Field(default_factory=set)

    def add(self, element) -> None:
        if element.name in self.next_keys:
            print("Такой уже есть Inter", element.name)
            return

        self.next_keys[element.name] = len(self.next)
        self.next.append(element)

    def get_by_name(self, name: str):
        key = self.next_keys.get(name, None)
        if key is None:
            return
        return self.next[key]

    def parse_next(self, recursive=False) -> None:
        for i in range(len(self.next)):
            if self.next[i].get("stage", None):
                self.next[i]: Intermediate = Intermediate.parse_obj(self.next[i])

                if recursive:
                    self.next[i].parse_next(True)
            else:
                self.next[i] = EducationDirection.parse_obj(self.next[i])

    def find_applicant(self, name: str) -> IntermediateResult:
        result: IntermediateResult = IntermediateResult(text=self.name)
        for child in self.next:
            if name in child.student_names:
                result.next.append(child.find_applicant(name))

        return result

    def update_student_names(self, recursive: bool = False):
        self.student_name: set = set()

        for child in self.next:
            if recursive:
                if type(child) is Intermediate:
                    child.update_student_names(recursive)
            self.student_names |= child.student_names


class ApplicantStorage(BaseModel):
    admissions: List[Intermediate] = Field(default_factory=list)
    admission_keys: dict = Field(default_factory=dict)

    def get_education_direction(self,
                                admission_campaign_type: str,
                                study_form: str,
                                td_code: str,
                                td_name: str) -> EducationDirection:
        admission_c_t = self.get_by_name(admission_campaign_type)
        if admission_c_t is None:
            admission_c_t = Intermediate(name=admission_campaign_type, stage="admissionCampaignType")
            self.add(admission_c_t)

        study_f = admission_c_t.get_by_name(study_form)
        if study_f is None:
            study_f = Intermediate(name=study_form, stage="studyForm")
            admission_c_t.add(study_f)

        e_d_i = study_f.next_keys.get(td_name, None)
        if e_d_i is None:
            study_f.add(EducationDirection(name=td_name, code=td_code))
            return study_f.next[-1]
        return study_f.next[e_d_i]

    def add(self, element) -> None:
        if element.name in self.admission_keys:
            print("Такой уже есть Storage")
            return

        self.admission_keys[element.name] = len(self.admissions)
        self.admissions.append(element)

    def find_applicant(self, name: str) -> List[IntermediateResult]:
        result: List[IntermediateResult] = []
        for intermediate in self.admissions:
            if name in intermediate.student_names:
                result += intermediate.find_applicant(name)

        return result

    def get_by_name(self, name: str):
        key = self.admission_keys.get(name, None)
        if key is None:
            return
        return self.admissions[key]

    def parse_next(self, recursive=False):
        for admission in self.admissions:
            admission.parse_next(recursive)


def _search_in_applicant_list(name: str, applicants: List[Applicant], text: str, quota: int):
    for applicant_i in range(len(applicants)):
        if name == applicants[applicant_i].name:
            return ApplicantResult(text=text, position=applicant_i + 1, quota=quota)


class Option(BaseModel):
    data: str
    type: str
    next: list = Field(default_factory=list)

    def parse_next(self, recursive=False):
        for i in range(len(self.next)):
            self.next[i]: Option = Option.parse_obj(self.next[i])

            if recursive:
                self.next[i].parse_next(True)
