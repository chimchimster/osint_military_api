import re

from typing import Optional, List, Final, Union, Dict
from pydantic import BaseModel, Extra, field_validator


VK_URL: Final[str] = 'https://vk.com/'
INST_URL: Final[str] = 'https://instagram.com/'


class Validator:

    @classmethod
    def validate_link(cls, link: str):

        if link.startswith(VK_URL):
            return ''.join(link.split(VK_URL))
        else:
            return ''.join(link.split(INST_URL))


class AccountProfileConnection(BaseModel, Validator, extra=Extra.allow):
    old_profile_id: int
    new_profile_id: int
    account: Union[str, Dict]
    user_id: int

    @field_validator('account')
    def validate_account(cls, value: str):

        if not re.match('^(https://vk\.com/((id\d{1,10})|(\w{5,32})))$|^(https://instagram\.com/\w{1,30})$', value):
            raise ValueError(f'Ссылка {value[:10] + "..." + value[-10:] if len(value) > 20 else value} '
                             f'не соответствует установленному формату.')

        return {value: cls.validate_link(value)}


class Account(BaseModel, Validator):
    profile_id: int
    accounts: Union[List[str], List[Dict]]
    user_id: int

    @field_validator('accounts')
    def validate_links(cls, value: Union[List[str], None]):

        mapping = []
        for link in value:
            if re.match('^(https://vk\.com/((id\d{1,10})|(\w{5,32})))$', link):
                mapping.append({link: cls.validate_link(link)})
            elif re.match('^(https://instagram\.com/\w{1,30})$', link):
                mapping.append({link: cls.validate_link(link)})
            else:
                raise ValueError(f'Ссылка {link[:10] + "..." + link[-10:] if len(link) > 20 else link} '
                                 f'не соответствует установленному формату.')

        return mapping


class Profile(BaseModel, Validator, extra=Extra.allow):
    full_name: str
    unit_id: int
    profile_info: Optional[str]
    social_media_links: Optional[Union[List[str], List[Dict]]]

    @field_validator('full_name')
    def validate_full_name(cls, value: str):
        if not re.match(r'^(?=.{1,100}$)([А-Я]{1}[а-я]+\s?){2,}$', value):
            raise ValueError('Поле full_name должно включать от 2х слов начинающихся с заглавной буквы. '
                             'Длина full_name не может привышать 100 символов.')
        return value

    @field_validator('profile_info')
    def validate_profile_info(cls, value: str):
        if not re.match(r'^[А-Яа-яA-Za-z0-9\s\.\,]{1,101}$', value):
            raise ValueError('Поле profile_info может содержать буквы русского и латинского алфавита и цифры. '
                             'Длина profile_info не может привышать 100 символов.')
        return value

    @field_validator('social_media_links')
    def validate_links(cls, value: Union[List[str], None]):

        if not value:
            return value

        mapping = []
        for link in value:
            if re.match('^(https://vk\.com/((id\d{1,10})|(\w{5,32})))$', link):
                mapping.append({link: cls.validate_link(link)})
            elif re.match('^(https://instagram\.com/\w{1,30})$', link):
                mapping.append({link: cls.validate_link(link)})
            else:
                raise ValueError(f'Ссылка {link[:10] + "..." + link[-10:] if len(link) > 20 else link} '
                                 f'не соответствует установленному формату.')

        return mapping

    def __hash__(self):
        return hash(''.join(self.social_media_links))


class Profiles(BaseModel):
    profiles: Optional[List[Profile]]
    user_id: Optional[int]


__all__ = ['Profiles', 'Profile', 'Account', 'AccountProfileConnection']
