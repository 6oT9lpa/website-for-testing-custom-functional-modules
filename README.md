# Веб-сервис для тестирование какстомных функциональных модулей
> Сервис предназначен для тестироваки разного уровня сложности алгоритмов / ИИ моделей / функции

## Возможности
* На данной стадии разработки веб-сервис позволит вам загрузить уже готовые .py файлы содеражащие определеную структуру кода, прописанных как указания во строеном редакторе кода. Также сайт позволит вам загрузить готовые тесты в json файле для проверки правильности составленного кода (тока при загрзки модуля)
* Функциональные модули, именуемые дальше как модули можно прикрепить за определенной ролью/ролями (на одну роль отстуствует ограничения в количестве, как и наоборот). На каждого клиена можно прикрепить не ограниченное количество ролей с модлями. 
* Клиент может использовать chat gpt внутри профиля, а также использовать подлеченные ему модули.
* Под каждый модуль создается уникальное окошко, которое будет завесить от указанных полей разработчиком модуля. На данный момент поле может бать текстовое так и загрузочное поле для файла.

## Начало работы 
1. Сконируйте проект с github на локальное устройство
```
git clone https://github.com/6oT9lpa/website-for-testing-custom-functional-modules.git
```
2. Установите зависимости прооекта с помощью pip, а также создайие вирутальное окружение
```
python -m venv venv
venv/Scripts/activate

pip install -r requirements.txt
```
3. Запустите проект используя команду (Python должен быть в Path)
```
python run.py
```
4. Перейдите на сайт http://127.0.0.1:5000, а также создайте и войдите в аккаунт. После чего вы попадете в профиль, от куда можно попасть прямиком в админ панели (если отсутствует роль админа нужно перейти по ссылке http://127.0.0.1:5000/admin-panel)
5. Для создания нового модуля перейдите во вкладку МОДУЛИ -> создать модуль, заполните необходимые поля. Также после создания модуля вы его можно редактировать в специальном редакторе, который реализован в веб сервисе.
6. Чтобы модуль появился у пользоватля, отнесите созданный модуль в любой роль, которые уже созданные или создайте новую. После чего добавьте роль существующему пользователю, которому нужен данный функциональный модуль для тестирования.

#### Важно: Для упрощения использования защита админ панели, а также профиля отсуствует !!!!
#### Заметка: Для использовая Chat GPT требуется ТОКЕН, без него работать он не будет. 

