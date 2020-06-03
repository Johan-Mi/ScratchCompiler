# ScratchCompiler

Compiles code into scratch projects.

## Language reference

### The stage

```go
stage {
	...
}
```
There can only be one stage. It can contain variables, lists, costumes, and
functions.

### Sprites

```go
sprite name_of_sprite {
	...
}
```
You can create as many sprites as you want to. Sprites can, just like the stage,
contain variables lists, costumes and functions.

### Costumes

```go
costumes {
	"costume1.png", "costume2.svg"
}
```
Sprites and the stage contain a list of costumes. The costumes are referred to
by their file names.

### Variables

```go
var foo;
```
Declares a variable named "foo". Variables can either be declared in the global
scope or in a sprite.

```go
foo = 5;
```
Assign a value to a variable.

```go
foo += 10;
foo -= 10;
foo *= 10;
foo /= 10;
```
These statements are equivalent to the following:
```go
foo = foo + 10;
foo = foo - 10;
foo = foo * 10;
foo = foo / 10;
```

### Arrays

```go
arr bar;
```
Declares an array named bar;

TODO: Make arrays usable

### Functions

```go
func my_function(a, b, c) {
	doSomething();
	doSomethingElse();
}
```
Creates the function "my\_function" that takes the arguments "a", "b", and "c".
When called, it will run the code in the braces. Functions can belong to sprites
or the stage.

```go
warp func render() {

}
```
The "warp" keyword applies "run without screen refresh" to a function.

### If statements

```go
if a_condition {
	doSomething();
}
```
Run doSomething() if a\_condition is true.

```go
if a_condition {
	branch1();
} else {
	branch2();
}
```
Run branch1() if a\_condition is true, otherwise run branch2().

```go
if a_condition {
	branch1();
} else if another_condition {
	branch2();
}
```
Run branch1() if a\_condition is true. If it's not true, continue down and run
branch2() if another_condition is true. "else if"s can be chained, and the chain
can optionally end with an "else" that will run if all of the "else if"s fail.
