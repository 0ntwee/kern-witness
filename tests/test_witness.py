"""Тесты для KERN Witness v2."""
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.witness import Witness


def test_basic_logging():
    print("🧪 Тест 1: Базовая запись с цепочкой хешей")
    witness = Witness("test_log_v2.txt")
    witness.clear()
    
    sig1 = witness.log("INFO", "TEST", "Сообщение 1")
    sig2 = witness.log("INFO", "TEST", "Сообщение 2")
    sig3 = witness.log("CRITICAL", "TEST", "Сообщение 3")
    
    assert sig1 != sig2 != sig3
    print("   ✅ Создано 3 записи с уникальными хешами")
    
    entries = witness.get_entries()
    assert len(entries) == 3
    print("   ✅ Все записи корректно парсятся")


def test_chain_integrity():
    print("\n🧪 Тест 2: Проверка целостности цепочки")
    witness = Witness("test_log_v2.txt")
    witness.clear()
    
    witness.log("INFO", "TEST", "Запись 1")
    witness.log("INFO", "TEST", "Запись 2")
    witness.log("INFO", "TEST", "Запись 3")
    
    is_valid, issues = witness.verify()
    assert is_valid, f"Ожидалась валидность, но найдены проблемы: {issues}"
    print("   ✅ Цепочка хешей цела")


def test_tampering_detection():
    print("\n🧪 Тест 3: Обнаружение подделки (изменение записи)")
    witness = Witness("test_log_v2.txt")
    witness.clear()
    
    witness.log("INFO", "TEST", "Запись 1")
    witness.log("INFO", "TEST", "Запись 2")
    witness.log("INFO", "TEST", "Запись 3")
    
    with open("test_log_v2.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    lines[1] = lines[1].replace("Запись 2", "ПОДДЕЛКА")
    
    with open("test_log_v2.txt", "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    is_valid, issues = witness.verify()
    assert not is_valid, "Ожидалось обнаружение подделки"
    assert len(issues) >= 1, "Должна быть хотя бы одна проблема"
    print(f"   ✅ Подделка обнаружена: {len(issues)} проблем в цепочке")


def test_deletion_detection():
    print("\n🧪 Тест 4: Обнаружение удаления записи")
    witness = Witness("test_log_v2.txt")
    witness.clear()
    
    witness.log("INFO", "TEST", "Запись 1")
    witness.log("INFO", "TEST", "Запись 2")
    witness.log("INFO", "TEST", "Запись 3")
    
    with open("test_log_v2.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    del lines[1]  # Удаляем вторую строку
    
    with open("test_log_v2.txt", "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    is_valid, issues = witness.verify()
    assert not is_valid, "Ожидалось обнаружение удаления"
    assert any("разрыв цепочки" in issue.lower() for issue in issues), \
        "Должен быть обнаружен разрыв цепочки"
    print("   ✅ Удаление записи обнаружено: разрыв цепочки зафиксирован")


if __name__ == "__main__":
    test_basic_logging()
    test_chain_integrity()
    test_tampering_detection()
    test_deletion_detection()
    print("\n🎉 Все тесты KERN Witness v2 пройдены!")
