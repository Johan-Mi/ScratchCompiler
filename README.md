# ScratchCompiler

Compiles code into scratch projects.

## Language reference

If you've ever used Pyton, you will probably find the syntax familiar.

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
You can create as many sprites as you want. Sprites can, just like the stage,
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
Declares a variable named `foo`. Variables can either be declared in the global
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
Declares an array named `bar`.

```python
bar[n]
```

Returns the `n`th element of the array `bar`. Array indices start at 1.

```python
bar += foo
```

Appends the value `foo` to the end of the array `bar`.

TODO: Add more array functions.

### Procedures

```python
def my_procedure(a, b, c):
	doSomething()
	doSomethingElse()
```
Creates the procedure `my\_procedure` that takes the arguments `a`, `b`, and
`c`. When called, it will run the code in the braces. Procedures can belong to
sprites or the stage.

```python
warp def render():
	...
```
The `warp` keyword applies "run without screen refresh" to a procedure.

### If statements

```python
if a_condition:
	doSomething()
```
Run `doSomething()` if `a_condition` is true.

```python
if a_condition:
	branch1()
else:
	branch2()
```
Run `branch1()` if `a_condition` is true, otherwise run `branch2()`.

```python
if a_condition:
	branch1()
elif another_condition:
	branch2()
```
Run `branch1()` if `a_condition` is true. If it's not true, continue down and
run `branch2()` if `another_condition` is true. `elif`s can be chained, and the
chain can optionally end with an `else` that will run if all of the conditions
fail.
