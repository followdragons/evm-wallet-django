# Инструкции по настройке GitHub репозитория

## ✅ Что уже сделано:
- ✅ Git репозиторий инициализирован
- ✅ Файлы переименованы (.gitignore, README.md)
- ✅ Первый коммит создан
- ✅ Git настроен с вашими данными

## 📋 Что нужно сделать дальше:

### 1. Создать репозиторий на GitHub
1. Перейдите на https://github.com
2. Войдите в свой аккаунт
3. Нажмите кнопку "New" или "+" → "New repository"
4. Заполните данные:
   - **Repository name**: `evm-wallet-django`
   - **Description**: `Django EVM Wallet with Squad Mechanics`
   - **Visibility**: Public или Private (на ваш выбор)
   - **НЕ** добавляйте README, .gitignore или лицензию (они уже есть)
5. Нажмите "Create repository"

### 2. Подключить локальный репозиторий к GitHub
После создания репозитория GitHub покажет команды. Выполните их:

```bash
# Добавить удаленный репозиторий (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/evm-wallet-django.git

# Переименовать ветку в main (современный стандарт)
git branch -M main

# Отправить код на GitHub
git push -u origin main
```

### 3. Альтернативный способ (если у вас есть SSH ключи)
```bash
# Для SSH (если настроены ключи)
git remote add origin git@github.com:YOUR_USERNAME/evm-wallet-django.git
git branch -M main
git push -u origin main
```

## 🔧 Дополнительные настройки

### Настройка ветки по умолчанию
После первого push GitHub может предложить изменить ветку по умолчанию с `master` на `main`. Согласитесь.

### Настройка защиты ветки (опционально)
1. Перейдите в Settings → Branches
2. Добавьте правило для ветки `main`
3. Включите "Require pull request reviews before merging"

## 📁 Структура репозитория
После push ваш репозиторий будет содержать:
```
evm-wallet-django/
├── .gitignore
├── README.md
├── requirements.txt
├── manage.py
├── authentication/
├── wallet/
├── squad/
├── evm_wallet/
└── ...
```

## ⚠️ Важные замечания
- Файл `.env` НЕ будет загружен на GitHub (защищен .gitignore)
- Файл `db.sqlite3` НЕ будет загружен (защищен .gitignore)
- Папка `venv/` НЕ будет загружена (защищена .gitignore)

## 🚀 После настройки
1. Клонируйте репозиторий на других машинах: `git clone https://github.com/YOUR_USERNAME/evm-wallet-django.git`
2. Создайте файл `.env` из `.env.example`
3. Установите зависимости: `pip install -r requirements.txt`
4. Примените миграции: `python manage.py migrate`
