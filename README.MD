# CYAO character generator tools

#### cyoa_eval.py
Evaluates XML files to generate CYOA characters.

#### cyoa_display.py
Displays data evaluated with cyao_eval.py

## Usage

```console
$ python ./cyoa_eval.py [-h] path
$ python ./cyoa_display.py [-h] data_path disp_path
```
```console
positional arguments:
  path/data_path	Path to the XML file to be evaluated
  disp_path		Path to the XML file describing the display format
```
```console
optional arguments:
  -h, --help  show this help message and exit
```
##### Example

```sh
$ python ./cyoa_display.py ./amg.xml ./amg_disp.xml
```

## Writing XML files
General information about the structure of XML files can be found [here](https://www.w3schools.com/xml/).
Remember that tags are case-sensitive.

* [Eval Tags](#eval-tags)
	* [CYOA](#cyoa)
	* [Constants](#constants)
	* [Questions](#questions)
		* [Options](#options)
	* [Random](#random)
	* [Repeats](#repeats)
	* [Comparisons](#comparisons)
	* [Macros](#macros)
* [Display Tags](#display-tags)
	* [Constants](#display-constants)
	* [Fields](#display-fields)

### Eval Tags
Tags used by cyoa_eval.py

#### CYOA
```xml
<cyoa>
...
</cyoa>
```
Encloses the entire structure. The actual tag is irrelevant and may be replaced to better suite your project.

#### Constants
```xml
<constant name="name" value="value" [conflict="overwrite"] />
```
Saves the value specified in `value` in the field specifed in `name`.
If the field already has a value, behaviour dpends on `conflict`:
* `"overwrite"`: The previous value is overwritten. Default behaviour.
* `"add"`: The previous and new values are treated as integers and added. Causes errors when either value is not an integer.
* `"append"`: Appends the new value to the old one.
* `"stack"`: Appends the new value in a new line and indented. This behaviour might change in future versions.
* `"skip"`: Discards the new value.

##### Example
```xml
<constant name="STR" value="5" />
<constant name="STR" value="2" conflict="add" />
```
This results in the field `"STR"` having the value `7`.

#### Questions
```xml
<question text="text" [name="name" [conflict="overwrite"]] [type="select"] >
	...
</question>
```
Asks the user the question specified in `text`. If an invalid answer is given, the question is repeated.
If `"name"` is given, the answer is saved in the respective field. Conflicts are resolved as for [constants](#constants).
The behaviour also depends on the value of `type`:
* `"select"`: Allows the user to select between multiple options given as [option](#options) tags. The selection can be made by number or by giving a unambigous leading substring (e.g. "mag" can be entered to select "Magic", if no other option starts with "mag"). This selection is case-insensitve. Default behaviour.
* `"input"`: Prompts the user to enter a value for the field given in `name`. Option tags are ignored.
* `"yesno"`: Automatically provides the options "Yes" and "No", with "Yes" as default if an empty input is received. The first two [option](#options) tags are treated as associated with these values, regardless of their value. Further [option](#options) tags are ignored.

##### Options
```xml
<option [value="value"]>
	...
</option>
```
If the question is of `type` `"select"`, the `value` must be specified.
When an option is selected, all subtags are evaluated. Subtags of not selected options are ignored.

##### Examples
```xml
<question text="Do you want to name your character?" type="yesno">
    <option>
        <question text="Enter name:" type="input" name="Name" />
    </option>
    <option>
        <constant name="Name" value="None" />
    </option>
</question>
```
Asks the use if they want to name their character. If the answer is "Yes", the user is prompted to input a name, otherwise the name is set to "None".
Note that the answer of the first question is not saved in a field, since no `name` is given.
```xml
<question text="Select one of the following:" name="Selection">
	<option value="Cats" />
	<option value="Dogs" />
	<option value="Spiders" />
</question>
```
Asks the user to select "Cats", "Dogs" or "Spiders", the answer is saved in the field "Selection".
To answer the user can either enter a number from 1 to 3, or the start of one of the strings, e.g. "Sp" to select "Spiders".

#### Random
```xml
<random [name="name" [conflict="overwrite"]] [type="list"] [min="1"] [max="100"]>
	...
</random>
```
Selects a random value to save in field `"name"`.  Conflicts are resolved as for [constants](#constants).
The exact behaviour depends on the value of `type`:
* `"list"`: Selects on of the options given as subtags. [Option](#options) behave mostly like those of [questions](#questions), but also allow for a `weight` attribute to make the random selection non-uniform. Default behaviour.
* `"range"`: Selects a random integer uniformly from `min` to `max`, with the default values being 1 and 100 respectively. This type ignores [option](#options) tags.

##### Examples
```xml
<random name="Age" type="range" min="14" max="36" />
```
Selects a random integer from 14 to 36 and saves it in the field "Age".
```xml
<random name="Element">
	<option value="Fire" weight="9" />
	<option value="other" weight="1">
		<question text="Enter an element:" type="input" name="Element" />
	</option>
</random>
```
Has a 90% chance to save "Fire" in the field "Element" and a 10% chance to let the user choose on their own instead. Note that the default conflict behaviour is `"overwrite"`, meaning that the value "other" is overwritten by the user selection.

#### Repeats
```xml
<repeat [number="2"]>
	...
</repeat>
```
Evaluates all subtags `number` times, or twice, if `number` is not specified. Currently there is no support for accessing the number of the loop.

##### Example
```xml
<repeat number="3">
	<random name="sum" type="range" max="10" conflict="add" />
</repeat>
Adds up three random numbers from 1 to 10 in the field "sum".
```

#### Comparisons
```xml
<equal>
	<constant value="fieldname" />
	...
	<constant value="fieldname" />
	<field value="fieldname" />
	...
	<field value="fieldname" />
	<do>
		...
	</do>
	<else>
		...
	</else>
</equal>
<greater>
	...
</greater>
```
Compares the first `<constant />` or `<field />` tag to all others given, comparing the content of `value` or the value of the field given in `value` respectively. If the values are all equal/the first value is greater than all others (for `<equal>`/`<greater>`), the subtags of `<do>` are evaluated, otherwise the subtags of `<else>` are evaluated.
Values that cannot be interpreted as integers may cause errors in `<greater></greater>` tags.
All subtags are optional.

##### Examples
```xml
<greater>
	<field value="Character age" />
	<constant value="20" />
	<do>
		<constant name="Trivia" value="May drink in the USA." conflict="stack" />
	</do>
</greater>
```
Checks if the value in the field "Character age" is greater than 20. If it is, the line "May drink in the USA" is appended as a new line to the field "Trivia".

```xml
<equal>
	<field value="Alice´s height" />
	<field value="Bob´s height" />
	<field value="Clemens´ height" />
	<else>
		<question text="Who has a different height?" type="input" name="Different"  />
	</else>
</equal>
```
If the values of the fields "Alice´s height", "Bob´s height" and "Clemens´ height" are not all equal, the user is prompted to answer the question "Who has a different height?", the answer of which is saved in the field "Different".

#### Macros
```xml
<macro [save="save"] [load="load"]>
	...
</macro>
```
If `save` is provided, all subtags are saved to be loaded later. The subtags are not evaluated at this point.
If `load` is provided, all subtags previously saved under this value are evaluated.
A macro may have `save` and `load` attributes at the same time, in which case the saving action is always executed first.

##### Example
```xml
<question text="What do you prefer?">
	<option value="Magic">
		<macro save="Attribute" load="Attribute">
			<constant name="MAG" value="1" conflict="add" />
		</macro>
	</option>
	<option value="Strength">
		<macro save="Attribute" load="Attribute">
			<constant name="STR" value="1" conflict="add" />
		</macro>
	</option>
</question>
...
<macro load="Attribute" />
```
Asks the user if they prefer "Magic" or "Strength". If they choose the first option, a macro containing a +1 increase to the value in the field "MAG" is saved, if they choose the second option, a macro containing a +1 increase to the value in the field "STR" is saved. In both cases the content is instantly evaluated as well, because of `load="Attribute"`.
Later the macro is loaded again, further increasing the chosen field by 1.

### Display Tags
Tags used by cyoa_display.py

#### Display Constants
```xml
<constant value="value" />
```
Prints the value of `value`.

##### Example
```xml
<constant value="Hello" />
<constant value="&#10;&#09;Hello" />
```
Prints:
```Console
Hello

	Hello
```

#### Display Fields
```xml
<field name="name" [name-format="{}: "] [seperator="&#10;&#09;"] />
```
Displays the name and contents of field `name`. The name is hereby formatted as given in `name-format`, replacing `{}` with the name.
If the value of field `name` is a list, the elements are joined with `seperator` as seperator.
The default values of these fields are "{}: " and "&#10;&#09;" respectively, where "&#10;" is a linebreak and "&#09;" is a tab.

##### Examples
Assume field `Fruit` contains "Apple" and field `Numbers` contains the list [1, 2, 3].
```xml
<field name="Fruit" />
```
Prints:
```console
Fruit: Apple
```
```xml
<field name="Numbers" name-format="--{}--&#10;" seperator="&#10;" />
```
Prints:
```console
--Numbers--
1
2
3
```

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
