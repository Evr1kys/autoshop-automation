# -*- coding: utf-8 -*-
"""
Система пагинации для правовых документов AutoShop
"""

import os
import re


class DocumentPagination:
    """Класс для управления пагинацией документов"""
    
    def __init__(self):
        self.cache = {}  # Кэш для загруженных документов
    
    def split_text_into_pages(self, text: str, max_chars: int = 3800) -> list:
        """Разбивает текст на страницы с учетом лимита символов"""
        if not text or len(text) <= max_chars:
            return [text] if text else []
        
        # Сначала разбиваем по разделам (заголовки с ##)
        sections = re.split(r'\n(?=## )', text)
        pages = []
        current_page = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Если секция помещается в текущую страницу
            if len(current_page + '\n\n' + section) <= max_chars:
                if current_page:
                    current_page += '\n\n' + section
                else:
                    current_page = section
            else:
                # Сохраняем текущую страницу (если есть)
                if current_page:
                    pages.append(current_page)
                
                # Если секция слишком большая, разбиваем её
                if len(section) > max_chars:
                    section_pages = self._split_large_section(section, max_chars)
                    pages.extend(section_pages[:-1])  # Все кроме последней
                    current_page = section_pages[-1]  # Последняя становится текущей
                else:
                    current_page = section
        
        # Добавляем последнюю страницу
        if current_page:
            pages.append(current_page)
        
        return pages if pages else [text]
    
    def _split_large_section(self, section: str, max_chars: int) -> list:
        """Разбивает большую секцию на части"""
        pages = []
        lines = section.split('\n')
        current_page = ""
        
        for line in lines:
            # Если строка + текущая страница помещаются
            if len(current_page + '\n' + line) <= max_chars:
                if current_page:
                    current_page += '\n' + line
                else:
                    current_page = line
            else:
                # Сохраняем текущую страницу
                if current_page:
                    pages.append(current_page)
                
                # Если строка слишком длинная, разбиваем по словам
                if len(line) > max_chars:
                    word_pages = self._split_long_line(line, max_chars)
                    pages.extend(word_pages[:-1])
                    current_page = word_pages[-1]
                else:
                    current_page = line
        
        if current_page:
            pages.append(current_page)
        
        return pages if pages else [section]
    
    def _split_long_line(self, line: str, max_chars: int) -> list:
        """Разбивает длинную строку по словам"""
        if len(line) <= max_chars:
            return [line]
        
        words = line.split(' ')
        pages = []
        current_line = ""
        
        for word in words:
            if len(current_line + ' ' + word) <= max_chars:
                if current_line:
                    current_line += ' ' + word
                else:
                    current_line = word
            else:
                if current_line:
                    pages.append(current_line)
                current_line = word
        
        if current_line:
            pages.append(current_line)
        
        return pages if pages else [line]
    
    def _find_break_position(self, text: str, start: int, max_end: int) -> int:
        """Находит оптимальную позицию для разрыва страницы"""
        # Ищем разрывы в порядке приоритета
        search_area = text[start:max_end]
        
        # 1. Конец абзаца (двойной перенос строки)
        last_paragraph = search_area.rfind('\n\n')
        if last_paragraph > len(search_area) * 0.7:  # Если найден в последних 30%
            return start + last_paragraph + 2
        
        # 2. Конец предложения
        last_sentence = max(
            search_area.rfind('. '),
            search_area.rfind('.\n'),
            search_area.rfind('! '),
            search_area.rfind('?\n')
        )
        if last_sentence > len(search_area) * 0.6:  # Если найден в последних 40%
            return start + last_sentence + 1
        
        # 3. Конец строки
        last_newline = search_area.rfind('\n')
        if last_newline > len(search_area) * 0.5:  # Если найден в последних 50%
            return start + last_newline + 1
        
        # 4. Последний пробел
        last_space = search_area.rfind(' ')
        if last_space > 0:
            return start + last_space + 1
        
        # 5. Принудительный разрыв
        return max_end
    
    def format_page_text(self, page_text: str, page_num: int, total_pages: int, title: str) -> str:
        """Форматирует текст страницы с заголовком и информацией о пагинации"""
        
        # Очищаем заголовок от лишних символов
        clean_title = re.sub(r'^#+\s*', '', title).strip()
        
        if total_pages == 1:
            # Если только одна страница, не показываем номер
            return f"""{clean_title}

{page_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 Полный документ"""
        else:
            # Для многостраничных документов показываем номер страницы
            return f"""{clean_title}

📄 <b>Страница {page_num} из {total_pages}</b>

{page_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 {page_num}/{total_pages} | 📖 {len(page_text)} символов"""
    
    def get_page_info(self, pages: list, current_page: int) -> dict:
        """Возвращает информацию о текущей странице"""
        if not pages or current_page < 1 or current_page > len(pages):
            return None
        
        return {
            'current_page': current_page,
            'total_pages': len(pages),
            'has_prev': current_page > 1,
            'has_next': current_page < len(pages),
            'page_text': pages[current_page - 1],
            'chars_count': len(pages[current_page - 1])
        }


def load_document_pages(file_path: str, max_chars: int = 3200):
    """Загружает документ и разбивает на страницы"""
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Определяем заголовок из содержимого файла
        lines = content.split('\n')
        title = "Документ"  # Заголовок по умолчанию
        
        # Ищем заголовок в первых строках
        for line in lines[:5]:
            if line.strip() and any(marker in line for marker in ['📜', '🔒', '📄', 'УСЛОВИЯ', 'ПОЛИТИКА', 'СОГЛАШЕНИЕ']):
                # Очищаем HTML теги для заголовка
                title = re.sub(r'<[^>]+>', '', line.strip())
                break
        
        # Создаем объект пагинации
        pagination = DocumentPagination()
        
        # Разбиваем на страницы
        pages = pagination.split_text_into_pages(content, max_chars)
        
        return pages, title
        
    except Exception as e:
        print(f"Ошибка загрузки документа {file_path}: {e}")
        return [], "Ошибка загрузки"


def get_document_pages(doc_type: str, max_chars: int = 3200):
    """Получает страницы документа с кэшированием"""
    
    # Определяем файлы документов
    doc_files = {
        'terms': 'terms_of_service.md',
        'privacy': 'privacy_policy.md',
        'agreement': 'user_agreement.md'
    }
    
    if doc_type not in doc_files:
        return [], "Документ не найден"
    
    # Путь к файлу документа
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(base_path, doc_files[doc_type])
    
    # Загружаем страницы
    return load_document_pages(file_path, max_chars)
