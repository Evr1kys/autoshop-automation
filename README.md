# AutoShop Automation

Python-приложение для автоматизации магазина цифровых товаров и Steam Points.

В проекте есть:

- Telegram-бот для пользователей и администраторов;
- управление товарами, балансами и платежами;
- синхронизация данных с базой;
- фоновые задачи и обновление курсов;
- обработка покупок Steam Points;
- журналирование и мониторинг ошибок.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Перед запуском заполните значения в `.env`.
