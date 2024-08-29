class A:
	def foo(self) -> None: ...

class B:
	def bar(self) -> None: ...

def identity[T](a: T) -> T:
	return a

def main() -> int:
	a = identity(A())
	b = identity(B())

	a.foo()
	b.bar()

	return 0

