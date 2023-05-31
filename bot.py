import asyncio
import re

from selenium import webdriver

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

bot = Bot(token='6157242757:AAF00WlpAZ5fpFHoHGiRxMDNdhjlxGEgJiM')  # Бот
dp = Dispatcher()
s = Service('chromedriver.exe')
driver = webdriver.Chrome(service=s)


class Storage:
    countries = dict()
    hotels = dict()

    @classmethod
    async def set_aviable_countries(self, countries):
        self.countries = countries

    @classmethod
    async def set_aviable_hotels(self, hotels):
        self.hotels = hotels


class User:

    def __init__(self, first_name, middle_name, last_name, phone_number):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.phone_number = phone_number

    suggestions = dict()

    async def set_first_name(self, first_name):
        self.first_name = first_name

    async def set_last_name(self, last_name):
        self.last_name = last_name

    async def set_middle_name(self, middle_name):
        self.middle_name = middle_name

    async def set_phone_number(self, phone_number):
        self.phone_number = phone_number


class BookHotel(StatesGroup):
    unnamed = State()
    standart = State()
    editing_info = State()
    editing_first_name = State()
    editing_last_name = State()
    editing_middle_name = State()
    editing_phone_number = State()
    checking_profile = State()
    choosing_country = State()
    choosing_town = State()
    choosing_hotel = State()
    choosing_suggestion = State()


main_user = User('', '', '', '')


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Обнуление данных пользователя
    kb = [[types.InlineKeyboardButton(text="Пропустить", callback_data="skip")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await state.set_state(BookHotel.unnamed)
    await main_user.set_first_name('')
    await main_user.set_last_name('')
    await main_user.set_middle_name('')
    await main_user.set_phone_number('')
    await message.answer(f"Здравствуйте! Я помогу вам выбрать тур в соответствии с вашими предпочтениями.")
    await message.answer("Как вас зовут?", reply_markup=keyboard)


@dp.callback_query(Text("skip"))
async def skip_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookHotel.standart)
    await main_user.set_first_name(callback.message.chat.first_name)
    await bot.send_message(
        text=f"Очень приятно, {callback.message.chat.first_name}! Чтобы перейти в главное меню, введите команду /home",
        chat_id=callback.message.chat.id)


@dp.message(F.text, BookHotel.unnamed)
async def insert_initial_name(message: types.Message, state: FSMContext):
    if not re.compile(r"[^/]+").match(message.text):
        await state.set_state(BookHotel.standart)
        await main_user.set_first_name(message.from_user.first_name)
        await message.answer(
            f"Выбрано недействительное имя. Введите команду /start, чтобы "
            f"ввести новое имя либо пропустите этот шаг, чтобы поставить имя профиля Telegram.")
    else:
        await message.answer(f"Очень приятно, {message.text}! Чтобы перейти в главное меню, введите команду /home")
        await state.set_state(BookHotel.standart)
        await main_user.set_first_name(message.text)


@dp.callback_query(Text("back_to_main_menu"))
async def duplicate_show_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookHotel.standart)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Профиль",
        callback_data="profile")
    )
    builder.add(types.InlineKeyboardButton(
        text="Начать поиск",
        callback_data="start_searching"
    )
    )
    builder.adjust(2)
    await bot.send_message(text="🚩Домашняя страница🚩", chat_id=callback.message.chat.id,
                           reply_markup=builder.as_markup())


@dp.message(Command("home"))
async def show_menu(message: types.Message, state: FSMContext):
    await state.set_state(BookHotel.standart)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Профиль",
        callback_data="profile")
    )
    builder.add(types.InlineKeyboardButton(
        text="Начать поиск",
        callback_data="start_searching"
    )
    )
    builder.adjust(2)
    await message.answer(
        "🚩Домашняя страница🚩",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(Text("profile"))
async def show_profile(callback: types.CallbackQuery, state: FSMContext):
    kb = [[types.InlineKeyboardButton(text="Редактировать", callback_data="edit_info"),
           types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await state.set_state(BookHotel.checking_profile)
    await bot.send_message(chat_id=callback.message.chat.id, text=
    f"<b><i>Ваши данные</i></b>:\n\n"
    f"<b>Фамилия</b>: {main_user.last_name}\n"
    f"<b>Имя</b>: {main_user.first_name}\n"
    f"<b>Отчество</b>: {main_user.middle_name}\n"
    f"<b>Номер телефона</b>: {main_user.phone_number}", parse_mode='HTML', reply_markup=keyboard)


@dp.callback_query(Text("edit_info"))
async def edit_profile(callback: types.CallbackQuery, state: FSMContext):
    kb = [
        [types.InlineKeyboardButton(text="Фамилию", callback_data="last_name"),
         types.InlineKeyboardButton(text="Имя", callback_data="first_name")],
        [types.InlineKeyboardButton(text="Отчество", callback_data="middle_name")],
        [types.InlineKeyboardButton(text="Номер телефона", callback_data="phone_number")],
        [types.InlineKeyboardButton(text="Назад", callback_data="profile")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await state.set_state(BookHotel.editing_info)
    await bot.send_message(chat_id=callback.message.chat.id, text="Выберите, какую информацию хотите отредактировать?",
                           reply_markup=keyboard)


@dp.callback_query(Text("last_name"), BookHotel.editing_info)
async def edit_last_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookHotel.editing_last_name)
    await bot.send_message(chat_id=callback.message.chat.id, text="Введите новую фамилию")


@dp.message(F.text, BookHotel.editing_last_name)
async def complete_editing_last_name(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="Да", callback_data="edit_info"),
           types.InlineKeyboardButton(text="Нет", callback_data="profile")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await main_user.set_last_name(message.text)
    await message.reply("Вы успешно изменили фамилию в профиле!")
    await message.answer("Хотите изменить другие данные?", reply_markup=keyboard)


@dp.callback_query(Text("first_name"), BookHotel.editing_info)
async def edit_first_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookHotel.editing_first_name)
    await bot.send_message(chat_id=callback.message.chat.id, text="Введите новое имя")


@dp.message(F.text, BookHotel.editing_first_name)
async def complete_editing_first_name(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="Да", callback_data="edit_info"),
           types.InlineKeyboardButton(text="Нет", callback_data="profile")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await main_user.set_first_name(message.text)
    await message.reply("Вы успешно изменили имя в профиле!")
    await message.answer("Хотите изменить другие данные?", reply_markup=keyboard)


@dp.callback_query(Text("middle_name"), BookHotel.editing_info)
async def edit_middle_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookHotel.editing_middle_name)
    await bot.send_message(chat_id=callback.message.chat.id, text="Введите новое отчество")


@dp.message(F.text, BookHotel.editing_middle_name)
async def complete_editing_middle_name(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="Да", callback_data="edit_info"),
           types.InlineKeyboardButton(text="Нет", callback_data="profile")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await main_user.set_middle_name(message.text)
    await message.reply("Вы успешно изменили отчество в профиле!")
    await message.answer("Хотите изменить другие данные?", reply_markup=keyboard)


@dp.callback_query(Text("phone_number"), BookHotel.editing_info)
async def edit_phone_number(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookHotel.editing_phone_number)
    await bot.send_message(chat_id=callback.message.chat.id, text="Введите новый номер телефона")


@dp.message(F.text, BookHotel.editing_phone_number)
async def complete_editing_phone_number(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="Да", callback_data="edit_info"),
           types.InlineKeyboardButton(text="Нет", callback_data="profile")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await main_user.set_phone_number(message.text)
    await message.reply("Вы успешно изменили номер телефона в профиле!")
    await message.answer("Хотите изменить другие данные?", reply_markup=keyboard)


@dp.callback_query(Text("start_searching"), BookHotel.standart)
async def choose_country(callback: types.CallbackQuery):
    url = "https://www.tez-tour.com/"
    driver.get(url)
    countries = dict()
    try:
        driver.find_element(By.ID, 'submitButton').click()
    except:
        pass
    finally:
        pass
    countries_container = driver.find_element(By.ID, 'hotOffersContainer')
    unfiltered_countries = countries_container.find_elements(By.CLASS_NAME, 'tile-item')
    for i in unfiltered_countries[:5]:
        country_name = i.find_element(By.CLASS_NAME, 'tile-title').text
        link = i.find_element(By.CLASS_NAME, 'tile-item-inner').get_attribute('href')
        countries[country_name] = link
    await Storage.set_aviable_countries(countries)

    kb = [[types.InlineKeyboardButton(text=i[0], callback_data=f'country:{i[0]}') for i in
           list(Storage.countries.items())[:3]],
          [types.InlineKeyboardButton(text=i[0], callback_data=f'country:{i[0]}') for i in
           list(Storage.countries.items())[3:]],
          [types.InlineKeyboardButton(text='В главное меню', callback_data='back_to_main_menu')]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.send_message(chat_id=callback.message.chat.id, text=f"Выберите страну:",
                           reply_markup=keyboard)


@dp.callback_query(Text(startswith="country:"))
async def choose_hotel(callback: types.CallbackQuery):
    hotels = dict()
    for country_info in Storage.countries.items():
        if callback.data.split(':')[1] == country_info[0]:
            driver.get(country_info[1])
            break
    unfiltered_hotels = driver.find_elements(By.CLASS_NAME, 'side-has-rating')[:5]
    for unfiltered_hotel in unfiltered_hotels:
        hotel_info = unfiltered_hotel.find_element(By.CLASS_NAME, 'h5')
        hotel_name = hotel_info.text
        link = hotel_info.find_element(By.TAG_NAME, 'a').get_attribute('href')
        hotels[hotel_name] = link

    await Storage.set_aviable_hotels(hotels)

    kb = [[types.InlineKeyboardButton(text=i[0], url=i[1]) for i in
           list(Storage.hotels.items())[:2]],
          [types.InlineKeyboardButton(text=i[0], url=i[1]) for i in
           list(Storage.hotels.items())[2:]],
          [types.InlineKeyboardButton(text='В главное меню', callback_data='back_to_main_menu')]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.send_message(chat_id=callback.message.chat.id, text=f"Выберите отель:",
                           reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
