#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Принудительное обновление и синхронизация баланса Steam API
"""

import sqlite3
import os
import time

def force_sync_steam_balance():
    """Принудительно синхронизируем баланс Steam API"""
    
    print("🔄 Принудительная синхронизация баланса Steam API")
    print("=" * 60)
    
    db_path = "tgbot/data/database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных {db_path} не найдена")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем текущие настройки
        cursor.execute("""
            SELECT 
                current_balance,
                api_price_per_point,
                price_per_point,
                low_balance_threshold,
                is_enabled,
                last_balance_check
            FROM steam_api_config 
            WHERE id = 1
        """)
        
        row = cursor.fetchone()
        
        if row:
            old_balance = row[0]
            api_price = row[1]
            admin_price = row[2]
            threshold = row[3]
            is_enabled = row[4]
            last_check = row[5]
            
            print(f"📊 Текущее состояние в БД:")
            print(f"  • Баланс: {old_balance:.2f} ₽")
            print(f"  • API цена: {api_price:.4f} ₽/очко")
            print(f"  • Админская цена: {admin_price:.4f} ₽/очко")  
            print(f"  • Порог: {threshold:.2f} ₽")
            print(f"  • Включено: {'Да' if is_enabled else 'Нет'}")
            print(f"  • Последняя проверка: {last_check or 'Никогда'}")
            
            # Правильные значения
            correct_balance = 498.65
            correct_api_price = 0.005
            correct_admin_price = 0.015
            correct_threshold = 10.0
            current_timestamp = str(int(time.time()))
            
            print(f"\n🔧 Принудительное обновление всех параметров...")
            
            # Обновляем ВСЕ параметры одновременно
            cursor.execute("""
                UPDATE steam_api_config 
                SET 
                    current_balance = ?,
                    api_price_per_point = ?,
                    price_per_point = ?,
                    low_balance_threshold = ?,
                    is_enabled = 1,
                    last_balance_check = ?,
                    last_price_check = ?
                WHERE id = 1
            """, (correct_balance, correct_api_price, correct_admin_price, 
                  correct_threshold, current_timestamp, current_timestamp))
            
            conn.commit()
            
            # Проверяем обновление
            cursor.execute("""
                SELECT 
                    current_balance,
                    api_price_per_point,
                    price_per_point,
                    low_balance_threshold,
                    is_enabled
                FROM steam_api_config 
                WHERE id = 1
            """)
            
            updated_row = cursor.fetchone()
            
            if updated_row:
                new_balance = updated_row[0]
                new_api_price = updated_row[1] 
                new_admin_price = updated_row[2]
                new_threshold = updated_row[3]
                new_enabled = updated_row[4]
                
                print(f"✅ Параметры обновлены:")
                print(f"  • Баланс: {old_balance:.2f}₽ → {new_balance:.2f}₽")
                print(f"  • API цена: {api_price:.4f}₽ → {new_api_price:.4f}₽")
                print(f"  • Админская цена: {admin_price:.4f}₽ → {new_admin_price:.4f}₽")
                print(f"  • Порог: {threshold:.2f}₽ → {new_threshold:.2f}₽")
                print(f"  • Система: {'Включена' if new_enabled else 'Выключена'}")
                
                # Рассчитываем баланс в очках для отображения
                balance_points = new_balance / new_api_price
                
                print(f"\n💎 Правильное отображение баланса:")
                print(f"  • В рублях: {new_balance:.2f} ₽")
                print(f"  • В очках: {balance_points:,.0f} очков")
                print(f"  • Формат: '{new_balance:.2f} ₽ ({balance_points:,.0f} очков)'")
                
                # Проверяем достаточность баланса
                is_sufficient = new_balance >= new_threshold
                print(f"\n🎯 Проверка работоспособности:")
                print(f"  • Баланс {new_balance:.2f}₽ {'≥' if is_sufficient else '<'} порог {new_threshold:.2f}₽")
                print(f"  • Результат: {'✅ Система должна работать' if is_sufficient else '❌ Требуется пополнение'}")
                
                if is_sufficient:
                    # Примеры заказов
                    min_cost = 100 * new_api_price  # 100 очков минимум
                    max_orders = int(new_balance / min_cost)
                    
                    print(f"  • Минимальный заказ: 100 очков = {min_cost:.2f}₽")
                    print(f"  • Максимум заказов: {max_orders}")
                    
                    # Прибыль с заказов
                    for points in [1000, 5000, 10000]:
                        user_pays = points * new_admin_price
                        api_costs = points * new_api_price
                        profit = user_pays - api_costs
                        
                        print(f"  • {points} очков: пользователь {user_pays:.0f}₽, прибыль {profit:.0f}₽")
        
        else:
            print("❌ Настройки Steam API не найдены")
            return False
        
        conn.close()
        
        print(f"\n" + "=" * 60)
        print("🎉 Принудительная синхронизация завершена!")
        print("\n📋 Что нужно сделать дальше:")
        print("  1. Перезапустить бота (Ctrl+C и запустить снова)")
        print("  2. Или дождаться следующего автоматического обновления (через 30 мин)")
        print("  3. Проверить админскую панель Steam Points")
        
        print(f"\n🚀 После перезапуска баланс должен отображаться как:")
        print(f"  💎 Баланс Steam API: 498.65 ₽ (99,730 очков)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = force_sync_steam_balance()
    
    if success:
        print("\n✅ Синхронизация выполнена! Перезапустите бота.")
    else:
        print("\n💥 Ошибка синхронизации!")
        exit(1)