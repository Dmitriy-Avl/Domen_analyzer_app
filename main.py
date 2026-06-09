"""
main.py - точка входа для анализатора конкурентов по домену
Запрашивает домен у пользователя, вызывает модули и выводит отчёт
"""

import sys
import logging
from typing import Optional, Dict, Any

# Импорт наших модулей
from api_client import quick_whois
from data_processor import process_whois_data
from report import print_report

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_domain_from_user() -> str:
    """
    Запрашивает у пользователя доменное имя
    
    Returns:
        str: очищенное доменное имя
    """
    print("\n" + "=" * 60)
    print("🔍 АНАЛИЗАТОР КОНКУРЕНТОВ ПО ДОМЕНУ")
    print("=" * 60)
    print("\nВведите адрес сайта или доменное имя для анализа.")
    print("Примеры: example.com, yandex.ru, google.com\n")
    
    while True:
        domain = input("🌐 Введите домен: ").strip()
        
        if not domain:
            print("❌ Ошибка: Домен не может быть пустым. Попробуйте снова.\n")
            continue
        
        # Очистка домена от протоколов и путей
        domain = domain.lower()
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.replace('www.', '')
        if '/' in domain:
            domain = domain.split('/')[0]
        
        # Простая валидация
        if '.' not in domain:
            print("⚠️  Внимание: Введённая строка не похожа на домен (отсутствует точка).")
            confirm = input("Продолжить? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        return domain


def analyze_domain(domain: str) -> Optional[Dict[str, Any]]:
    """
    Выполняет полный анализ домена
    
    Шаги:
    1. Получение WHOIS-данных (api_client)
    2. Обработка данных (data_processor)
    3. Формирование отчёта (будет вызвано отдельно)
    
    Args:
        domain: доменное имя для анализа
        
    Returns:
        Optional[Dict]: обработанные данные или None при ошибке
    """
    print(f"\n🔄 Выполняется анализ домена: {domain}")
    print("-" * 60)
    
    try:
        # Шаг 1: Получение WHOIS-данных через api_client
        logger.info(f"Шаг 1/2: Запрос WHOIS-данных для {domain}")
        print("📡 Запрос WHOIS-данных...")
        
        raw_data = quick_whois(domain, timeout=30)
        
        if not raw_data:
            logger.error(f"Не удалось получить данные для {domain}")
            print("❌ Не удалось получить WHOIS-данные")
            return None
        
        print("✅ WHOIS-данные получены")
        
        # Шаг 2: Обработка данных через data_processor
        logger.info(f"Шаг 2/2: Обработка WHOIS-данных для {domain}")
        print("🔄 Обработка данных...")
        
        processed_data = process_whois_data(raw_data)
        
        if not processed_data:
            logger.error(f"Не удалось обработать данные для {domain}")
            print("❌ Не удалось обработать данные")
            return None
        
        print("✅ Данные успешно обработаны")
        
        return processed_data
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        print(f"\n❌ Ошибка валидации: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при анализе домена {domain}: {e}")
        print(f"\n❌ Ошибка при анализе: {e}")
        print("\nВозможные причины:")
        print("  • Домен не существует или не зарегистрирован")
        print("  • Отсутствует подключение к интернету")
        print("  • WHOIS-сервер временно недоступен")
        return None


def main():
    """Основная функция приложения - точка входа"""
    
    # Получаем домен от пользователя
    domain = get_domain_from_user()
    
    # Выполняем анализ
    result = analyze_domain(domain)
    
    # Шаг 3: Вывод отчёта через report
    if result:
        print("\n" + "=" * 60)
        print("📊 ФОРМИРОВАНИЕ ОТЧЁТА")
        print("=" * 60)
        
        # Выводим отчёт
        print_report(result)
        
        # Предложение проанализировать другой домен
        print("\n" + "=" * 60)
        again = input("\n🔁 Проанализировать другой домен? (д/н): ").strip().lower()
        
        if again in ['д', 'да', 'y', 'yes']:
            main()  # Рекурсивный вызов для нового анализа
        else:
            print("\n👋 Спасибо за использование анализатора! До свидания!\n")
            sys.exit(0)
    else:
        print("\n❌ Анализ не выполнен.")
        retry = input("\n🔁 Попробовать другой домен? (д/н): ").strip().lower()
        
        if retry in ['д', 'да', 'y', 'yes']:
            main()
        else:
            print("\n👋 До свидания!\n")
            sys.exit(1)


# Точка входа в программу
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана пользователем (Ctrl+C)")
        print("👋 До свидания!\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Произошла критическая ошибка: {e}")
        print("Пожалуйста, перезапустите программу.\n")
        sys.exit(1)