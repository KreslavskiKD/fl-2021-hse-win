Внимание -- экстеншн из 5 задания возможно сломался после заливки на гит так как:
warning: LF will be replaced by CRLF in dfa-lang/.vscode/launch.json.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/.vscodeignore.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/CHANGELOG.md.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/README.md.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/language-configuration.json.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/package.json.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/syntaxes/DFA.tmLanguage.json.
The file will have its original line endings in your working directory
warning: LF will be replaced by CRLF in dfa-lang/vsc-extension-quickstart.md.
The file will have its original line endings in your working directory

# Язык для описания конечных детерминированных автоматов.

Есть несколько сущностей: **символы**, **алфавиты** и **автоматы**. 

Ключевые слова:
	`def`, `class`, `override`, `fun`, `return`
Подсвечивыаются в VS Code с моим экстеншеном.

Расширение для файлов --	.dfa (blabla.dfa)

## Символы.
Есть базовый класс `Symbol`, от которого унаследованы базовые типы `Char`, `Int`, `String`, `Boolean`.

Можно сделать свой символ, унаследовав его от `Symbol`. Тогда придётся переопределить функцию сравнения (`==` оно же `equals`).
Так же у сиволов есть метод `inRange(from, to)`, который опционален, но если вы хотите его переопределить, 
то вам надо будет сначала переопределить сравнение (`>` или `<`, метод `more`, `less`). У интов понятно какое сравнение,
у чаров по коду в юникоде, у строк лексиграфически.
Подсвечивыаются в VS Code с моим экстеншеном только символы, которые строки.

## Алфавиты.
Алфавит представлен классом `Alphabet<T>`, где `T` это какой-то класс, унаследованный от `Symbol`, то есть какой-то символ (логично).
Наследоваться от алфавита нельзя (пока не вижу в этом смысла). Задавать алфавиты можно перечислением символов
через запятую внутри блока из фигурных скобок `{ }`, либо методом `inRange`. Для кастомных символов тоже можно 
задавать алфавиты перечислением символов через запятую внутри блока из фигурных скобок либо с помощью метода `describe`,
внутри которого следующий синтаксис: 
`имя_поля_класса_символа from имя_алфавита_откуда_брать_значения_для_этого_поля`
Если полей несколько, то перечислять через запятую. 
Ключевые слова: `from`
Подсвечивыаются в VS Code с моим экстеншеном отдельно (другим цветом) от основных ключевых слов.

## Пример на символы и алфавиты:
```
class MySymb(a: String, b: Int, c: Int) : Symbol {
	override fun equals(ps: MySymb) : Boolean {
		return ((this.a == ps.a) && (this.b == ps.b) && (this.c == ps.c))
	}
}

def alphabetInt: Alphabet<Int> = Int.inRange(0, 100)

def alphabetString: Alphabet<String> = {"for", "if", "else", "while"}

def myAlphabet: Alphabet<MySymb> = Alphabet.describe {
	a from alphabetString,
	b, c from alphabetInt
}
```
## Автоматы.
    Для реализации автоматов есть класс `Automaton`. У него есть несколько методов:
* Инициализационные методы: 
	* `setAlphabet(alphabet: Alphabet<T>)` 	-- фиксирует алфавит автомата
	* `describe { <body> }`       			-- собственно описывает состояния автомата и переходы между ними

    Какой вид у `<body>`:

    Ключевые слова: `start`, `else`, `deadend`, `alphabet`, `terminal`, `itself`
    * `start`     -- стартовое состояние
	* `else`      -- множество всех символов алфавита, для которых не прописасн отдельно переход
	* `deadend`   -- состояние-тупик, из которого не прийти ни в какое другое. Не терминальное
	* `alphabet`  -- множество всех символов алфавита
	* `terminal`  -- после него идёт свой блок `{ <body> }`, в котором слово `terminal` запрещено.
	* `itself` -- то же состояние, что и слева от стрелки
	Подсвечивыаются в VS Code с моим экстеншеном отдельно (другим цветом) от основных ключевых слов.

	Описание состояний:
    ```
		condition_from_name	symbol_group1 -> condition_to_name_1
					symbol_group2 -> condition_to_name_2
					etc...
    ```

	Между именем состояния откуда и группой символов должен быть пробел, между группой символов и стрелкой -- тоже.
	Между стрелкой и именем куда -- пробел. Если нужно использовать зарезервированные символы, то можно сделать
	`Char(' ')` для пробела, например, или `String("else")` для символа `else`.

Методы обработки:
* `changeState(symbol: Symbol)`			    -- изменяет состояние автомата по символу
* `checkWord(word: Array<Symbol>) : Boolean`	-- определяет принадлежит ли слово языку, который этот автомат распознаёт

(так как этот раздел не относится к понятию "описание языка", то я про него особо много и не запаривался)

## Общие синтаксические правила.
* Переменные создаются через ключевое слово `def`. Пример:
```
	def alphabetIntValence: Alphabet<Int> = Int.inRange(1, 8)
```
* Для переопределения методов используются ключевые слова `override fun`, для создания новых -- `fun`. Пример:
```
	class PairSymb(a: String, b: Int = 1) : Symbol {
		override fun equals(ps: PairSymb) : Boolean {
			return (a == ps.a && b == ps.b)
		}
	}
```
Так же выше привдены примеры использования `return` и `class`.


# Описание подсветки

## Что хотелось подсветить

1. Ключевые слова всей программы: `def`, `class`, `override`, `fun`, `return`

2. Ключевые слова блока `describe` для алфавитов: `from`

3. Ключевые слова блока describe для автоматов: `start`, `else`, `deadend`, `alphabet`, `terminal`

4. Строковые литералы.


## Оформление

* Группы 1, (2, 3), 4 посвечиваются разными цветами (2 и 3 одинаковым, отличным от цвета группы 1 и 4, у групп 1 и 4 тоже разные цвета)

* Строковые литералы, содержащие ключевые слова подсвечиваются как строковые литералы, а не как ключевые слова.





















