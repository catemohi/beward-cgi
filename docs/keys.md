## Общее описание
Управление ключами для панелей Beward

## Доступные команды:
1. `eqmup`: Загрузить ключи на панель из EQM файла
2. `d2j`: Выгрузить ключи с панели в JSON
3. `lj`: Загрузить ключи на панель из JSON

---

### Команда `eqmup`

#### Описание
Загрузить ключи на панель из EQM файла

#### Использование
```
python3 keys.py eqmup <IP> --filepath путь/к/файлу
```

#### Атрибуты
- `ip`: IP адрес панели (обязательный атрибут)
- `--username`: Имя пользователя
- `--password`: Пароль пользователя
- `--filepath`: Путь к файлу с ключами

#### Примеры
1. Загрузка ключей на панель из EQM файла:
   ```
   python3 keys.py eqmup 192.168.0.1 --filepath path/to/file.eqm
   ```
   
2. Загрузка ключей на панель из EQM файла с указанием имени пользователя и пароля:
   ```
   python3 keys.py eqmup 192.168.0.1 --username admin --password 123456 --filepath path/to/file.eqm
   ```

3. Загрузка ключей на панель из EQM файла с указанием имени пользователя и пароля:
   ```
   python3 keys.py eqmup 192.168.0.1 --username admin --password 123456 --filepath path/to/file.eqm
   ```

4. Загрузка ключей на панель из EQM файла с указанием имени пользователя и пароля, а также с выводом справочной информации:
   ```
   python3 keys.py eqmup 192.168.0.1 --username admin --password 123456 --filepath path/to/file.eqm --help
   ```

---

### Команда `d2j`

#### Описание
Выгрузить ключи с панели в JSON

#### Использование
```
python3 keys.py d2j <IP> --filepath путь/к/файлу
```

#### Атрибуты
- `ip`: IP адрес панели (обязательный атрибут)
- `--username`: Имя пользователя
- `--password`: Пароль пользователя
- `--filepath`: Путь сохранения файла (по умолчанию текущая директория)
- `--format_type`: Формат ключей (выбор из ["RFID", "MIFARE"], по умолчанию "MIFARE")

#### Примеры
1. Выгрузка ключей с панели в JSON:
   ```
   python3 keys.py d2j 192.168.0.1 --filepath path/to/output.json
   ```

2. Выгрузка ключей с панели в JSON с указанием формата ключей:
   ```
   python3 keys.py d2j 192.168.0.1 --filepath path/to/output.json --format_type RFID
   ```

3. Выгрузка ключей с панели в JSON с указанием имени пользователя и пароля:
   ```
   python3 keys.py d2j 192.168.0.1 --username admin --password 123456 --filepath path/to/output.json
   ```

4. Выгрузка ключей с панели в JSON с указанием формата ключей и пути сохранения файла:
   ```
   python3 keys.py d2j 192.168.0.1 --filepath path/to/output.json --format_type MIFARE --username admin --password 123456
   ```

---

### Команда `lj`

#### Описание
Загрузить ключи на панель из JSON

#### Использование
```
python3 keys.py lj <IP> --filepath путь/к/файлу
```

#### Атрибуты
- `ip`: IP адрес панели (обязательный атрибут)
- `--username`: Имя пользователя
- `--password`: Пароль пользователя
- `--filepath`: Путь к файлу

#### Примеры
1. Загрузка ключей на панель из JSON:
   ```
   python3 keys.py lj 192.168.0.1 --filepath path/to/input.json
   ```
2. Загрузка ключей на панель из JSON с указанием имени пользователя и пароля:
   ```
   python3 keys.py lj 192.168.0.1 --username admin --password 123456 --filepath path/to/input.json
   ```
---

**Версия**: 1.0, Nikita Vasilev (catemohi@gmail.com), 03.11.2023
