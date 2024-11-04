Программа-генератор сводной таблицы из оборотно-сальдовых ведомостей (ОСВ) бухгалтерских счетов из 1С

Эта программа предназначена для экономистов, аналитиков, бухгалтеров и других специалистов, которые занимаются составлением сводной финансовой и управленческой отчетности по группе компаний. Например, она может быть использована для подготовки сводного отчета о стоимости вложений во внеоборотные активы (08 счет) или дебиторской/кредиторской задолженности (60, 62, 76и пр. счета) контрагентов на определенную дату.
Программа позволяет объединить ОСВ счетов из 1С в одну сводную плоскую таблицу, что значительно упрощает дальнейший анализ и подготовку сводных отчетов.

Создание нового файла Excel

После запуска программы в папке с исходными файлами для обработки создается новый файл Excel с двумя листами: сводная таблица и таблица с отклонениями по оборотам до и после обработки. Второй лист служит для проверки правильности интеграции необходимых строк из ОСВ счетов в итоговый файл.

Тестирование на различных версиях 1С

Программа была протестирована на анализах счетов из 1С: Бухгалтерия 8.3 и 1С УПП. Она поддерживает ОСВ счетов с детализацией по субсчетам и субконто любого уровня вложенности.
Например, для составления сводного отчета о дебиторской задолженности покупателей можно выгрузить ОСВ 62 счета по каждой компании с детализацией по контрагентам и договорам.

Рекомендации по работе с программой

При работе с программой рекомендуется включать в название файлов идентификатор компании, так как в результирующем файле будет столбец с названием файла, по которому можно идентифицировать каждую компанию в группе.

Уровни иерархии

Важно отметить, что выгруженные в файлы Excel ОСВ счетов должны содержать уровни иерархии (группировки строк, которые скрываются/отображаются с помощью кнопок + и – слева в полях). По этим уровням программа будет разворачивать вложенные данные в плоский вид таблицы. Поэтому ОСВ счетов следует выгружать через меню "Сохранить как" в 1С.

Запуск программы

Перед запуском программы убедитесь, что нет открытых файлов Excel.

Ошибки и улучшения

Обратите внимание, что алгоритм скрипта не может учесть все особенности различных вариаций выгрузок анализов счетов из 1С, что может привести к ошибкам в работе программы. Если вы столкнулись с какими-либо ошибками или хотите предложить улучшения, пожалуйста, отправьте информацию об ошибках (вместе с образцами выгрузок из 1С, которые не были корректно обработаны программой) или предложения по улучшению по контакту в телеграм @kaetosh.

Создание .exe файла с помощью pyinstaller

используйте команду:
pyinstaller --onefile --collect-all pyfiglet --icon=icon.ico main.py