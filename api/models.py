import re

from typing import Optional, List
from pydantic import BaseModel, field_validator


class Profile(BaseModel):
    full_name: Optional[str]
    unit_id: Optional[int]
    profile_info: Optional[str] = None
    social_media_links: Optional[List[str]]

    @field_validator('full_name')
    def validate_full_name(cls, value: str):
        if not re.match(r'^(?=.{1,100}$)([А-Я]{1}[а-я]+\s?){2,}$', value):
            raise ValueError('Поле full_name должно включать от 2х слов начинающихся с заглавной буквы. '
                             'Длина full_name не может привышать 100 символов.')
        return value

    @field_validator('profile_info')
    def validate_profile_info(cls, value: str):
        if not re.match(r'^[А-Яа-яA-Za-z0-9\s]{1,101}$', value):
            raise ValueError('Поле profile_info может содержать буквы русского и латинского алфавита и цифры. '
                             'Длина profile_info не может привышать 100 символов.')
        return value

    @field_validator('social_media_links')
    def validate_links(cls, value: List[str]):

        for link in value:

            if not re.match(
                    r'^(https://vk\.com/((id\d{1,10})|(\w{5,32})))$|^(https://instagram\.com/\w{1,30})$', link
            ):
                raise ValueError(f'Ссылка {link[:10] + "..." + link[-10:] if len(link) > 20 else link} '
                                 f'не соответствует установленному формату.')

        return value


class Profiles(BaseModel):
    profiles: Optional[List[Profile]]


__all__ = ['Profiles', 'Profile']
