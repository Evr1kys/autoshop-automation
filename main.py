import asyncio
import colorama
import sys
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from tgbot.handlers import userRouter, adminRouter
from tgbot.data.loader import dp, bot, adButtonRouter, scheduler
from tgbot.middlewares import setup_middlewares
from tgbot.utils.utils import check_rates, check_contests, check_updates, clear_stats_day, clear_stats_week, check_steam_api_status, enable_steam_if_balance_sufficient
from tgbot.data.config import DB
from tgbot.utils.models import async_main

colorama.init()

async def scheduler_start():
    scheduler.add_job(clear_stats_week, "cron", day_of_week="mon", hour=00, args=[DB])
    scheduler.add_job(clear_stats_day, "cron", hour=00, args=[DB])
    scheduler.add_job(check_rates, 'cron', hour=00, args=[DB, bot])
    
    # Steam API задачи - проверяем каждые 30 минут
    scheduler.add_job(check_steam_api_status, 'interval', minutes=30, args=[DB, bot], id='steam_check')
    
    # Проверяем возможность включения Steam API каждые 2 часа (если он был отключен из-за низкого баланса)
    scheduler.add_job(enable_steam_if_balance_sufficient, 'interval', hours=2, args=[DB, bot], id='steam_enable_check')

async def main():
    try:
        # Запускаем настройку и проверку базы данных
        await async_main()
    except (ConnectionRefusedError, OSError) as e:
        print(colorama.Fore.RED + "ОШИБКА: Не удается подключиться к базе данных PostgreSQL!")
        print(colorama.Fore.YELLOW + "Проверьте:")
        print(colorama.Fore.YELLOW + "1. Запущен ли сервер PostgreSQL (команда: pg_ctl start)")
        print(colorama.Fore.YELLOW + "2. Правильность настроек подключения к БД в конфигурации")
        print(colorama.Fore.YELLOW + "3. Доступность порта (обычно 5432)")
        print(colorama.Fore.YELLOW + "4. Файрвол не блокирует подключение")
        print(colorama.Fore.RED + f"Детали ошибки: {e}" + colorama.Fore.RESET)
        sys.exit(1)
    except (OperationalError, SQLAlchemyError) as e:
        print(colorama.Fore.RED + "ОШИБКА: Проблема с базой данных!")
        print(colorama.Fore.YELLOW + "Возможные причины:")
        print(colorama.Fore.YELLOW + "1. Неверные учетные данные для подключения к БД")
        print(colorama.Fore.YELLOW + "2. База данных не существует")
        print(colorama.Fore.YELLOW + "3. Недостаточно прав доступа")
        print(colorama.Fore.RED + f"Детали ошибки: {e}" + colorama.Fore.RESET)
        sys.exit(1)
    except Exception as e:
        print(colorama.Fore.RED + f"НЕОЖИДАННАЯ ОШИБКА при инициализации: {e}")
        print(colorama.Fore.YELLOW + "Тип ошибки:", type(e).__name__ + colorama.Fore.RESET)
        sys.exit(1)
    
    # Запускаем задания
    loop = asyncio.get_event_loop()
    loop.create_task(check_contests(DB, bot))
    loop.create_task(check_rates(DB, bot))
    loop.create_task(check_updates())
    
    # Первоначальная проверка Steam API при запуске
    loop.create_task(check_steam_api_status(DB, bot))
    
    # Подключаем мидлвари к роутерам
    setup_middlewares(userRouter)
    setup_middlewares(adButtonRouter)
    setup_middlewares(adminRouter)
    
    # Запуск заданий
    await scheduler_start()
    scheduler.start()
    
    print(colorama.Fore.GREEN + "=====================================")
    print(colorama.Fore.RED + "Bot Was Started")
    print(colorama.Fore.LIGHTBLUE_EX + "Developer: https://t.me/ToSa_LZT")
    print(colorama.Fore.LIGHTBLUE_EX + "TG Channel: https://t.me/ToSa_GG")
    print(colorama.Fore.GREEN + "=====================================" + colorama.Fore.RESET)
    
    # Удаляем ненужный нам вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    
    # В дистпетчер включаем наши роутеры и запускаем бота
    dp.include_routers(userRouter, adminRouter, adButtonRouter)    
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print(colorama.Fore.YELLOW + "\n🛑 Получен сигнал остановки (Ctrl+C)")
        print(colorama.Fore.BLUE + "🔄 Корректно завершаем работу бота...")
        scheduler.shutdown()
        print(colorama.Fore.GREEN + "✅ Бот остановлен" + colorama.Fore.RESET)
    except Exception as e:
        print(colorama.Fore.RED + f"❌ Ошибка во время работы бота: {e}" + colorama.Fore.RESET)
        scheduler.shutdown()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(colorama.Fore.GREEN + "👋 До свидания!" + colorama.Fore.RESET)
