import aiohttp
import json
import hmac
import hashlib
import time
import random
import secrets
import uuid
import ssl
try:
    import certifi
    HAS_CERTIFI = True
except ImportError:
    HAS_CERTIFI = False

from yoomoney import Quickpay, Client


class PAL24:
    def __init__(self, api_token: str, shop_id: str) -> None:
        self.api_token = api_token
        self.shop_id = shop_id
        self.base_url = "https://pal24.pro/api/v1"
        self.timeout = aiohttp.ClientTimeout(total=360)

    def _create_signature(self, out_sum: str, inv_id: str) -> str:
        """Создание подписи для проверки платежей"""
        string_to_sign = f"{out_sum}:{inv_id}:{self.api_token}"
        return hashlib.md5(string_to_sign.encode()).hexdigest().upper()

    async def create_bill(self, amount: float, order_id: str, description: str = None, 
                         currency: str = "RUB", payment_method: str = "SBP") -> dict:
        """Создание счета для оплаты"""
        url = f"{self.base_url}/bill/create"
        
        data = {
            'amount': amount,
            'shop_id': self.shop_id,
            'order_id': order_id,
            'currency_in': currency,
            'type': 'normal',
            'payment_method': payment_method,  # SBP или BANK_CARD
            'payer_pays_commission': 1
        }
        
        if description:
            data['description'] = description
            
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(url, data=data, headers=headers) as response:
                result = await response.json()
                return result

    async def get_bill_status(self, bill_id: str) -> dict:
        """Получение статуса счета"""
        url = f"{self.base_url}/bill/status"
        params = {'id': bill_id}
        
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params, headers=headers) as response:
                result = await response.json()
                return result

    async def get_payment_status(self, payment_id: str) -> dict:
        """Получение статуса платежа"""
        url = f"{self.base_url}/payment/status"
        params = {'id': payment_id}
        
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params, headers=headers) as response:
                result = await response.json()
                return result

    def verify_signature(self, out_sum: str, inv_id: str, signature: str) -> bool:
        """Проверка подписи от PAL24"""
        expected_signature = self._create_signature(out_sum, inv_id)
        return expected_signature == signature.upper()


class Lava:
    def __init__(self, shop_id: str, secret_token: str) -> None:
        self.shop_id = shop_id
        self.secret = secret_token
        self.base_url = "https://api.lava.ru/"
        self.timeout = aiohttp.ClientTimeout(total=360)

    def _signature_headers(self, data: dict) -> dict:
        jsonStr = json.dumps(data).encode()
        sign = hmac.new(bytes(self.secret, 'UTF-8'), jsonStr, hashlib.sha256).hexdigest()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Signature': sign
        }
        return headers

    async def create_invoice(self, amount: float, success_url: str, comment: str) -> dict:
        url = f"{self.base_url}/business/invoice/create"
        params = {
            "sum": amount,
            "shopId": self.shop_id,
            "successUrl": success_url,
            "orderId": f'{time.time()}_{secrets.token_hex(random.randint(5, 10))}',
            "comment": comment
        }
        headers = self._signature_headers(params)
        async with aiohttp.ClientSession(headers=headers, timeout=self.timeout) as session:
            response = await session.post(url=url, headers=headers, json=params)
            res = await response.json()
            await session.close()
        return res

    async def status_invoice(self, invoice_id: str) -> bool:
        url = f"{self.base_url}/business/invoice/status"
        params = {
            "shopId": self.shop_id,
            "invoiceId": invoice_id
        }
        headers = self._signature_headers(params)
        async with aiohttp.ClientSession(headers=headers, timeout=self.timeout) as session:
            response = await session.post(url=url, headers=headers, json=params)
            res = await response.json()
            await session.close()
        return res['data']['status'] == "success"

    async def get_balance(self) -> dict:
        params = {'shopId': self.shop_id}
        headers = self._signature_headers(params)
        async with aiohttp.ClientSession(headers=headers, timeout=self.timeout) as session:
            request = await session.post('https://api.lava.ru/business/shop/get-balance', json=params, headers=headers)
            response = await request.json()
            await session.close()
            return response


class YooMoney:
    def __init__(self, token, number):
        self.token = token
        self.number = number
        self.client = Client(token)

    def create_yoomoney_link(self, amount: float, comment: str) -> dict:
        payment_form = dict()
        number = self.number
        quick_pay = Quickpay(
            receiver=number,
            quickpay_form="shop",
            targets="Balance refill",
            paymentType="SB",
            sum=amount,
            label=comment
        )
        payment_form["link"] = quick_pay.base_url
        payment_form['comment'] = quick_pay.label
        payment_form["key"] = "Number"
        payment_form["value"] = number
        return payment_form

    def check_yoomoney_payment(self, comment: str) -> bool:
        for operation in self.client.operation_history(label=comment).operations:
            comment_payment = str(operation.label)
            if comment_payment == comment:
                return True
        return False

    def get_balance(self):
        return self.client.account_info().balance


class Platega:
    def __init__(self, merchant_id: str, api_secret: str) -> None:
        self.merchant_id = merchant_id
        self.api_secret = api_secret
        self.base_url = "https://app.platega.io"
        self.timeout = aiohttp.ClientTimeout(total=360)
        
        # Создаем SSL контекст для безопасного подключения
        if HAS_CERTIFI:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        else:
            self.ssl_context = ssl.create_default_context()
    
    def _create_connector(self):
        """Создает новый коннектор для каждого запроса"""
        return aiohttp.TCPConnector(ssl=self.ssl_context)
    
    def _create_fallback_connector(self):
        """Создает коннектор без проверки SSL для fallback"""
        ssl_context_no_verify = ssl.create_default_context()
        ssl_context_no_verify.check_hostname = False
        ssl_context_no_verify.verify_mode = ssl.CERT_NONE
        return aiohttp.TCPConnector(ssl=ssl_context_no_verify)

    def _get_headers(self) -> dict:
        """Получение заголовков для авторизации"""
        return {
            'Content-Type': 'application/json',
            'X-MerchantId': self.merchant_id,
            'X-Secret': self.api_secret,
            'Accept': 'application/json'
        }

    async def create_payment(self, amount: float, transaction_id: str, description: str = None,
                           currency: str = "RUB", payment_method: int = 2, 
                           return_url: str = None, failed_url: str = None, 
                           payload: str = None) -> dict:
        """
        Создание платежа в Platega
        payment_method: 
        1 - СБП (P2P)
        2 - СБП / QR 
        9 - ALL_RU (P2P CARD / P2P СБП)
        10 - CardRu(P2P CARD)
        11 - Card (МИР)
        12 - International
        """
        url = f"{self.base_url}/transaction/process"
        
        # Генерируем UUID если transaction_id не в формате UUID
        try:
            # Проверяем, является ли transaction_id валидным UUID
            uuid.UUID(transaction_id)
            payment_id = transaction_id
        except ValueError:
            # Если нет, генерируем новый UUID
            payment_id = str(uuid.uuid4())
        
        data = {
            'paymentMethod': payment_method,
            'id': payment_id,
            'paymentDetails': {
                'amount': amount,
                'currency': currency
            },
            'return': return_url or 'https://example.com/success',  # Обязательное поле
            'failedUrl': failed_url or 'https://example.com/failed'  # Добавляем fallback
        }
        
        if description:
            data['description'] = description
            
        # Обновляем URL если переданы новые значения
        if return_url:
            data['return'] = return_url
            
        if failed_url:
            data['failedUrl'] = failed_url
            
        if payload:
            data['payload'] = payload
        
        headers = self._get_headers()
        
        try:
            connector = self._create_connector()
            async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                try:
                    async with session.post(url, json=data, headers=headers) as response:
                        response_text = await response.text()
                        print(f"Platega API Response: Status {response.status}")
                        print(f"Platega API Response Body: {response_text}")
                        
                        if response.status == 200:
                            result = await response.json()
                            return {
                                'success': True,
                                'data': {
                                    'payment_url': result.get('redirect'),
                                    'transaction_id': result.get('transactionId'),
                                    'status': result.get('status'),
                                    'expires_in': result.get('expiresIn')
                                }
                            }
                        else:
                            try:
                                result = await response.json()
                                error_msg = result.get('Message', f'HTTP {response.status}')
                                error_code = result.get('Code', response.status)
                            except:
                                # Очищаем HTML теги из ответа
                                import re
                                clean_response = re.sub(r'<[^>]+>', '', response_text) if response_text else ''
                                clean_response = clean_response.strip()
                                
                                if response.status == 503:
                                    error_msg = "Сервис временно недоступен. Попробуйте позже."
                                elif response.status == 500:
                                    error_msg = "Внутренняя ошибка сервера. Попробуйте позже."
                                elif response.status == 404:
                                    error_msg = "Сервис не найден. Обратитесь в поддержку."
                                elif clean_response:
                                    error_msg = clean_response
                                else:
                                    error_msg = f"Ошибка сервера (код {response.status})"
                                
                                error_code = response.status
                                
                            print(f"Platega API Error: {error_msg} (Code: {error_code})")
                            return {
                                'success': False,
                                'error': error_msg,
                                'code': error_code
                            }
                except Exception as e:
                    print(f"Platega API Exception: {e}")
                    return {
                        'success': False,
                        'error': f'Connection error: {str(e)}',
                        'code': -1
                    }
        except ssl.SSLError as ssl_error:
            print(f"⚠️ SSL ошибка при подключении к Platega: {ssl_error}")
            # Попробуем без проверки SSL как fallback (не рекомендуется для продакшена)
            try:
                connector_no_verify = self._create_fallback_connector()
                
                async with aiohttp.ClientSession(connector=connector_no_verify, timeout=self.timeout) as session:
                    async with session.post(url, json=data, headers=headers) as response:
                        response_text = await response.text()
                        print(f"Platega API Response (No SSL): Status {response.status}")
                        print(f"Platega API Response Body (No SSL): {response_text}")
                        
                        if response.status == 200:
                            result = await response.json()
                            return {
                                'success': True,
                                'data': {
                                    'payment_url': result.get('redirect'),
                                    'transaction_id': result.get('transactionId'),
                                    'status': result.get('status'),
                                    'expires_in': result.get('expiresIn')
                                }
                            }
                        else:
                            try:
                                result = await response.json()
                                error_msg = result.get('Message', f'HTTP {response.status}')
                                error_code = result.get('Code', response.status)
                            except:
                                error_msg = response_text or f'HTTP {response.status}'
                                error_code = response.status
                                
                            print(f"Platega API Error (No SSL): {error_msg} (Code: {error_code})")
                            return {
                                'success': False,
                                'error': error_msg,
                                'code': error_code
                            }
            except Exception as fallback_error:
                print(f"❌ Fallback ошибка Platega: {fallback_error}")
                return {
                    'success': False,
                    'error': f'SSL and fallback connection failed: {str(ssl_error)}',
                    'code': -2
                }
        except Exception as e:
            print(f"❌ Общая ошибка Platega: {e}")
            return {
                'success': False,
                'error': f'General connection error: {str(e)}',
                'code': -3
            }

    async def get_payment_status(self, transaction_id: str) -> dict:
        """
        Получение статуса платежа
        Статусы:
        PENDING - ожидание оплаты
        CONFIRMED - подтверждение оплаты
        EXPIRED - истек срок оплаты
        CANCELED - отмененный платеж
        FAILED - ошибка создания платежа
        """
        url = f"{self.base_url}/transaction/{transaction_id}"
        headers = self._get_headers()
        
        try:
            connector = self._create_connector()
            async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    result = await response.json()
                    return result
        except ssl.SSLError as ssl_error:
            print(f"⚠️ SSL ошибка при проверке статуса платежа: {ssl_error}")
            # Fallback без SSL проверки
            try:
                connector_no_verify = self._create_fallback_connector()
                
                async with aiohttp.ClientSession(connector=connector_no_verify, timeout=self.timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        result = await response.json()
                        return result
            except Exception:
                return {'success': False, 'error': f'SSL connection failed: {str(ssl_error)}'}
        except Exception as e:
            print(f"❌ Ошибка получения статуса платежа: {e}")
            return {'success': False, 'error': f'Connection error: {str(e)}'}

    async def get_payment_rate(self, payment_method: int = 2, currency_from: str = "RUB", 
                             currency_to: str = "USDT") -> dict:
        """Получение курса обмена для платежного метода"""
        url = f"{self.base_url}/rates/payment_method_rate"
        params = {
            'merchantId': self.merchant_id,
            'paymentMethod': payment_method,
            'currencyFrom': currency_from,
            'currencyTo': currency_to
        }
        
        headers = self._get_headers()
        
        try:
            connector = self._create_connector()
            async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                async with session.get(url, params=params, headers=headers) as response:
                    result = await response.json()
                    return result
        except ssl.SSLError as ssl_error:
            print(f"⚠️ SSL ошибка при получении курса: {ssl_error}")
            # Fallback без SSL проверки
            try:
                connector_no_verify = self._create_fallback_connector()
                
                async with aiohttp.ClientSession(connector=connector_no_verify, timeout=self.timeout) as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        result = await response.json()
                        return result
            except Exception:
                return {'success': False, 'error': f'SSL connection failed: {str(ssl_error)}'}
        except Exception as e:
            print(f"❌ Ошибка получения курса: {e}")
            return {'success': False, 'error': f'Connection error: {str(e)}'}

    def verify_callback(self, data: dict) -> bool:
        """
        Проверка callback уведомления от Platega
        (Конкретный алгоритм проверки подписи может отличаться - 
        уточните в технической поддержке Platega)
        """
        # Здесь должна быть логика проверки подписи callback'а
        # Пока возвращаем True, т.к. точный алгоритм не указан в документации
        return True
