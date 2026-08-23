import os
from google import genai
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, BigInteger, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    
ContextTypes, 
MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://", "postgresql+psycopg://", 1
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass 
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pubg_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    warnings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


Base.metadata.create_all(engine)
TELEGRAM_CHANNEL = os.getenv(
    "TELEGRAM_CHANNEL",
    "@NexoraArenaOfficial"
)

TELEGRAM_URL = os.getenv(
    "TELEGRAM_URL",
    "https://t.me/NexoraArenaOfficial"
)

YOUTUBE_URL = os.getenv(
    "YOUTUBE_URL",
    "https://youtube.com"
)

TIKTOK_URL = os.getenv(
    "TIKTOK_URL",
    "https://tiktok.com"
)

INSTAGRAM_URL = os.getenv(
    "INSTAGRAM_URL",
    "https://instagram.com"
)


def social_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 عضویت در Telegram",
                    url=TELEGRAM_URL
                )
            ],
            [
                InlineKeyboardButton(
                    "▶️ Subscribe YouTube",
                    url=YOUTUBE_URL
                )
            ],
            [
                InlineKeyboardButton(
                    "🎵 Follow TikTok",
                    url=TIKTOK_URL
                )
            ],
            [
                InlineKeyboardButton(
                    "📸 Follow Instagram",
                    url=INSTAGRAM_URL
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ بررسی عضویت",
                    callback_data="check_membership"
                )
            ],
        ]
    )


def main_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🏆 مسابقات",
                    callback_data="tournaments"
                ),
                InlineKeyboardButton(
                    "📝 ثبت‌نام",
                    callback_data="register"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📜 قوانین",
                    callback_data="rules"
                ),
                InlineKeyboardButton(
                    "🎁 جوایز",
                    callback_data="prizes"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎮 PUBG ID",
                    callback_data="pubg"
                ),
                InlineKeyboardButton(
                    "👤 پروفایل من",
                    callback_data="profile"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🥇 رتبه‌بندی",
                    callback_data="leaderboard"
                ),
                InlineKeyboardButton(
                    "📅 مسابقات آینده",
                    callback_data="upcoming"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📢 شبکه‌های اجتماعی",
                    callback_data="social"
                ),
                InlineKeyboardButton(
                    "🆘 پشتیبانی",
                    callback_data="support"
                ),
            ],
        ]
    )


async def is_telegram_member(
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        member = await context.bot.get_chat_member(
            chat_id=TELEGRAM_CHANNEL,
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator",
        ]

    except Exception as error:
        print("Membership check error:", error)
        return False


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (
        "⚡ RAIDEN | NEXORA ARENA 👑\n\n"
        "🎮 به مرکز مسابقات PUBG Mobile خوش آمدید!\n\n"
        "🏆 Solo • Duo • Squad\n"
        "💰 UC و جوایز ویژه\n"
        "🥇 رقابت کن، برنده شو و قهرمان شو!\n\n"
        "برای ورود به بخش مسابقات، ابتدا شبکه‌های "
        "اجتماعی NEXORA ARENA را دنبال کنید 👇\n\n"
        "📌 عضویت Telegram توسط ربات به‌صورت واقعی "
        "بررسی می‌شود."
    )

    await update.message.reply_text(
        text,
        reply_markup=social_keyboard()
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    if action == "check_membership":

        member = await is_telegram_member(
            user_id,
            context
        )

        if not member:
            await query.message.reply_text(
                "❌ عضویت شما در کانال Telegram "
                "تأیید نشد.\n\n"
                "ابتدا وارد کانال شوید و عضو شوید، "
                "سپس دوباره روی «✅ بررسی عضویت» بزنید.",
                reply_markup=social_keyboard()
            )
            return

        await query.message.reply_text(
            "✅ عضویت Telegram شما تأیید شد!\n\n"
            "👑 به NEXORA ARENA خوش آمدید.\n"
            "حالا می‌توانید از منوی اصلی استفاده کنید.",
            reply_markup=main_keyboard()
        )
        return

    if action == "tournaments":
        text = (
            "🏆 مسابقات NEXORA ARENA\n\n"
            "مسابقات فعال به‌زودی در این قسمت "
            "نمایش داده می‌شوند."
        )

    elif action == "register":
        text = (
            "📝 ثبت‌نام مسابقه\n\n"
            "سیستم ثبت‌نام بازیکنان در مرحله بعد "
            "به RAIDEN اضافه می‌شود."
        )

    elif action == "rules":
        text = (
            "📜 قوانین NEXORA ARENA\n\n"
            "1️⃣ Hack و Cheat ممنوع است.\n"
            "2️⃣ PUBG ID باید صحیح باشد.\n"
            "3️⃣ استفاده از حساب شخص دیگر ممنوع است.\n"
            "4️⃣ توهین، تهدید و آزار کاربران ممنوع است.\n"
            "5️⃣ Spam و تبلیغات غیرمجاز ممنوع است.\n"
            "6️⃣ بازیکنان باید سر وقت وارد Lobby شوند.\n"
            "7️⃣ تبانی برای Kill یا امتیاز ممنوع است.\n"
            "8️⃣ قوانین مخصوص هر Tournament باید رعایت شود.\n"
            "9️⃣ تقلب می‌تواند باعث حذف از مسابقه شود.\n"
            "🔟 نتایج قبل از پرداخت جایزه بررسی می‌شوند."
        )

    elif action == "prizes":
        text = (
            "🎁 جوایز NEXORA ARENA\n\n"
            "💰 UC\n"
            "📱 iPhone\n"
            "🎧 AirPods\n"
            "🎮 PS5\n"
            "🎁 Gift Cards\n"
            "🏆 جوایز ویژه Tournament\n\n"
            "نوع و مقدار جایزه هر مسابقه "
            "جداگانه اعلام می‌شود."
        )

    elif action == "pubg":
        text = (
            "🎮 PUBG ID\n\n"
            "در مرحله بعد می‌توانید PUBG Username "
            "و PUBG ID خود را در ربات ذخیره کنید."
        )

    elif action == "profile":
        text = (
            "👤 پروفایل بازیکن\n\n"
            "به‌زودی این بخش شامل:\n\n"
            "🎮 PUBG Username\n"
            "🆔 PUBG ID\n"
            "🏆 مسابقات\n"
            "🥇 بردها\n"
            "💀 Killها\n"
            "⭐ امتیاز\n"
            "🏅 رتبه\n"
            "🎁 جوایز\n"
            "⚠️ اخطارها"
        )

    elif action == "leaderboard":
        text = (
            "🥇 Leaderboard\n\n"
            "رتبه‌بندی بازیکنان براساس:\n\n"
            "🏆 Wins\n"
            "💀 Kills\n"
            "⭐ Points\n\n"
            "در مرحله بعد فعال می‌شود."
        )

    elif action == "upcoming":
        text = (
            "📅 مسابقات آینده\n\n"
            "تاریخ، ساعت، Map، Mode، ظرفیت و "
            "Prize مسابقات آینده اینجا نمایش داده می‌شود."
        )

    elif action == "social":
        await query.message.reply_text(
            "📢 شبکه‌های اجتماعی رسمی NEXORA ARENA",
            reply_markup=social_keyboard()
        )
        return

    elif action == "support":
        text = (
            "🆘 RAIDEN SUPPORT\n\n"
            "🎮 مشکل مسابقه\n"
            "📝 مشکل ثبت‌نام\n"
            "🎁 مشکل جایزه\n"
            "👤 مشکل حساب\n"
            "🚫 گزارش بازیکن\n"
            "❓ سؤال دیگر\n\n"
            "📢 کانال رسمی:\n"
            "@NexoraArenaOfficial"
        )

    else:
        text = "❌ گزینه نامعتبر است."

    await query.message.reply_text(
        text,
        reply_markup=main_keyboard()
    )


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if not user_message:
        return

    history = context.user_data.get("ai_history", [])

    history.append({
        "role": "user",
        "text": user_message
    })

    conversation = ""
    for item in history[-6:]:
        conversation += f"{item['role']}: {item['text']}\n"

    try:
        response = await gemini_client.aio.models.generate_content(
            model="gemini-3.7-flash",
            contents=conversation,
            config={
                "system_instruction": (
                    "شما NEXORA، دستیار هوشمند NEXORA ARENA هستید. "
                    "با کاربران دوستانه، واضح و مفید صحبت کن. "
                    "اگر کاربر فارسی صحبت کرد، فارسی جواب بده. "
                    "از تاریخچه گفتگو برای به خاطر سپردن صحبت‌های قبلی استفاده کن."
                )
            }
        )

        answer = response.text

        history.append({
            "role": "assistant",
            "text": answer
        })

        context.user_data["ai_history"] = history[-10:]

        await update.message.reply_text(answer)

    except Exception as e:
        print("Gemini error:", e)
        await update.message.reply_text(
            "⚠️ فعلاً نتوانستم پاسخ هوشمند تولید کنم. لطفاً دوباره تلاش کنید."
        )
def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is not set"
        )

    app = Application.builder().token(
        BOT_TOKEN
    ).build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_chat
        )
    )
    
    print("RAIDEN | NEXORA ARENA is running...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
