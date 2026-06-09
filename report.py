"""
report.py - модуль для формирования и вывода отчёта в терминал
Принимает обработанные данные и выводит их в читаемом виде
"""

from typing import Dict, Any, List
from datetime import datetime


class ReportGenerator:
    """Генератор отчётов для вывода в терминал"""
    
    def __init__(self):
        """Инициализация генератора отчётов"""
        pass
    
    def generate_report(self, processed_data: Dict[str, Any]) -> str:
        """
        Генерация отчёта на основе обработанных данных
        
        Args:
            processed_data: словарь с обработанными данными от data_processor
            
        Returns:
            строка с отформатированным отчётом
        """
        # Проверка на истечение срока регистрации
        is_expired = self._check_expiration(processed_data.get('expiration_date'))
        
        lines = []
        
        # Заголовок
        lines.append("=" * 60)
        lines.append(f"📊 ОТЧЁТ ПО ДОМЕНУ: {processed_data.get('domain_name', 'Неизвестно')}")
        lines.append("=" * 60)
        lines.append("")
        
        # Основная информация
        lines.append("📋 ОСНОВНАЯ ИНФОРМАЦИЯ:")
        lines.append("-" * 40)
        lines.append(f"  🏢 Владелец/организация: {processed_data.get('owner_organization', 'Не указано')}")
        lines.append(f"  📛 Регистратор: {processed_data.get('registrar', 'Не указано')}")
        lines.append(f"  🌍 Страна: {processed_data.get('registrant_country', 'Не указано')}")
        lines.append("")
        
        # Даты
        lines.append("📅 ДАТЫ РЕГИСТРАЦИИ:")
        lines.append("-" * 40)
        lines.append(f"  📆 Дата регистрации: {processed_data.get('creation_date', 'Не указано')}")
        lines.append(f"  ⏰ Дата обновления: {processed_data.get('updated_date', 'Не указано')}")
        
        # Дата истечения с особым форматированием
        expiration = processed_data.get('expiration_date', 'Не указано')
        if is_expired:
            lines.append(f"  ⚠️  Дата истечения: {expiration} (СРОК ИСТЁК!)")
        else:
            lines.append(f"  ✅ Дата истечения: {expiration}")
        lines.append("")
        
        # Техническая информация
        lines.append("🖥️ ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:")
        lines.append("-" * 40)
        
        # Серверы имён
        name_servers = processed_data.get('name_servers', ['Не указаны'])
        if isinstance(name_servers, list):
            lines.append(f"  🌐 DNS-серверы ({len(name_servers)} шт.):")
            for ns in name_servers:
                lines.append(f"     • {ns}")
        else:
            lines.append(f"  🌐 DNS-серверы: {name_servers}")
        
        lines.append("")
        
        # Статусы
        statuses = processed_data.get('domain_status', ['Не указаны'])
        if isinstance(statuses, list):
            lines.append(f"  🔒 Статусы домена ({len(statuses)} шт.):")
            for status in statuses:
                # Очистка статуса от лишних символов
                clean_status = status.strip()
                if clean_status:
                    status_icon = self._get_status_icon(clean_status)
                    lines.append(f"     {status_icon} {clean_status}")
        else:
            lines.append(f"  🔒 Статусы домена: {statuses}")
        
        lines.append("")
        
        # Дополнительная информация и предупреждения
        lines.append("⚠️  ПРЕДУПРЕЖДЕНИЯ И РЕКОМЕНДАЦИИ:")
        lines.append("-" * 40)
        
        warnings = self._generate_warnings(processed_data)
        if warnings:
            for warning in warnings:
                lines.append(f"  {warning}")
        else:
            lines.append("  ✅ Критических проблем не обнаружено")
        
        lines.append("")
        
        # Подвал
        lines.append("=" * 60)
        lines.append(f"📅 Отчёт сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _check_expiration(self, expiration_date: str) -> bool:
        """
        Проверка, истёк ли срок регистрации домена
        
        Args:
            expiration_date: дата истечения в формате DD.MM.YYYY
            
        Returns:
            True если срок истёк, False если нет или дата не указана
        """
        if not expiration_date or expiration_date == 'Не указано':
            return False
        
        try:
            # Парсим дату в формате DD.MM.YYYY
            exp_date = datetime.strptime(expiration_date, '%d.%m.%Y')
            return exp_date < datetime.now()
        except:
            return False
    
    def _get_status_icon(self, status: str) -> str:
        """
        Возвращает иконку для статуса домена
        """
        status_lower = status.lower()
        
        if 'clienttransferprohibited' in status_lower or 'servertransferprohibited' in status_lower:
            return "🔒"
        elif 'ok' in status_lower:
            return "✅"
        elif 'inactive' in status_lower:
            return "⛔"
        elif 'pending' in status_lower:
            return "⏳"
        elif 'redemption' in status_lower:
            return "⚠️"
        elif 'delegated' in status_lower:
            return "🌐"
        elif 'verified' in status_lower:
            return "✓"
        elif 'registered' in status_lower:
            return "📝"
        else:
            return "•"
    
    def _generate_warnings(self, data: Dict[str, Any]) -> List[str]:
        """
        Генерация списка предупреждений на основе данных
        
        Returns:
            список строк с предупреждениями
        """
        warnings = []
        
        # Проверка истечения срока
        expiration = data.get('expiration_date')
        if expiration and expiration != 'Не указано':
            if self._check_expiration(expiration):
                warnings.append("❌ СРОЧНО! Срок регистрации домена ИСТЁК!")
        
        # Проверка статусов на проблемы
        statuses = data.get('domain_status', [])
        if isinstance(statuses, list):
            for status in statuses:
                status_lower = status.lower()
                if 'redemption' in status_lower:
                    warnings.append("⚠️ Домен находится в состоянии возврата (redemption period)")
                elif 'pendingdelete' in status_lower:
                    warnings.append("⚠️ Домен ожидает удаления (pending delete)")
                elif 'inactive' in status_lower:
                    warnings.append("⚠️ Домен неактивен (inactive)")
        
        # Проверка скрытия данных (есть в расширенной версии)
        if data.get('is_privacy_protected'):
            warnings.append("🛡️ Данные владельца скрыты сервисом приватности")
        
        # Рекомендация по продлению
        if expiration and expiration != 'Не указано' and not self._check_expiration(expiration):
            try:
                exp_date = datetime.strptime(expiration, '%d.%m.%Y')
                days_left = (exp_date - datetime.now()).days
                if days_left < 30 and days_left > 0:
                    warnings.append(f"⏰ Внимание! До истечения срока регистрации осталось {days_left} дней")
                elif days_left <= 0:
                    warnings.append("❌ Срок регистрации истёк! Необходимо срочное продление!")
            except:
                pass
        
        return warnings


def print_report(processed_data: Dict[str, Any]) -> None:
    """
    Упрощённая функция для вывода отчёта в консоль
    
    Args:
        processed_data: обработанные данные от data_processor
    """
    generator = ReportGenerator()
    report = generator.generate_report(processed_data)
    print(report)