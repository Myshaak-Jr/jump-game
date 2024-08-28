class A:
	def foo():
		pass

class B:
	def bar():
		pass

def identity[T](a: T) -> T:
	return a

def main() -> int:
	a = identity(A())
	b = identity(B())

	a.foo()
	b.bar()

	return 0

