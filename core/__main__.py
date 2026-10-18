"""
Точка входа для CLI KERN Witness.
Позволяет использовать команду: kern-witness <file> <action> [options]
"""
import argparse
import sys
from .witness import Witness

def main():
    parser = argparse.ArgumentParser(
        description="KERN Witness CLI - Криптографически неизменяемый журнал событий",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  kern-witness system.log log -m "Система запущена" -l INFO -M CORE
  kern-witness system.log verify
        """
    )
    parser.add_argument("file", help="Путь к файлу журнала (например, system.log)")
    parser.add_argument("action", choices=["log", "verify"], help="Действие: добавить запись или проверить целостность")
    parser.add_argument("-m", "--message", help="Текст сообщения (обязательно для действия 'log')")
    parser.add_argument("-l", "--level", default="INFO", help="Уровень события (INFO, WARNING, CRITICAL, и т.д.)")
    parser.add_argument("-M", "--module", default="CLI", help="Имя модуля-источника")

    args = parser.parse_args()

    # Инициализация Witness
    witness = Witness(args.file)

    if args.action == "log":
        if not args.message:
            print("❌ Ошибка: для действия 'log' необходим флаг -m или --message")
            sys.exit(1)
        
        try:
            sig = witness.log(args.level, args.module, args.message)
            print(f"✅ Записано: '{args.message}'")
            print(f"   Уровень: {args.level} | Модуль: {args.module}")
            print(f"   Подпись (SIG): {sig}")
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
            
    elif args.action == "verify":
        print(f"🔍 Проверка целостности журнала: {args.file}...")
        is_valid, issues = witness.verify()
        if is_valid:
            print("✅ Журнал целостен. Нарушений не обнаружено.")
        else:
            print(f"❌ Обнаружено нарушений: {len(issues)}")
            for issue in issues:
                print(f"   ⚠️  {issue}")
            sys.exit(1)

if __name__ == "__main__":
    main()
