from datetime import datetime
from pydantic import BaseModel, Field
from json import loads
from typing import List


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
    ordinaturePriority: float
    personal: int = Field(..., ge=0, le=10)
    scoreSum: int = Field(..., ge=0, le=310)

    def __cmp__(self, other):
        return self.scoreSum - other.scoreSum

    def __lt__(self, other):
        return self.scoreSum < other.scoreSum


class EducationDirection(BaseModel):
    code: str
    name: str
    datetime_update: datetime
    budget_quota: int = Field(0, ge=0)
    company_quota: int = Field(0, ge=0)
    special_quota: int = Field(0, ge=0)
    finance_quota: int = Field(0, ge=0)
    base_budget_list: List[Applicant] = Field(default_factory=list)
    special_budget_list: List[Applicant] = Field(default_factory=list)
    company_list: List[Applicant] = Field(default_factory=list)
    special_list: List[Applicant] = Field(default_factory=list)
    finance_list: List[Applicant] = Field(default_factory=list)


class Intermediate(BaseModel):
    name: str
    stage: str
    next: list = Field(default_factory=list)
    education_codes: set = Field(default_factory=set)
    student_ids: set = Field(default_factory=set)


if __name__ == '__main__':
    with open("../response.json", "r", encoding="utf-8") as inp:
        j = loads(inp.read().replace('"-"', "0").replace('"+"', "1"))

    applications = []
    for i in range(4):
        applications.append(Applicant(**j["data"][i]))

    print(applications)
    applications.sort(reverse=True)
    print(applications)

    pmi = EducationDirection(name="Прикладная математика и информатика", code="01.03.02", budget_quota=59, company_quota=8, special_quota=8, finance_quota=5,
                             datetime_update="2021-07-09 09:05:20", base_budget_list=applications)
    vl = Intermediate(name="Владивосток", stage="implementationPlace", next=[pmi])
    f_ed = Intermediate(name="Очная", stage="studyForm", next=[vl])
    finance = Intermediate(name="Бюджетная основа", stage="financingSource", next=[f_ed])
    admission = Intermediate(name="Прием на обучение на бакалавриат/специалитет", stage="admissionCampaignType", next=[finance])
    # print(admission)
    print(admission.json())
    new_a = Intermediate.parse_raw(admission.json())
    print(new_a)