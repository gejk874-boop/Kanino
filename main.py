import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Конфигурация бота
BOT_TOKEN = "8594982337:AAFkcLhYzCqSj364eNAytMQu_VSINILPvAA"
ADMIN_IDS = [5000512685, 7741560076, 6986121067]

# Текст сообщений
WELCOME_MESSAGE = (
    "Здравия, вас приветствует бот для приёма анкет в клан «A terrible death.»\n\n"
    "Пришлите пожалуйста анкету, одним сообщением."
)

APPLICATION_RECEIVED = "Ваша анкета принята! Ожидайте ответа."

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=None)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    """Обработчик команды /start - максимально быстрый"""
    # Отправляем ответ сразу, не дожидаясь логирования
    await message.answer(WELCOME_MESSAGE)
    logger.info(f"Пользователь {message.from_user.id} отправил /start")

@dp.message()
async def handle_all_messages(message: types.Message):
    """Обработчик всех сообщений - максимально быстрый"""
    # Пропускаем команды
    if message.text and message.text.startswith('/'):
        return
    
    # Сразу отправляем подтверждение пользователю
    user_response_task = asyncio.create_task(message.answer(APPLICATION_RECEIVED))
    
    # Параллельно отправляем администраторам
    admin_tasks = []
    application_text = f"Новая анкета от @{message.from_user.username or 'Нет username'} (ID: {message.from_user.id}):\n\n{message.text or 'Не текстовое сообщение'}"
    
    for admin_id in ADMIN_IDS:
        task = asyncio.create_task(bot.send_message(admin_id, application_text))
        admin_tasks.append(task)
    
    # Ждем завершения всех задач
    try:
        await user_response_task
        await asyncio.gather(*admin_tasks, return_exceptions=True)
        logger.info(f"Анкета от {message.from_user.id} обработана")
    except Exception as e:
        logger.error(f"Ошибка обработки анкеты: {e}")

async def main():
    logger.info("🤖 Бот запускается...")
    
    try:
        # Быстрая инициализация без долгих ожиданий
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Бот готов к работе")
        
        # Запускаем поллинг сразу
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        # Быстрый перезапуск через 5 секунд
        await asyncio.sleep(5)
        await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")        
