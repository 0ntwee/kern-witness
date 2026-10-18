"""
Пример: Монитор "Живого инструмента"
Симулирует получение телеметрии с инструмента (например, шуруповёрта),
анализирует аномалии и логирует их в KERN Witness с человеческим интерфейсом.
"""
import time
import random
import sys
from pathlib import Path

# Добавляем путь к core, если запускаем из папки examples
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.witness import Witness

class LivingToolMonitor:
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        # ИнициализируемWitness специально для этого инструмента
        self.witness = Witness(f"{tool_name.lower().replace(' ', '_')}_log.txt")
        
        # Пороговые значения (можно калибровать под реальный инструмент)
        self.vibration_threshold = 15.0  # условные единицы
        self.current_threshold = 8.0     # Амперы
        
        print(f"🔧 [{self.tool_name}] Инициализация монитора...")
        self.witness.log("INFO", "SYSTEM", f"Монитор {self.tool_name} запущен. Ожидание данных.")

    def process_telemetry(self, vibration: float, current: float):
        """Обрабатывает поток данных с инструмента."""
        timestamp = time.strftime("%H:%M:%S")
        
        # 1. Нормальная работа
        if vibration < self.vibration_threshold and current < self.current_threshold:
            # Логируем редко, чтобы не засорять (например, каждые 10 нормальных циклов)
            if random.random() < 0.1:
                self.witness.log("DEBUG", "TELEMETRY", f"Норма: вибро={vibration:.1f}, ток={current:.1f}A")
            return

        # 2. Обнаружена аномалия!
        if vibration >= self.vibration_threshold:
            self.witness.log("WARNING", "VIBRATION", f"Аномальная вибрация: {vibration:.1f} (порог: {self.vibration_threshold})")
            self._alert_human("Кажется, инструмент работает с перегрузом или бьёт. Проверь, плотно ли сидит бит/игла.")
            
        if current >= self.current_threshold:
            self.witness.log("CRITICAL", "POWER", f"Скачок тока: {current:.1f}A (порог: {self.current_threshold}A)")
            self._alert_human("Внимание! Двигатель перегрет или заклинило. Лучше остановиться на пару минут.")

    def _alert_human(self, message: str):
        """Выводит сообщение в стиле Human-Facing Design (Принцип Человеческого лица)."""
        print(f"\n💬 [{self.tool_name}]: {message}")
        print(f"   (Событие зафиксировано в Свидетеле: {time.strftime('%H:%M:%S')})\n")

    def run_simulation(self, duration_seconds: int = 10):
        """Симулирует работу инструмента в течение заданного времени."""
        print(f"▶️  Запуск симуляции работы на {duration_seconds} секунд...\n")
        
        start_time = time.time()
        cycle = 0
        
        while time.time() - start_time < duration_seconds:
            cycle += 1
            
            # Генерируем "реалистичные" данные с шумом
            base_vibration = 5.0
            base_current = 3.0
            
            # Иногда добавляем шум
            vibration = base_vibration + random.gauss(0, 2.0)
            current = base_current + random.gauss(0, 1.0)
            
            # Каждые 5 циклов симулируем "проблему" (например, уперлись в сук или тупую иглу)
            if cycle % 5 == 0:
                vibration += random.uniform(10.0, 15.0)
                current += random.uniform(5.0, 8.0)
            
            self.process_telemetry(vibration, current)
            time.sleep(1) # 1 секунда = 1 цикл опроса
            
        print(f"⏹️  Симуляция завершена.")
        self.witness.log("INFO", "SYSTEM", "Монитор остановлен пользователем.")
        
        # Финальная проверка целостности
        print("\n🔍 Финальная проверка целостности журнала...")
        is_valid, issues = self.witness.verify()
        if is_valid:
            print("✅ Журнал целостен. Все записи на месте.")
        else:
            print(f"❌ Обнаружены проблемы: {issues}")


if __name__ == "__main__":
    # Запускаем монитор для условной "Швейной машинки" или "Шуруповёрта"
    monitor = LivingToolMonitor("Шуруповёрт")
    monitor.run_simulation(duration_seconds=12)
