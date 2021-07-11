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
    date: datetime
    admissionCampaignType: str
    financingSource: str
    studyForm: str
    implementationPlace: str
    category: str
    examinationsless: bool
    preemptiveRight: bool
    consent: bool
    enrolled: int = Field(..., ge=0)
    test1score: int = Field(..., ge=0, le=100)
    test2score: int = Field(..., ge=0, le=100)
    test3score: int = Field(..., ge=0, le=100)
    test4score: int = Field(default=0, ge=0, le=100)
    ordinaturePriority: float
    personal: int = Field(..., ge=0, le=10)
    scoreSum: int = Field(..., ge=0, le=310)

    def __cmp__(self, other) -> bool:
        return self.scoreSum - other.scoreSum

    def __lt__(self, other) -> bool:
        return self.scoreSum < other.scoreSum

    def __bool__(self) -> bool:
        return True


class EducationDirection(BaseModel):
    code: str
    name: str
    datetime_update: datetime = Field(default_factory=datetime.now)
    budget_quota: int = Field(0, ge=0)
    company_quota: int = Field(0, ge=0)
    special_quota: int = Field(0, ge=0)
    finance_quota: int = Field(0, ge=0)
    base_budget_list: List[Applicant] = Field(default_factory=list)
    special_budget_list: List[Applicant] = Field(default_factory=list)
    company_list: List[Applicant] = Field(default_factory=list)
    special_list: List[Applicant] = Field(default_factory=list)
    finance_list: List[Applicant] = Field(default_factory=list)
    student_names: Set[str] = Field(default_factory=set)

    def find_applicant(self, name: str) -> IntermediateResult:
        result: IntermediateResult = IntermediateResult(text=self.name)

        args = ((self.special_budget_list, "На общих основаниях", self.budget_quota),
                (self.base_budget_list, "На общих основаниях", self.budget_quota, len(self.special_budget_list)),
                (self.company_list, "Целевой приём", self.company_quota),
                (self.special_list, "Особая квота", self.special_quota),
                (self.finance_list, "Полное возмещение затрат", self.finance_quota))
        for arg in args:
            if res := _search_in_application_list(name, *arg):
                result.next.append(res)

        return result


class Intermediate(BaseModel):
    name: str
    stage: str
    next: list = Field(default_factory=list)
    education_codes: Set[str] = Field(default_factory=set)
    student_names: Set[str] = Field(default_factory=set)

    def parse_next(self, recursive=False):
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


class ApplicantStorage(BaseModel):
    admissions: List[Intermediate] = Field(default_factory=list)

    def find_applicant(self, name: str) -> List[IntermediateResult]:
        result: List[IntermediateResult] = []
        for intermediate in self.admissions:
            if name in intermediate.student_names:
                result += intermediate.find_applicant(name)

        return result


def _search_in_application_list(name: str, applications: List[Applicant], text: str, quota: int, scope: int = 0):
    for applicant_i in range(len(applications)):
        if name == applications[applicant_i].name:
            return ApplicantResult(text=text, position=applicant_i + 1 + scope, quota=quota)


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

    applications = []
    names = set()
    for a in j["data"]:
        applications.append(Applicant(**a))
        names.add(applications[-1].name)

    print(applications)
    applications.sort(reverse=True)
    print(applications)

    pmi = EducationDirection(name="Прикладная математика и информатика", code="01.03.02", budget_quota=59, company_quota=8, special_quota=8, finance_quota=5,
                             datetime_update="2021-07-09 09:05:20", base_budget_list=applications, student_names=names)
    vl = Intermediate(name="Владивосток", stage="implementationPlace", next=[pmi], student_names=names)
    f_ed = Intermediate(name="Очная", stage="studyForm", next=[vl], student_names=names)
    finance = Intermediate(name="Бюджетная основа", stage="financingSource", next=[f_ed], student_names=names)
    admission = Intermediate(name="Прием на обучение на бакалавриат/специалитет", stage="admissionCampaignType", next=[finance], student_names=names)
    # print(admission)
    new_a = Intermediate.parse_raw(admission.json())
    new_a.parse_next(True)
    print()
    print(new_a.find_applicant("142-701-763 36"))
