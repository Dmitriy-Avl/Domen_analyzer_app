"""
api_client.py - модуль для запроса WHOIS-данных домена
"""

import whois
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WHOISAPIClient:
    """Клиент для работы с WHOIS API"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        
    def fetch_whois_data(self, domain: str) -> Dict[str, Any]:
        """
        Получение WHOIS-данных для домена
        """
        domain = self._clean_domain(domain)
        self._validate_domain(domain)
        
        logger.info(f"Запрос WHOIS-данных для домена: {domain}")
        
        try:
            # Выполняем WHOIS-запрос
            w = whois.whois(domain, timeout=self.timeout)
            
            # Извлекаем данные напрямую, без сложной нормализации
            result = {}
            
            # Доменное имя
            if w.domain_name:
                result['domain_name'] = w.domain_name[0] if isinstance(w.domain_name, list) else w.domain_name
            else:
                result['domain_name'] = domain
            
            # Регистратор
            result['registrar'] = w.registrar if w.registrar else None
            
            # Организация и владелец
            result['org'] = w.org if w.org else None
            result['name'] = w.name if w.name else None
            
            # Даты
            result['creation_date'] = self._format_date(w.creation_date)
            result['expiration_date'] = self._format_date(w.expiration_date)
            result['updated_date'] = self._format_date(w.updated_date)
            
            # DNS серверы
            if w.name_servers:
                if isinstance(w.name_servers, list):
                    result['name_servers'] = [ns for ns in w.name_servers if ns]
                else:
                    result['name_servers'] = [w.name_servers]
            else:
                result['name_servers'] = []
            
            # Статусы
            if w.status:
                if isinstance(w.status, list):
                    result['status'] = [s for s in w.status if s]
                else:
                    result['status'] = [w.status]
            else:
                result['status'] = []
            
            # Страна
            result['country'] = w.country if w.country else None
            
            logger.info(f"Данные для {domain} успешно получены")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка для {domain}: {str(e)}")
            raise Exception(f"Ошибка при получении WHOIS-данных для {domain}: {str(e)}") from e
    
    def _format_date(self, date_value):
        """Форматирование даты в ISO строку"""
        if not date_value:
            return None
        
        if isinstance(date_value, list):
            date_value = date_value[0]
        
        if isinstance(date_value, datetime):
            return date_value.isoformat()
        
        return str(date_value)
    
    def _clean_domain(self, domain: str) -> str:
        """Очистка доменного имени"""
        domain = domain.strip().lower()
        domain = domain.replace('http://', '').replace('https://', '')
        if domain.startswith('www.'):
            domain = domain[4:]
        if '/' in domain:
            domain = domain.split('/')[0]
        return domain
    
    def _validate_domain(self, domain: str) -> None:
        """Валидация формата домена"""
        if not domain or len(domain) < 3:
            raise ValueError(f"Некорректный домен: '{domain}' - слишком короткий")
        
        if '.' not in domain:
            raise ValueError(f"Некорректный домен: '{domain}' - отсутствует точка")


def quick_whois(domain: str, timeout: int = 30) -> Dict[str, Any]:
    """Упрощённая функция для быстрого получения WHOIS-данных"""
    client = WHOISAPIClient(timeout=timeout)
    return client.fetch_whois_data(domain)