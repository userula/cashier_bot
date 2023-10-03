from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main_kb = [
    [KeyboardButton(text='Catalog'),
     KeyboardButton(text='Cart')],
    [KeyboardButton(text='My profile'),
     KeyboardButton(text='Contacts')]
]

adm_kb = [
    [KeyboardButton(text='Catalog'),
     KeyboardButton(text='Cart')],
    [KeyboardButton(text='My profile'),
     KeyboardButton(text='Contacts')],
    [KeyboardButton(text='Add product')]
]

adm_main = ReplyKeyboardMarkup(keyboard=adm_kb,
                               resize_keyboard=True,
                               input_field_placeholder='Выберите пункт ниже')

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')


socials = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='NU Bot support', url='https://t.me/lj23onelove')],
    [InlineKeyboardButton(text='Shop', url='https://t.me/lj23onelove')]
])

catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Carrot', callback_data='carrot')],
    [InlineKeyboardButton(text='Potato', callback_data='potato')]
])

buy = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Buy", callback_data="buy")],
    [InlineKeyboardButton(text="Catalog", callback_data="catalog")]
])
