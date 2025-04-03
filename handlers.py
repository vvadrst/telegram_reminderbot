from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram import Bot
import asyncio

from cfg import TOKEN

import app.keyboard as kb

bot = Bot(token=TOKEN)
router = Router()

# Глобальные переменные для хранения данных
user_timers = {}  # {user_id: bool} - флаги активности таймеров
user_data = {}     # {user_id: {'name': str, 'reminder': str, 'data_reminder': str}}

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Этот бот-напоминалка',
                         reply_markup=kb.markup)

@router.callback_query(F.data == 'cmd_list')
async def cmd_list(callback: CallbackQuery):
    await callback.message.answer('Список команд:'
                                  '\n'
                                  '\n/register — регистрация'
                                  '\n'
                                  '\n/send — начать отправку напоминания'
                                  '\n'
                                  '\n/stop — остановить отправку напоминания'
                                  '\n'
                                  '\nПо вопросам — @abstrxctive')

async def send_periodic_message(user_id: int):
    while user_timers.get(user_id, False):
        # Получаем данные конкретного пользователя
        data = user_data.get(user_id, {})
        if data:
            await bot.send_message(
                user_id, 
                f"{data.get('name', 'Пользователь')}, ваше напоминание "
                f"{data.get('reminder', 'что-то')}, "
                f"дата: {data.get('data_reminder', 'не указана')}"
            )
        await asyncio.sleep(28800)  # 8 часов

@router.message(Command('send'))
async def start_timer(message: Message):
    user_id = message.from_user.id
    
    if user_timers.get(user_id, False):
        await message.reply("Отправка уже начата")
        return
    
    if user_id not in user_data:
        await message.reply("Сначала зарегистрируйтесь с помощью /register")
        return
    
    user_timers[user_id] = True
    await message.reply("Напоминание запущено! Вы будете получать напоминание каждые 8 часов.")
    
    asyncio.create_task(send_periodic_message(user_id))
    
@router.message(Command('stop'))
async def stop_timer(message: Message):
    user_id = message.from_user.id
    
    if not user_timers.get(user_id, False):
        await message.reply("Таймер не запущен.")
        return
    
    user_timers[user_id] = False
    await message.reply("Уведомления остановлены.")

class Reg(StatesGroup):
    name = State()    
    reminder = State()  
    data_reminder = State()

@router.message(Command('register'))
async def cmd_reg(message: Message, state: FSMContext):
    await state.set_state(Reg.name)  
    await message.answer('Введите своё имя')

@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text) 
    await state.set_state(Reg.reminder)  
    await message.answer('Введите напоминание')

@router.message(Reg.reminder)
async def reg_reminder(message: Message, state: FSMContext):
    await state.update_data(reminder=message.text)  
    await state.set_state(Reg.data_reminder) 
    await message.answer('Введите дату напоминания')

@router.message(Reg.data_reminder)
async def reg_reminder_data(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(data_reminder=message.text)
    data = await state.get_data()
    
    # Сохраняем данные конкретного пользователя
    user_data[user_id] = {
        'name': data.get('name', ''),
        'reminder': data.get('reminder', ''),
        'data_reminder': data.get('data_reminder', '')
    }
    
    await message.answer(
        f"{user_data[user_id]['name']}, ваше напоминание "
        f"{user_data[user_id]['reminder']}, "
        f"дата: {user_data[user_id]['data_reminder']}"
    )
    await state.clear()
