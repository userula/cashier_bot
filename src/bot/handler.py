from typing import List

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, \
    KeyboardButton
from aiogram.utils.markdown import hbold, hitalic

import bot
from bot import keyboards
from conf import ADMIN_IDS, EMOJI
from services import DB
from utils import Logger

logger = Logger(name='handler').logger

router = Router()
repo = DB()


def get_admin_panel(user_id):
    if str(user_id) in ADMIN_IDS:
        return keyboards.adm_main
    return keyboards.main


@router.message(CommandStart())
async def start(message: Message):
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer(f"{EMOJI['handshake']} Hello {hbold(message.from_user.full_name)} {message.from_user.id}!",
                             reply_markup=keyboards.adm_main)
    else:
        await message.answer(f"{EMOJI['handshake']} Hello {hbold(message.from_user.full_name)}!",
                             reply_markup=keyboards.main)


@router.message(F.text == f'{EMOJI["catalog"]} Catalog')
async def catalog(message: Message):
    result = repo.get_all_product()
    inlines = []
    if len(result) < 5:
        for res in result:
            inline = [InlineKeyboardButton(text=f'{res[1]} {res[2]}kg', callback_data=f'{res[3]}:add')]
            inlines.append(inline)
    else:
        for i in range(0, len(result), 2):
            if i + 1 == len(result):
                inline = [
                    InlineKeyboardButton(text=f'{result[i][1]} {result[i][2]}kg', callback_data=f'{result[i][3]}:add')]
            else:
                inline = [InlineKeyboardButton(text=f'{result[i][1]} {result[i][2]}kg',
                                               callback_data=f'{result[i][3]}:add'),
                          InlineKeyboardButton(text=f'{result[i + 1][1]} {result[i + 1][2]}kg',
                                               callback_data=f'{result[i + 1][3]}:add')]
            inlines.append(inline)
    products = InlineKeyboardMarkup(inline_keyboard=inlines)

    await message.answer(text=f'{EMOJI["catalog"]} {hbold("Catalog:")}\n{hitalic("Price: tg/kg")}',
                         reply_markup=products) if result else await message.answer(text=f"Shop is empty...")


@router.message(F.text == f'{EMOJI["phone"]} Contacts')
async def contacts(message: Message):
    await message.answer(text=hbold(f"{EMOJI['phone']} Contacts:"), reply_markup=keyboards.socials)


@router.message(F.text == f'{EMOJI["cart"]} Cart')
async def cart(message: Message):
    result = repo.get_cart_by_user_id(message.from_user.id)
    inlines = []
    for res in result:
        inline = [InlineKeyboardButton(text=f'{res[1]} {res[2]}', callback_data=f'{res[4]}:remove')]
        inlines.append(inline)
    buy_btn = [InlineKeyboardButton(text=f'Go to order', callback_data="buy")]
    inlines.append(buy_btn)
    user_cart = InlineKeyboardMarkup(inline_keyboard=inlines)
    await message.answer(text=f'{EMOJI["cart"]} {hbold("Cart:")}', reply_markup=user_cart) if result \
        else await message.answer(text=f"Cart is empty...")


@router.callback_query(lambda cb: True)
async def callback(cb: CallbackQuery, state: FSMContext):
    if cb.data.endswith(":add"):
        product = cb.data.split(":")[0]
        pr = repo.get_product_by_name(product)
        repo.add_to_cart(user_id=cb.from_user.id, product=pr[1], amount=1, screen_name=pr[3], product_id=pr[0])
        await cb.message.answer(text=f"{EMOJI['green']} Added to cart!")
    elif cb.data.endswith(":remove"):
        product = cb.data.split(":")[0]
        pr = repo.get_product_by_name(product)
        repo.remove_from_cart(user_id=cb.from_user.id, product_id=pr[0])
        await cb.message.answer(text=f"{EMOJI['red']} Removed from cart!")
    else:
        if cb.data == "Catalog":
            await catalog(cb.message)
        elif cb.data == "buy":
            await state.set_state(Address.name)
            await cb.message.answer(f"{EMOJI['user']} Provide name:")
        else:
            await echo(cb.message)


class Address(StatesGroup):
    name = State()
    address = State()


@router.message(Address.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Address.address)
    await message.reply(f"{EMOJI['address']} Provide address:")


@router.message(Address.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    await state.clear()
    d = {
        "address": data['address'],
        "name": data['name'],
        "cart": repo.get_cart_by_user_id(user_id=message.from_user.id)
    }
    await notify_admin(data=d, message=message)
    repo.clear_cart_by_user_id(user_id=message.from_user.id)
    await message.reply("Thank you for purchase!")


async def notify_admin(data, message):
    notify_text = f"{EMOJI['order']} NEW ORDER!!!\n" \
                  f"{EMOJI['user']} {data['name']}\n" \
                  f"{EMOJI['address']} {data['address']}\n" \
                  f"{format_table(data['cart'])}"
    for admin in ADMIN_IDS:
        await message.bot.send_message(chat_id=admin,
                                       text=notify_text,
                                       parse_mode=ParseMode.MARKDOWN,
                                       disable_notification=True)


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "okay...",
            reply_markup=get_admin_panel(message.from_user.id),
        )
    else:
        await state.clear()
        await message.answer(
            "Cancelled.",
            reply_markup=get_admin_panel(message.from_user.id),
        )


class ProductClass(StatesGroup):
    FUNC = State()
    PRODUCT_LIST = State()


@router.message(F.text == f"{EMOJI['add']} Add product")
@router.message(F.text == "/add_product")
async def add_product(message: Message, state: FSMContext):
    if str(message.from_user.id) not in ADMIN_IDS:
        await state.clear()
        return
    await state.set_state(ProductClass.PRODUCT_LIST)
    await message.answer(text=f"To add a new products, provide:\n{hbold('Name Amount Price')}\nof product in each row\n"
                              "Type /cancel to cancel.")


@router.message(ProductClass.PRODUCT_LIST)
async def process_pr_list(message: Message, state: FSMContext):
    await state.update_data(product_list=message.text)
    data = await state.get_data()
    await state.clear()
    product_list = data["product_list"].split("\n")
    headers = [["Name", "Amount", "Price"], ["---------", "---------", "---------"]]
    for pr in product_list:
        parts: List[str] = pr.split(" ")
        if len(parts) < 3:
            await message.reply(f"{EMOJI['red']} You forgot some params!\n"
                                f"<pre>{headers}\n{pr}</pre>")
            return
        if not parts[1].isdigit() or not parts[2].isdigit():
            await message.reply(f"{EMOJI['red']} Amount/Price is not digit!\n"
                                f"<pre>{headers}\n{pr}</pre>")
            return

    for pr in product_list:
        parts: List[str] = pr.split(" ")
        scr = parts[0][0].lower() + parts[0][1:]
        repo.add_product(name=parts[0], amount=parts[1], screen_name=scr, price=parts[2])
        headers.append(parts)
    await message.reply(f"{EMOJI['green']} Products added! count [{len(product_list)}]\n"
                        f"{format_table(headers)}", parse_mode=ParseMode.MARKDOWN)


def format_table(data):
    t = ""
    for d in data:
        t += f"{d[0]} {d[1]} {d[2]}\n"
    return t


@router.message()
async def echo(message: Message):
    await message.answer(text=f"Please, choose command:", reply_markup=get_admin_panel(message.from_user.id))
