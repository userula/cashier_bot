from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, \
    KeyboardButton
from aiogram.utils.markdown import hbold, hitalic

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
        await message.answer(f"{EMOJI[5]} Hello {hbold(message.from_user.full_name)} {message.from_user.id}!",
                             reply_markup=keyboards.adm_main)
    else:
        await message.answer(f"{EMOJI[5]} Hello {hbold(message.from_user.full_name)}!", reply_markup=keyboards.main)


@router.message(F.text == 'Catalog')
async def catalog(message: Message):
    result = repo.get_all_product()
    inlines = []
    if len(result) < 5:
        for res in result:
            inline = [InlineKeyboardButton(text=f'{res[1]} {res[2]}kg', callback_data=f'{res[3]}:add')]
            inlines.append(inline)
    else:
        print(len(result))
        for i in range(0, len(result), 2):
            if i + 1 == len(result):
                inline = [
                    InlineKeyboardButton(text=f'{result[i][1]} {result[i][2]}kg', callback_data=f'{result[i][3]}:add')]
            else:
                inline = [InlineKeyboardButton(text=f'{result[i][1]} {result[i][2]}kg', callback_data=f'{result[i][3]}:add'),
                          InlineKeyboardButton(text=f'{result[i + 1][1]} {result[i + 1][2]}kg', callback_data=f'{result[i + 1][3]}:add')]
            inlines.append(inline)
    products = InlineKeyboardMarkup(inline_keyboard=inlines)

    await message.answer(text=f'{hbold("Catalog:")}\n{hitalic("Price: tg/kg")}', reply_markup=products) if result \
        else await message.answer(text=f"Shop is empty...")


@router.message(F.text == 'Contacts')
async def contacts(message: Message):
    await message.answer(text=hbold(f"{EMOJI[2]} Contacts:"), reply_markup=keyboards.socials)


@router.message(F.text == 'Cart')
async def cart(message: Message):
    result = repo.get_cart_by_user_id(message.from_user.id)
    inlines = []
    for res in result:
        inline = [InlineKeyboardButton(text=f'{res[1]} {res[2]}', callback_data=f'{res[4]}:remove')]
        inlines.append(inline)
    user_cart = InlineKeyboardMarkup(inline_keyboard=inlines)
    await message.answer(text=f'{EMOJI[1]} {hbold("Cart:")}', reply_markup=user_cart) if result \
        else await message.answer(text=f"Cart is empty...")


@router.callback_query(lambda cb: True)
async def callback(cb: CallbackQuery):
    if cb.data.endswith(":add"):
        product = cb.data.split(":")[0]
        pr = repo.get_product_by_name(product)
        repo.add_to_cart(user_id=cb.from_user.id, product=pr[1], amount=1, screen_name=pr[3], product_id=pr[0])
        await cb.message.answer(text=f"{EMOJI[4]} Added to cart!")
    elif cb.data.endswith(":remove"):
        product = cb.data.split(":")[0]
        pr = repo.get_product_by_name(product)
        repo.remove_from_cart(user_id=cb.from_user.id, product_id=pr[0])
        await cb.message.answer(text=f"{EMOJI[3]} Removed from cart!")
    else:
        if cb.data == "Catalog":
            await catalog(cb.message)
        elif cb.data == "buy":
            pass
        else:
            await echo(cb.message)


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


class AddProduct(StatesGroup):
    NAME = State()
    AMOUNT = State()
    PRICE = State()


# Start command handler to initiate the conversation
@router.message(F.text == "Add product")
@router.message(F.text == "/add_product")
async def cmd_start(message: Message, state: FSMContext):
    if str(message.from_user.id) not in ADMIN_IDS:
        await state.clear()
        return
    await state.set_state(AddProduct.NAME)
    await message.answer(text="To add a new product, please provide the Name of product:\n"
                              "Type /cancel to cancel.")


@router.message(AddProduct.NAME)
async def process_pr_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.AMOUNT)
    await message.reply("Great! Please provide the amount:")


@router.message(AddProduct.AMOUNT)
async def process_pr_amount(message: Message, state: FSMContext):
    await state.update_data(amount=message.text)
    await state.set_state(AddProduct.PRICE)
    await message.reply("Nice! Please provide the price:")


@router.message(AddProduct.PRICE)
async def process_pr_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    data = await state.get_data()
    await state.clear()
    scr = data["name"][0].lower() + data['name'][1:]
    repo.add_product(name=data["name"], amount=data["amount"], screen_name=scr, price=data['price'])
    await message.reply(f"Thank you! {data['name']} added!")


@router.message()
async def echo(message: Message):
    await message.answer(text=f"Please, choose command:", reply_markup=get_admin_panel(message.from_user.id))
