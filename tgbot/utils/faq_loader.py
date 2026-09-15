#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FAQ Loader - Утилита для загрузки FAQ из .md файла в базу данных
"""

import os
import asyncio
from pathlib import Path

class FAQLoader:
    def __init__(self):
        self.faq_file_path = Path(__file__).parent.parent.parent / "FAQ.md"
    
    def read_faq_file(self) -> str:
        """Читает FAQ из .md файла"""
        try:
            if self.faq_file_path.exists():
                with open(self.faq_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                return content
            else:
                print(f"❌ FAQ файл не найден: {self.faq_file_path}")
                return ""
        except Exception as e:
            print(f"❌ Ошибка чтения FAQ файла: {e}")
            return ""
    
    async def update_faq_in_db(self) -> bool:
        """Обновляет FAQ в базе данных"""
        try:
            # Импортируем DB только здесь, чтобы избежать циркулярного импорта
            from tgbot.data.loader import DB
            
            faq_content = self.read_faq_file()
            if not faq_content:
                return False
            
            # Конвертируем в HTML для лучшего отображения
            faq_html = convert_md_to_html(faq_content)
            
            # Обновляем настройки в базе данных
            await DB.update_settings(faq=faq_html)
            print("✅ FAQ успешно обновлен в базе данных")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления FAQ в БД: {e}")
            return False
    
    async def get_current_faq(self) -> str:
        """Получает текущий FAQ из базы данных"""
        try:
            from tgbot.data.loader import DB
            settings = await DB.get_settings()
            return settings.faq or ""
        except Exception as e:
            print(f"❌ Ошибка получения FAQ из БД: {e}")
            return ""

# Функция для быстрого обновления FAQ
async def update_faq_from_file():
    """Быстрая функция для обновления FAQ из файла"""
    loader = FAQLoader()
    return await loader.update_faq_in_db()

# Функция для получения FAQ в HTML формате
def convert_md_to_html(content: str) -> str:
    """Конвертирует базовый Markdown в HTML для Telegram"""
    if not content:
        return ""
    
    # Базовая конвертация Markdown в HTML
    import re
    
    # Заголовки
    content = re.sub(r'^# (.+)', r'<b>\1</b>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)', r'<b>\1</b>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)', r'<b>\1</b>', content, flags=re.MULTILINE)
    
    # Жирный текст
    content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
    
    # Курсив
    content = re.sub(r'\*(.+?)\*', r'<i>\1</i>', content)
    
    # Код
    content = re.sub(r'`(.+?)`', r'<code>\1</code>', content)
    
    # Удаляем лишние символы Markdown
    content = re.sub(r'^> ', '', content, flags=re.MULTILINE)
    content = re.sub(r'^---$', '━━━━━━━━━━━━━━━━━━━━', content, flags=re.MULTILINE)
    
    return content

if __name__ == "__main__":
    async def main():
        loader = FAQLoader()
        
        print("📖 Чтение FAQ из файла...")
        faq_content = loader.read_faq_file()
        
        if faq_content:
            print(f"✅ Прочитано {len(faq_content)} символов")
            print("📝 Обновление FAQ в базе данных...")
            
            success = await loader.update_faq_in_db()
            if success:
                print("🎉 FAQ успешно обновлен!")
            else:
                print("❌ Ошибка обновления FAQ")
        else:
            print("❌ Не удалось прочитать FAQ")
    
    asyncio.run(main())
