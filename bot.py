import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, PollAnswer, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)

TOKEN = "8750690912:AAHgIwEzLSLHPw9adDKTIfTq4WlORSwUWHE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

QUIZ_DATA = [
    {
        "question": "1/7. Какой из перечисленных оксидов является АМФОТЕРНЫМ?",
        "options": ["CaO", "ZnO", "SO3", "CO"],
        "correct": 1,
        "explanation": "ZnO (оксид цинка) — амфотерный оксид. CaO — основный, SO3 — кислотный, CO — несолеобразующий."
    },
    {
        "question": "2/7. Какая степень окисления у хрома в дихромате калия (K2Cr2O7)?",
        "options": ["+3", "+6", "+7", "+2"],
        "correct": 1,
        "explanation": "У калия +1, у кислорода -2. 2*(+1) + 2*x + 7*(-2) = 0 -> 2x = 12 -> x = +6."
    },
    {
        "question": "3/7. С помощью какого реактива можно качественно распознать сульфат-ионы (SO4²⁻)?",
        "options": ["AgNO3", "BaCl2", "NaOH", "HCl"],
        "correct": 1,
        "explanation": "Ионы Ba²⁺ дают с сульфат-ионами белый кристаллический осадок BaSO4, нерастворимый в кислотах."
    },
    {
        "question": "4/7. Какой газ выделяется при реакции меди с КОНЦЕНТРИРОВАННОЙ азотной кислотой?",
        "options": ["H2 (водород)", "NO (оксид азота II)", "NO2 (бурый газ)", "N2O (веселящий газ)"],
        "correct": 2,
        "explanation": "Концентрированная HNO3 с малоактивными металлами (Cu) восстанавливается до бурого газа NO2."
    },
    {
        "question": "5/7. Выберите ряд, где все вещества — СИЛЬНЫЕ электролиты:",
        "options": [
            "HCl, NaOH, BaSO4",
            "H2SO4, KOH, NaCl",
            "HNO2, Cu(OH)2, KNO3",
            "H2CO3, NH4OH, AgCl"
        ],
        "correct": 1,
        "explanation": "H2SO4, KOH и растворимая соль NaCl полностью диссоциируют на ионы в водном растворе."
    },
    {
        "question": "6/7. С каким из веществ НЕ реагирует гидроксид натрия (NaOH)?",
        "options": ["Al2O3", "CO2", "CuSO4", "MgO"],
        "correct": 3,
        "explanation": "MgO — основной оксид. Щёлочи не реагируют с основными оксидами."
    },
    {
        "question": "7/7. Как изменяются неметаллические свойства в ряду Si -> P -> S -> Cl?",
        "options": ["Усиливаются", "Ослабевают", "Не изменяются", "Сначала усиливаются, затем ослабевают"],
        "correct": 0,
        "explanation": "В периоде слева направо радиус атома уменьшается, а электроотрицательность и неметаллические свойства растут."
    }
]

user_sessions = {}

kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧪 Начать квиз заново")]],
    resize_keyboard=True
)

async def send_next_question(user_id: int, chat_id: int):
    session = user_sessions.get(user_id)
    if not session:
        return

    idx = session["index"]
    if idx < len(QUIZ_DATA):
        q = QUIZ_DATA[idx]
        await bot.send_poll(
            chat_id=chat_id,
            question=q["question"],
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct"],
            explanation=q["explanation"],
            is_anonymous=False
        )
    else:
        score = session["score"]
        total = len(QUIZ_DATA)
        await bot.send_message(
            chat_id=chat_id,
            text=f"🏁 **Тест завершён!**\n\nТвой результат: **{score} из {total}**.",
            reply_markup=kb,
            parse_mode="Markdown"
        )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 🧪 Добро пожаловать в квиз по неорганической химии.\n"
        "Нажми /quiz или кнопку ниже, чтобы начать!",
        reply_markup=kb
    )

@dp.message(Command("quiz"))
@dp.message(F.text == "🧪 Начать квиз заново")
async def start_quiz(message: Message):
    user_id = message.from_user.id
    user_sessions[user_id] = {"index": 0, "score": 0}
    await message.answer("Вопрос 1 👇")
    await send_next_question(user_id, message.chat.id)

@dp.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    user_id = poll_answer.user.id
    session = user_sessions.get(user_id)
    if not session:
        return

    current_idx = session["index"]
    if current_idx < len(QUIZ_DATA):
        if poll_answer.option_ids and poll_answer.option_ids[0] == QUIZ_DATA[current_idx]["correct"]:
            session["score"] += 1
        session["index"] += 1
        await asyncio.sleep(1.0)
        await send_next_question(user_id, user_id)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, polling_timeout=20)

if __name__ == "__main__":
    asyncio.run(main())
