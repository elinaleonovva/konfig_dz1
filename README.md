Эмулятор для языка оболочки ОС, работа которого похожа на сеанс shell в UNIX-подобной ОС.
Эмулятор запускается из реальной командной строки, а файл с виртуальной файловой системой не распаковывается у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата tar. Эмулятор должен работать в режиме CLI.
Ключами командной строки задаются:
• Имя пользователя для показа в приглашении к вводу.
• Путь к архиву виртуальной файловой системы.
В эмуляторе поддерживаются команды ls, cd и exit, а также:
1. rmdir.
2. head.
Все функции эмулятора покрыты тестами, а для каждой из поддерживаемых команд написаны по 3 теста.
