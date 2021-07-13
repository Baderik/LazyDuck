from datetime import datetime
from pydantic import BaseModel, Field
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


class EducationDirection(BaseModel):
    code: str
    name: str
    datetime_update: datetime = Field(default_factory=datetime.now)
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
            if res := _search_in_application_list(name, *arg):
                result.next.append(res)

        return result

    def update(self, applicants: List[BaseApplicant]) -> None:
        if not applicants:
            print("LOG ed did not update")
            return

        list_updated = {"На общих основаниях": self.budget_list,
                        "Имеющие особое право": self.special_list,
                        "Целевой прием": self.company_list,
                        "Полное возмещение затрат": self.finance_list}
        is_updated = {"На общих основаниях": False,
                      "Имеющие особое право": False,
                      "Целевой прием": False,
                      "Полное возмещение затрат": False}
        for applicant in applicants:
            if applicant.financingSource == "Бюджетная основа":
                type_applicant = applicant.category
            else:
                type_applicant = applicant.financingSource

            if not is_updated[type_applicant]:
                list_updated[type_applicant] = type_applicant
                is_updated[type_applicant] = True

            list_updated[type_applicant].append(applicant.compress())


class Intermediate(BaseModel):
    name: str
    stage: str
    next: list = Field(default_factory=list)
    next_keys: dict = Field(default_factory=dict)
    student_names: Set[str] = Field(default_factory=set)

    def add(self, element) -> None:
        if element.name in self.next_keys:
            print("Такой уже есть")
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
                                td_name: str) -> None:
        admission_c_t = self.get_by_name(admission_campaign_type)
        if type(admission_c_t) is bool:
            admission_c_t = Intermediate(name=admission_campaign_type, stage="admissionCampaignType")
            self.add(admission_c_t)

        study_f = admission_c_t.get_by_name(study_form)
        if type(study_f) is bool:
            study_f = Intermediate(name=study_form, stage="studyForm")
            admission_c_t.add(study_f)

        e_d_i = study_f.next_keys.get(study_form, None)
        if e_d_i is None:
            study_f.add(EducationDirection(name=td_name, code=td_code))
        else:
            study_f.next[e_d_i] = EducationDirection(name=td_name, code=td_code)

    def add(self, element) -> None:
        if element.name in self.admission_keys:
            print("Такой уже есть")
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


def _search_in_application_list(name: str, applicants: List[Applicant], text: str, quota: int):
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


if __name__ == '__main__':
    with open("../response.json", "r", encoding="utf-8") as inp:
        j = loads(inp.read().replace('"-"', "0").replace('"+"', "1"))

    #
    # applications = []
    # names = set()
    # for a in j["data"]:
        # b = BaseApplicant(**a)
        # print(b)
        # c = b.compress()
        # print(c)
        # break
        # applications.append(Applicant(**a))
    #     names.add(applications[-1].name)
    #
    # print(applications)
    # applications.sort(reverse=True)
    # print(applications)
    #
    # pmi = EducationDirection(name="Прикладная математика и информатика", code="01.03.02", budget_quota=59, company_quota=8, special_quota=8, finance_quota=5,
    #                          datetime_update="2021-07-09 09:05:20", base_budget_list=applications, student_names=names)
    # vl = Intermediate(name="Владивосток", stage="implementationPlace", next=[pmi], student_names=names) # -
    # f_ed = Intermediate(name="Очная", stage="studyForm", next=[vl], student_names=names)
    # finance = Intermediate(name="Бюджетная основа", stage="financingSource", next=[f_ed], student_names=names) # -
    # admission = Intermediate(name="Прием на обучение на бакалавриат/специалитет", stage="admissionCampaignType", next=[finance], student_names=names)
    # # print(admission)
    # new_a = Intermediate.parse_raw(admission.json())
    # new_a.parse_next(True)
    # print()
    # print(new_a.find_applicant("142-701-763 36"))
