import logging
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import CommandStart

# Конфигурация бота
BOT_TOKEN = "8594982337:AAFkcLhYzCqSj364eNAytMQu_VSINILPvAA"
ADMIN_IDS = [5000512685, 7741560076, 6986121067]

# Текст сообщений
WELCOME_MESSAGE = (
    "Здравия, вас приветствует бот для приёма анкет в клан «A terrible death.»\n\n"
    "Пришлите пожалуйста анкету, одним сообщением."
)

APPLICATION_RECEIVED = "Ваша анкета принята! Ожидайте ответа."

APPLICATION_FORWARD_TEXT = "Новая анкета от @{username} (ID: {user_id}):\n\n{text}"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

class ApplicationBot:
    def __init__(self):
        self.admin_ids = ADMIN_IDS
    
    async def send_to_admins(self, message: types.Message):
        """Отправка анкеты всем администраторам"""
        application_text = APPLICATION_FORWARD_TEXT.format(
            username=message.from_user.username or "Нет username",
            user_id=message.from_user.id,
            text=message.text
        )
        
        success_sent = 0
        for admin_id in self.admin_ids:
            try:
                await bot.send_message(admin_id, application_text)
                success_sent += 1
                logger.info(f"Анкета отправлена администратору {admin_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки администратору {admin_id}: {e}")
        
        return success_sent

# Создаем экземпляр бота
app_bot = ApplicationBot()

@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(WELCOME_MESSAGE)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_application(message: types.Message):
    """Обработчик текстовых сообщений (анкет)"""
    # Пропускаем команды
    if message.text.startswith('/'):
        return
    
    # Отправляем анкету администраторам
    success_count = await app_bot.send_to_admins(message)
    
    if success_count > 0:
        await message.answer(APPLICATION_RECEIVED)
        logger.info(f"Анкета от {message.from_user.id} обработана успешно")
    else:
        await message.answer("Произошла ошибка при отправке анкеты. Попробуйте позже.")
        logger.error(f"Не удалось отправить анкету от {message.from_user.id}")

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_other_messages(message: types.Message):
    """Обработчик не текстовых сообщений"""
    if message.content_type != types.ContentType.TEXT:
        await message.answer("Пожалуйста, отправьте анкету текстовым сообщением.")
        logger.info(f"Пользователь {message.from_user.id} отправил не текстовое сообщение: {message.content_type}")

# === ЗАПУСК ДЛЯ BEEHOST ===
async def main():
    logger.info("✅ Бот инициализирован")
    logger.info("🤖 Бот запускается на Beehost...")
    
    try:
        # Принудительно закрываем ВСЕ предыдущие сессии
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Все предыдущие сессии завершены")
        
        # Ждем немного чтобы убедиться что старые процессы завершились
        await asyncio.sleep(2)
        
        logger.info("🔄 Запускаем поллинг...")
        await dp.start_polling()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        # Перезапуск через 10 секунд
        await asyncio.sleep(10)
        await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
