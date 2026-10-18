"""
KERN Witness v2
Immutable blockchain-style event logger for autonomous systems.
Part of KERN SYSTEMS. Licensed under AGPL-3.0.
"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


class Witness:
    """
    Блокчейн-журнал событий с криптографической цепочкой хешей.
    Удаление или изменение любой записи ломает всю цепочку.
    """
    VALID_LEVELS = {"INFO", "DEBUG", "WARNING", "CRITICAL", "ACTION", "BEACON", "MISSION", "AUTH", "SECURITY"}
    GENESIS_HASH = "GENESIS"
    
    def __init__(self, filename: str = "witness_log.txt", base_dir: Optional[str] = None):
        if base_dir:
            self.filepath = Path(base_dir) / filename
        else:
            self.filepath = Path(filename)
        self.last_hash = self._load_last_hash()
    
    def _load_last_hash(self) -> str:
        if not self.filepath.exists():
            return self.GENESIS_HASH
        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            return self.GENESIS_HASH
        last_line = lines[-1].strip()
        if " | SIG: " in last_line:
            return last_line.rsplit(" | ", 1)[1].replace("SIG: ", "").strip()
        return self.GENESIS_HASH
    
    def log(self, level: str, module: str, message: str) -> str:
        if level not in self.VALID_LEVELS:
            raise ValueError(f"Недопустимый уровень: {level}. Допустимые: {self.VALID_LEVELS}")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        raw_string = f"[{timestamp}] [{level}] [{module}] {message}"
        
        hash_input = f"{raw_string}{self.last_hash}"
        current_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:16]
        
        final_entry = f"{raw_string} | PREV: {self.last_hash} | SIG: {current_hash}\n"
        
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(final_entry)
        
        self.last_hash = current_hash
        return current_hash
    
    def verify(self) -> Tuple[bool, list]:
        if not self.filepath.exists():
            return False, ["Файл журнала не найден"]
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            return False, ["Журнал пуст"]
        
        issues = []
        prev_hash = self.GENESIS_HASH
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or " | SIG: " not in line:
                issues.append(f"Строка {i}: некорректный формат")
                continue
            
            # rsplit делит строку максимум 2 раза СПРАВА, защищая сообщение от символов '|'
            parts = line.rsplit(" | ", 2)
            if len(parts) != 3:
                issues.append(f"Строка {i}: ожидалось 3 части, найдено {len(parts)}")
                continue
            
            raw_string = parts[0]
            prev_part = parts[1]
            sig_part = parts[2]
            
            if not prev_part.startswith("PREV: ") or not sig_part.startswith("SIG: "):
                issues.append(f"Строка {i}: некорректный формат PREV/SIG")
                continue
            
            saved_prev_hash = prev_part[6:].strip()
            saved_sig = sig_part[5:].strip()
            
            if saved_prev_hash != prev_hash:
                issues.append(f"Строка {i}: разрыв цепочки! Ожидался PREV: {prev_hash}, найдено: {saved_prev_hash}")
            
            hash_input = f"{raw_string}{saved_prev_hash}"
            calculated_sig = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:16]
            
            if calculated_sig != saved_sig:
                issues.append(f"Строка {i}: хеш не совпадает! Ожидался: {calculated_sig}, найдено: {saved_sig}")
            
            prev_hash = saved_sig
        
        return len(issues) == 0, issues
    
    def get_entries(self, level: Optional[str] = None, module: Optional[str] = None) -> list:
        if not self.filepath.exists():
            return []
        
        entries = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or " | SIG: " not in line:
                    continue
                
                parts = line.rsplit(" | ", 2)
                if len(parts) != 3:
                    continue
                
                raw_string = parts[0]
                signature = parts[2][5:].strip()
                
                bracket_parts = raw_string.split("] [")
                if len(bracket_parts) < 3:
                    continue
                
                timestamp = bracket_parts[0].lstrip("[")
                entry_level = bracket_parts[1]
                module_and_message = bracket_parts[2]
                
                module_end = module_and_message.find("] ")
                if module_end == -1:
                    continue
                
                entry_module = module_and_message[:module_end]
                message = module_and_message[module_end + 2:]
                
                if level and entry_level != level:
                    continue
                if module and entry_module != module:
                    continue
                
                entries.append({
                    "timestamp": timestamp,
                    "level": entry_level,
                    "module": entry_module,
                    "message": message,
                    "signature": signature
                })
        
        return entries
    
    def clear(self):
        """Очистка журнала. Внимание: деструктивная операция, только для тестов."""
        self.filepath.write_text("", encoding="utf-8")
        self.last_hash = self.GENESIS_HASH
    
    def get_genesis_hash(self) -> str:
        if not self.filepath.exists():
            return self.GENESIS_HASH
        with open(self.filepath, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        if " | SIG: " in first_line:
            return first_line.rsplit(" | ", 1)[1].replace("SIG: ", "").strip()
        return self.GENESIS_HASH
    
    def __repr__(self):
        return f"Witness(filepath={self.filepath.name}, last_hash={self.last_hash[:8]}...)"
