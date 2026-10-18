[🇷🇺 Читать на русском](README_RU.md)

# KERN Witness

**Immutable blockchain-style event logger for autonomous systems.**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

KERN Witness is a cryptographically secure, append-only event logging system designed for autonomous robotics, IoT devices, and safety-critical applications. Each log entry contains a cryptographic hash of the previous entry, creating an immutable chain that detects tampering, deletion, or modification of any record.

## Why KERN Witness?

Traditional log files can be silently modified or deleted by attackers, corrupted by system failures, or manipulated by insiders. KERN Witness solves this by implementing a blockchain-style hash chain:

- **Tamper-proof**: Changing any single log entry breaks the entire chain
- **Deletion-proof**: Removing any entry creates a detectable gap in the hash chain
- **Offline-first**: Works without internet, cloud, or external dependencies
- **Lightweight**: Pure Python, no external dependencies beyond standard library
- **Transparent**: Open-source under AGPL-3.0, auditable by anyone

## Use Cases

- **Autonomous robotics**: Log mission events, sensor readings, and system states with cryptographic proof
- **IoT monitoring**: Record device telemetry in a way that cannot be retroactively altered
- **Safety-critical systems**: Maintain audit trails for compliance (medical devices, industrial control)
- **Incident forensics**: Prove what happened, when, and in what order, even after system compromise
- **Supply chain tracking**: Immutable record of temperature, location, and handling events

## Installation

```bash
pip install kern-witness
```

Or clone the repository:

```bash
git clone https://github.com/ontwe/kern-witness.git
cd kern-witness
pip install -e .
```

## Quick Start

```python
from core.witness import Witness

# Initialize witness with a log file
witness = Witness("my_system_log.txt")

# Log events
witness.log("INFO", "SYSTEM", "System initialized")
witness.log("WARNING", "SENSOR", "Temperature above threshold: 85°C")
witness.log("CRITICAL", "SAFETY", "Emergency shutdown triggered")

# Verify integrity
is_valid, issues = witness.verify()
if is_valid:
    print("✓ Log integrity verified")
else:
    print(f"✗ Integrity issues detected: {issues}")
```

## How It Works

Each log entry has the format:
```
[timestamp] [level] [module] message | PREV: prev_hash | SIG: current_hash
```

The `current_hash` is computed as:
```python
hash_input = f"[timestamp] [level] [module] message{prev_hash}"
current_hash = SHA256(hash_input)[:16]
```

This creates a chain where:
- Entry 1: `SIG: hash1` (PREV: "GENESIS")
- Entry 2: `SIG: hash2` (PREV: hash1)
- Entry 3: `SIG: hash3` (PREV: hash2)

If anyone modifies Entry 2, its hash changes, breaking the chain for Entry 3 and all subsequent entries.

## API Reference

### `Witness(filename: str, base_dir: Optional[str] = None)`

Initialize a witness instance.

**Parameters:**
- `filename`: Name of the log file (e.g., "system_log.txt")
- `base_dir`: Optional directory path (defaults to current directory)

### `log(level: str, module: str, message: str) -> str`

Append a new event to the log.

**Parameters:**
- `level`: Event severity ("INFO", "DEBUG", "WARNING", "CRITICAL", "ACTION", "BEACON", "MISSION", "AUTH", "SECURITY")
- `module`: Source module or component name
- `message`: Event description

**Returns:** The cryptographic signature (hash) of this entry

**Example:**
```python
signature = witness.log("CRITICAL", "POWER", "Battery level below 10%")
print(f"Logged with signature: {signature}")
```

### `verify() -> Tuple[bool, list]`

Verify the integrity of the entire log chain.

**Returns:**
- `is_valid`: True if the chain is intact, False if tampering detected
- `issues`: List of detected problems (empty if valid)

**Example:**
```python
is_valid, issues = witness.verify()
if not is_valid:
    for issue in issues:
        print(f"Integrity violation: {issue}")
```

### `get_entries(level: Optional[str] = None, module: Optional[str] = None) -> list`

Retrieve log entries with optional filtering.

**Parameters:**
- `level`: Filter by severity level (optional)
- `module`: Filter by module name (optional)

**Returns:** List of dictionaries with keys: `timestamp`, `level`, `module`, `message`, `signature`

**Example:**
```python
critical_events = witness.get_entries(level="CRITICAL")
for event in critical_events:
    print(f"[{event['timestamp']}] {event['message']}")
```

### `clear()`

Clear the log file and reset the chain. **Warning:** This is destructive and should only be used in testing.

## Security Considerations

KERN Witness provides **cryptographic integrity**, not encryption:
- Log entries are stored in plaintext (readable by anyone with file access)
- The hash chain prevents undetected modification or deletion
- For confidentiality, combine with encryption at rest (e.g., LUKS, file-level encryption)

**Attack resistance:**
- ✓ Detects modification of any log entry
- ✓ Detects deletion of any log entry
- ✓ Detects reordering of entries
- ✗ Does not prevent reading logs (use encryption for confidentiality)
- ✗ Does not prevent appending new entries (use file permissions)

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual tests:

```bash
python tests/test_witness.py
```

## Examples

See the `examples/` directory for complete usage examples:
- `basic_usage.py`: Simple logging and verification
- `iot_logging.py`: Simulated IoT sensor logging with integrity checks
- `tamper_detection.py`: Demonstrates detection of log tampering

## Part of KERN SYSTEMS

KERN Witness is a core component of the KERN SYSTEMS architecture, designed for autonomous systems that must operate reliably in extreme conditions without cloud connectivity.

**Related projects:**
- [KERN OS](https://github.com/ontwe/kern-os) - Core operating system for autonomous platforms
- [KERN Night Cycle](https://github.com/ontwe/kern-night-cycle) - Self-diagnostics service
- [KERN Three Keys](https://github.com/ontwe/kern-three-keys) - Multi-factor authentication

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

The AGPL-3.0 license ensures that any modifications or derivative works remain open-source, protecting the transparency and auditability that are core to KERN Witness's security model.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`python -m pytest tests/`)
- Code follows PEP 8 style guidelines
- New features include tests and documentation updates

## Author

Created by Semion as part of the KERN SYSTEMS project.

**Philosophy:** "ENGINEERED TO ENDURE" - Built to survive where others fail.
