# ScratchCompiler

Compiles code into scratch projects.

## Language reference

### The stage

```python
stage:
	...
```
There can only be one stage. It can contain variables, lists, costumes, and
functions.

### Sprites

```python
sprite name_of_sprite:
	...
```
You can create as many sprites as you want to. Sprites can, just like the stage,
contain variables lists, costumes and functions.

### Costumes

```python
costumes {
	"costume1.png", "costume2.svg"
}
```
Sprites and the stage contain a list of costumes. The costumes are referred to
by their file names.

### Variables

```python
var foo
```
Declares a variable named "foo". Variables can either be declared in the global
scope or in a sprite.

```python
foo = 5
```
Assign a value to a variable.

```python
foo += 10
foo -= 10
foo *= 10
foo /= 10
```
These statements are equivalent to the following:
```python
foo = foo + 10
foo = foo - 10
foo = foo * 10
foo = foo / 10
```

### Arrays

```python
arr bar
```
Declares an array named bar;

TODO: Make arrays usable

### Functions

```python
def my_function(a, b, c):
	doSomething()
	doSomethingElse()
```
Creates the function "my\_function" that takes the arguments "a", "b", and "c".
When called, it will run the code in the braces. Functions can belong to sprites
or the stage.

```python
warp def render():
	...
```
The "warp" keyword applies "run without screen refresh" to a function.

### If statements

```python
if a_condition:
	doSomething()
```
Run doSomething() if a\_condition is true.

```python
if a_condition:
	branch1()
else:
	branch2()
```
Run branch1() if a\_condition is true, otherwise run branch2().

```python
if a_condition:
	branch1()
else if another_condition:
	branch2()
```
Run branch1() if a\_condition is true. If it's not true, continue down and run
branch2() if another_condition is true. "else if"s can be chained, and the chain
can optionally end with an "else" that will run if all of the "else if"s fail.
