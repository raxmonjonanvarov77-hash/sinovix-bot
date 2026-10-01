
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


# ==================================================
# TOKEN
# ==================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")


# ==================================================
# BOT
# ==================================================

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ==================================================
# TEST SAVOLLARI
# ==================================================

QUIZZES = {

    "IELTS": [
        {
            "question": "Choose the correct sentence:",
            "answers": [
                "She go to school every day.",
                "She goes to school every day.",
                "She going to school every day.",
                "She gone to school every day."
            ],
            "correct": 1
        },

        {
            "question": "What is the synonym of 'important'?",
            "answers": [
                "Difficult",
                "Significant",
                "Small",
                "Unnecessary"
            ],
            "correct": 1
        },

        {
            "question": "I ___ English for three years.",
            "answers": [
                "study",
                "studied",
                "have studied",
                "studying"
            ],
            "correct": 2
        }
    ],


    "CEFR": [
        {
            "question": "He ___ football every Sunday.",
            "answers": [
                "play",
                "plays",
                "playing",
                "played"
            ],
            "correct": 1
        },

        {
            "question": "What is the opposite of 'easy'?",
            "answers": [
                "Simple",
                "Hard",
                "Quick",
                "Small"
            ],
            "correct": 1
        },

        {
            "question": "I am interested ___ music.",
            "answers": [
                "on",
                "at",
                "in",
                "for"
            ],
            "correct": 2
        }
    ],


    "ONA TILI": [
        {
            "question": "O‘zbek tilida nechta unli tovush mavjud?",
            "answers": [
                "5 ta",
                "6 ta",
                "7 ta",
                "8 ta"
            ],
            "correct": 1
        },

        {
            "question": "Qaysi biri ot so‘z turkumiga kiradi?",
            "answers": [
                "Chiroyli",
                "Kitob",
                "Tez",
                "O‘qimoq"
            ],
            "correct": 1
        },

        {
            "question": "Gapning bosh bo‘laklari qaysilar?",
            "answers": [
                "Aniqlovchi va to‘ldiruvchi",
                "Ega va kesim",
                "Hol va aniqlovchi",
                "To‘ldiruvchi va hol"
            ],
            "correct": 1
        }
    ],


    "MATEMATIKA": [
        {
            "question": "5 + 7 × 2 = ?",
            "answers": [
                "24",
                "19",
                "17",
                "14"
            ],
            "correct": 1
        },

        {
            "question": "x + 5 = 12. x = ?",
            "answers": [
                "5",
                "6",
                "7",
                "8"
            ],
            "correct": 2
        },

        {
            "question": "Uchburchak ichki burchaklari yig‘indisi nechaga teng?",
            "answers": [
                "90°",
                "180°",
                "270°",
                "360°"
            ],
            "correct": 1
        }
    ]
}


# ==================================================
# FOYDALANUVCHI NATIJASI
# ==================================================

user_data = {}
ADMIN_ID = 6707551846
class AddQuestion(StatesGroup):
    subject = State()
    question = State()
    answer_a = State()
    answer_b = State()
    answer_c = State()
    answer_d = State()
    correct = State()
    @dp.message(Command("admin"))
@dp.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda admin huquqi yo‘q.")
        return

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="➕ Savol qo‘shish",
        callback_data="admin_add"
    )

    keyboard.adjust(1)

    await message.answer(
        "⚙️ <b>SINOVIX ADMIN PANEL</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
# ==================================================
# TELEGRAM ID
# ==================================================

@dp.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )


# ==================================================
# /START
# ==================================================

@dp.message(Command("start"))
async def start(message: Message):

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="📝 Test boshlash",
        callback_data="subjects"
    )

    keyboard.button(
        text="📊 Natijam",
        callback_data="result"
    )

    keyboard.adjust(1)

    await message.answer(
        "👋 <b>SINOVIX</b> botiga xush kelibsiz!\n\n"
        "📚 Bilimingizni sinang va natijangizni tekshiring.",
        reply_markup=keyboard.as_markup(), 
        parse_mode="HTML"
    )   


# ==================================================
# FANLAR
# ==================================================

@dp.callback_query(F.data == "subjects")
async def subjects(callback: CallbackQuery):

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🇬🇧 IELTS",
        callback_data="quiz_IELTS"
    )

    keyboard.button(
        text="📘 CEFR",
        callback_data="quiz_CEFR"
    )

    keyboard.button(
        text="🇺🇿 Ona tili",
        callback_data="quiz_ONA TILI"
    )

    keyboard.button(
        text="📐 Matematika",
        callback_data="quiz_MATEMATIKA"
    )

    keyboard.adjust(2)

    await callback.message.edit_text(
        "📚 <b>Fanni tanlang:</b>",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    await callback.answer()


# ==================================================
# TESTNI BOSHLASH
# ==================================================

@dp.callback_query(F.data.startswith("quiz_"))
async def start_quiz(callback: CallbackQuery):

    subject = callback.data.replace("quiz_", "")

    user_id = callback.from_user.id

    user_data[user_id] = {
        "subject": subject,
        "question": 0,
        "score": 0
    }

    await callback.answer()

    await send_question(
        callback.message,
        user_id
    )


# ==================================================
# SAVOLNI YUBORISH
# ==================================================

async def send_question(message: Message, user_id: int):

    data = user_data[user_id]

    subject = data["subject"]

    question_number = data["question"]

    quiz = QUIZZES[subject]

    if question_number >= len(quiz):

        await show_result(message, user_id)

        return

    question = quiz[question_number]

    keyboard = InlineKeyboardBuilder()

    for index, answer in enumerate(question["answers"]):

        keyboard.button(
            text=f"{chr(65 + index)}. {answer}",
            callback_data=f"answer_{index}"
        )

    keyboard.adjust(1)

    await message.edit_text(

        f"📚 <b>{subject}</b>\n\n"

        f"❓ <b>Savol {question_number + 1}/{len(quiz)}</b>\n\n"

        f"{question['question']}",

        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


# ==================================================
# JAVOB
# ==================================================

@dp.callback_query(F.data.startswith("answer_"))
async def answer(callback: CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in user_data:

        await callback.answer(
            "Avval testni boshlang.",
            show_alert=True
        )

        return

    selected = int(
        callback.data.replace("answer_", "")
    )

    data = user_data[user_id]

    subject = data["subject"]

    question_number = data["question"]

    question = QUIZZES[subject][question_number]

    if selected == question["correct"]:

        data["score"] += 1

        text = "✅ To‘g‘ri!"

    else:

        text = (
            "❌ Noto‘g‘ri!\n"
            f"To‘g‘ri javob: "
            f"{chr(65 + question['correct'])}"
        )

    await callback.answer(text)

    data["question"] += 1

    await send_question(
        callback.message,
        user_id
    )


# ==================================================
# NATIJA
# ==================================================

async def show_result(message: Message, user_id: int):

    data = user_data[user_id]

    subject = data["subject"]

    score = data["score"]

    total = len(QUIZZES[subject])

    percentage = round(
        score / total * 100
    )

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🔄 Qayta ishlash",
        callback_data=f"quiz_{subject}"
    )

    keyboard.button(
        text="📚 Boshqa test",
        callback_data="subjects"
    )

    keyboard.adjust(1)

    await message.edit_text(

        "🎉 <b>Test yakunlandi!</b>\n\n"

        f"📚 Fan: <b>{subject}</b>\n"
        f"✅ To‘g‘ri javoblar: <b>{score}</b>\n"
        f"📝 Jami savollar: <b>{total}</b>\n"
        f"📊 Natija: <b>{percentage}%</b>\n\n"

        "SINOVIX bilan yana mashq qiling! 🚀",

        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


# ==================================================
# NATIJANI KO‘RISH
# ==================================================

@dp.callback_query(F.data == "result")
async def result(callback: CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in user_data:

        await callback.answer(
            "Hali test ishlamagansiz.",
            show_alert=True
        )

        return

    await show_result(
        callback.message,
        user_id
    )

    await callback.answer()


# ==================================================
# BOTNI ISHGA TUSHIRISH
# ==================================================

async def main():

    logging.basicConfig(
        level=logging.INFO
    )

    print("SINOVIX bot ishga tushdi!")

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
