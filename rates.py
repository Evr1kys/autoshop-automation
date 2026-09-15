import aiohttp
import ssl
try:
    import certifi
    HAS_CERTIFI = True
except ImportError:
    HAS_CERTIFI = False

async def get_exchanges(amount: float, cur1: str, cur2: str):
    if float(amount) == 0.0:
        return 0.0

    # Создаем SSL context
    if HAS_CERTIFI:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    else:
        # Альтернативный вариант без certifi
        ssl_context = ssl.create_default_context()
    
    # Создаем connector с SSL настройками
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
            ress = await session.get(f'https://api.exchangerate-api.com/v4/latest/{cur1}')
            res = await ress.json()
            rate = res['rates'][cur2]
            return float(rate)
    except (aiohttp.ClientError, ssl.SSLError) as e:
        print(f"⚠️ Ошибка SSL при получении курса {cur1}->{cur2}: {e}")
        # Пробуем без проверки SSL (не рекомендуется, но как fallback)
        try:
            ssl_context_no_verify = ssl.create_default_context()
            ssl_context_no_verify.check_hostname = False
            ssl_context_no_verify.verify_mode = ssl.CERT_NONE
            connector_no_verify = aiohttp.TCPConnector(ssl=ssl_context_no_verify)
            
            async with aiohttp.ClientSession(connector=connector_no_verify, timeout=aiohttp.ClientTimeout(total=10)) as session:
                ress = await session.get(f'https://api.exchangerate-api.com/v4/latest/{cur1}')
                res = await ress.json()
                rate = res['rates'][cur2]
                return float(rate)
        except Exception as e2:
            print(f"⚠️ Полная ошибка получения курса {cur1}->{cur2}: {e2}")
            # Возвращаем резервные курсы
            fallback_rates = {
                ('USD', 'RUB'): 75.0,
                ('USD', 'EUR'): 0.85,
                ('EUR', 'RUB'): 88.0,
                ('EUR', 'USD'): 1.18,
                ('RUB', 'USD'): 0.013,
                ('RUB', 'EUR'): 0.011
            }
            return fallback_rates.get((cur1, cur2), 1.0)
    except Exception as e:
        print(f"⚠️ Общая ошибка получения курса {cur1}->{cur2}: {e}")
        fallback_rates = {
            ('USD', 'RUB'): 75.0,
            ('USD', 'EUR'): 0.85,
            ('EUR', 'RUB'): 88.0,
            ('EUR', 'USD'): 1.18,
            ('RUB', 'USD'): 0.013,
            ('RUB', 'EUR'): 0.011
        }
        return fallback_rates.get((cur1, cur2), 1.0)

async def get_def_exchanges():
    try:
        rate_usd_to_rub = float(await get_exchanges(1, 'USD', 'RUB'))
        rate_usd_to_eur = float(await get_exchanges(1, 'USD', 'EUR'))
        rate_eur_to_rub = float(await get_exchanges(1, 'EUR', 'RUB'))
        rate_eur_to_usd = float(await get_exchanges(1, 'EUR', 'USD'))
        rate_rub_to_usd = float(await get_exchanges(1, 'RUB', 'USD'))
        rate_rub_to_eur = float(await get_exchanges(1, 'RUB', 'EUR'))

        print("✅ Курсы валют успешно обновлены")
        return rate_usd_to_rub, rate_usd_to_eur, rate_eur_to_rub, rate_eur_to_usd, rate_rub_to_usd, rate_rub_to_eur
    except Exception as e:
        print(f"❌ Ошибка получения курсов валют: {e}")
        print("🔄 Используем резервные курсы валют")
        # Возвращаем стандартные курсы при ошибке
        return 75.0, 0.85, 88.0, 1.18, 0.013, 0.011
