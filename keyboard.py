from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Список команд', callback_data='cmd_list')]
])
