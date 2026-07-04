from enum import StrEnum


class Gender(StrEnum):
    male = "male"
    female = "female"


GENDER_LABELS = {
    Gender.male.value: "Мужской",
    Gender.female.value: "Женский",
}
