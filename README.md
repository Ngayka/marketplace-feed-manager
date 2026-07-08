# Інструкція з запуску проєкту

## Необхідні програми

1. VSCode або будь-який інший текстовий редактор.
2. Docker та Docker Compose.
3. Google Drive Desktop (щоб синхронізувати локальну папку з хмарою).

### 1. Клонування проєкту
Скопіюйте проєкт на свій комп’ютер:

`git clone https://github.com/Ngayka/parsing_and_merged_xml_files

cd parsing_and_merged_xml_files`

## Збереження та доступ до об’єднаного XML на Google Drive

### 2. Використання Google Drive як сховища

* Встановіть Google Drive на ваш комп’ютер і авторизуйте його.
* Створіть папку для XML-файлів у Google Drive, наприклад:
* GoogleDrive/XML_merge
* Переконайтеся, що папка синхронізується з комп’ютером через Google Drive Desktop.
* Визначте повний шлях до цієї папки на вашому комп’ютері, наприклад:
* /Users/username/GoogleDrive/XML_merge

### 2. Налаштування Docker для роботи з Google Drive

У файлі docker-compose.yaml знайдіть усі рядки з коментарем #вот тут потрібно додати свій шлях до диску 
і замініть на свій шлях, наприклад:

[- /Users/username/GoogleDrive/XML_merge:/data]()

### 4. Налаштування .env

Створіть файл .env у корені проєкту і додайте потрібні змінні середовища.
Приклад:

#### Шлях до збереження об’єднаного файлу
OUTPUT_PATH=/data/merged_viatec.xml

### 5. Запуск контейнерів
У терміналі, перебуваючи в корені проєкту, запустіть:
```commandline
docker-compose up -d --build
```
Контейнери:
* 
* Redis – черга для Celery.
* Celery Worker – виконує завдання з об’єднання XML.
* Celery Beat – планувальник завдань.
* Nginx – веб-сервер для доступу до файлів.

### 6. Перевірка роботи

XML-файли будуть завантажені та об’єднані в один файл у Google Drive.

Перевірте папку: GoogleDrive/XML_merge/merged_viatec.xml.

### 7. Зупинка контейнерів
```commandline
docker-compose down
```
