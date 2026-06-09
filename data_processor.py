"""
data_processor.py - модуль для обработки WHOIS-данных
Извлекает из сырого ответа унифицированные поля для отчёта
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import OrderedDict


class WHOISDataProcessor:
    """Обработчик WHOIS-данных"""
    
    # Поля, которые будут в финальном отчёте
    OUTPUT_FIELDS = [
        'domain_name',
        'owner_organization',  # владелец или организация
        'registrar',           # регистратор
        'creation_date',       # дата регистрации
        'expiration_date',     # дата истечения
        'updated_date',        # дата последнего обновления
        'name_servers',        # серверы имён
        'domain_status',       # статус домена
        'registrant_country'   # страна регистранта
    ]
    
    def __init__(self):
        """Инициализация процессора"""
        pass
    
    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка сырых WHOIS-данных и извлечение нужных полей
        
        Args:
            raw_data: сырые данные от WHOISAPIClient
            
        Returns:
            Dict с обработанными данными по указанным полям
        """
        processed = OrderedDict()
        
        # 1. Доменное имя
        processed['domain_name'] = self._extract_domain_name(raw_data)
        
        # 2. Владелец или организация (приоритет: org > name)
        processed['owner_organization'] = self._extract_owner(raw_data)
        
        # 3. Регистратор
        processed['registrar'] = self._extract_registrar(raw_data)
        
        # 4. Дата регистрации
        processed['creation_date'] = self._extract_date(raw_data, 'creation_date')
        
        # 5. Дата истечения
        processed['expiration_date'] = self._extract_date(raw_data, 'expiration_date')
        
        # 6. Дата последнего обновления
        processed['updated_date'] = self._extract_date(raw_data, 'updated_date')
        
        # 7. Серверы имён
        processed['name_servers'] = self._extract_name_servers(raw_data)
        
        # 8. Статус домена (обработка и очистка)
        processed['domain_status'] = self._extract_status(raw_data)
        
        # 9. Страна регистранта
        processed['registrant_country'] = self._extract_country(raw_data)
        
        return processed
    
    def _extract_domain_name(self, data: Dict[str, Any]) -> str:
        """Извлечение доменного имени"""
        domain = data.get('domain_name')
        if not domain:
            return 'Не указано'
        
        # Если пришёл список, берём первый элемент
        if isinstance(domain, list):
            domain = domain[0] if domain else 'Не указано'
        
        return str(domain).lower()
    
    def _extract_owner(self, data: Dict[str, Any]) -> str:
        """
        Извлечение владельца или организации
        Приоритет: org > name
        """
        org = data.get('org')
        if org and org != 'None' and str(org).strip():
            if isinstance(org, list):
                org = org[0] if org else None
            return str(org)
        
        name = data.get('name')
        if name and name != 'None' and str(name).strip():
            if isinstance(name, list):
                name = name[0] if name else None
            return str(name)
        
        # Проверка дополнительных полей, которые могут содержать владельца
        for field in ['registrant_name', 'registrant_organization', 'owner']:
            if field in data and data[field]:
                val = data[field]
                if isinstance(val, list):
                    val = val[0] if val else None
                if val and str(val).strip():
                    return str(val)
        
        return 'Не указано'
    
    def _extract_registrar(self, data: Dict[str, Any]) -> str:
        """Извлечение регистратора"""
        registrar = data.get('registrar')
        if not registrar:
            return 'Не указано'
        
        if isinstance(registrar, list):
            registrar = registrar[0] if registrar else 'Не указано'
        
        # Очистка от лишних символов
        registrar = str(registrar).strip()
        
        # Убираем URL из названия регистратора, если есть
        if 'http://' in registrar or 'https://' in registrar:
            # Оставляем только название до URL
            parts = re.split(r'\s+http', registrar)
            registrar = parts[0].strip()
        
        return registrar if registrar else 'Не указано'
    
    def _extract_date(self, data: Dict[str, Any], field_name: str) -> str:
        """
        Извлечение и форматирование даты
        
        Args:
            data: словарь с данными
            field_name: имя поля ('creation_date', 'expiration_date', 'updated_date')
        """
        date_value = data.get(field_name)
        
        if not date_value:
            return 'Не указано'
        
        # Если это список, берём первый элемент
        if isinstance(date_value, list):
            date_value = date_value[0] if date_value else None
        
        if not date_value:
            return 'Не указано'
        
        # Если уже строка в ISO формате
        if isinstance(date_value, str):
            # Пробуем распарсить для красивого вывода
            try:
                # Попытка разных форматов
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                    try:
                        dt = datetime.strptime(date_value, fmt)
                        return dt.strftime('%d.%m.%Y')
                    except ValueError:
                        continue
                # Если не распарсилось, возвращаем как есть
                return date_value
            except:
                return date_value
        
        # Если объект datetime
        if isinstance(date_value, datetime):
            return date_value.strftime('%d.%m.%Y')
        
        # Если что-то другое, пробуем преобразовать в строку
        return str(date_value).split()[0] if date_value else 'Не указано'
    
    def _extract_name_servers(self, data: Dict[str, Any]) -> List[str]:
        """Извлечение списка DNS-серверов"""
        ns = data.get('name_servers', [])
        
        if not ns:
            return ['Не указаны']
        
        # Убеждаемся, что это список
        if not isinstance(ns, list):
            ns = [ns]
        
        # Очистка и фильтрация пустых значений
        clean_ns = []
        for server in ns:
            if server and isinstance(server, str):
                server = server.strip().lower()
                if server:
                    clean_ns.append(server)
        
        return clean_ns if clean_ns else ['Не указаны']
    
    def _extract_status(self, data: Dict[str, Any]) -> List[str]:
        """
        Извлечение и обработка статусов домена
        Возвращает список статусов
        """
        status = data.get('status', [])
        
        if not status:
            return ['Не указаны']
        
        # Убеждаемся, что это список
        if not isinstance(status, list):
            status = [status]
        
        # Очистка статусов
        clean_status = []
        for stat in status:
            if stat and isinstance(stat, str):
                # Убираем лишние символы и пробелы
                stat = stat.strip()
                # Убираем возможные URL или лишний текст в скобках
                if ' ' in stat:
                    stat = stat.split()[0]
                if stat and stat not in clean_status:
                    clean_status.append(stat)
        
        return clean_status if clean_status else ['Не указаны']
    
    def _extract_country(self, data: Dict[str, Any]) -> str:
        """Извлечение страны регистранта"""
        country = data.get('country')
        
        if not country:
            return 'Не указано'
        
        if isinstance(country, list):
            country = country[0] if country else 'Не указано'
        
        # Приводим к нормальному виду
        country = str(country).strip()
        
        # Словарь сокращений стран (можно расширить)
        country_codes = {
            'US': 'United States',
            'UK': 'United Kingdom',
            'GB': 'United Kingdom',
            'RU': 'Russia',
            'DE': 'Germany',
            'FR': 'France',
            'CN': 'China',
            'JP': 'Japan',
            'CA': 'Canada',
            'AU': 'Australia',
            'BR': 'Brazil',
            'IN': 'India'
        }
        
        # Если это код страны, преобразуем в полное название
        if country.upper() in country_codes:
            country = country_codes[country.upper()]
        
        return country if country else 'Не указано'


def process_whois_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Упрощённая функция для обработки WHOIS-данных
    
    Args:
        raw_data: сырые данные от WHOISAPIClient
        
    Returns:
        Dict с обработанными данными
    """
    processor = WHOISDataProcessor()
    return processor.process(raw_data)