from typing import TypeVar, Protocol, runtime_checkable


T = TypeVar("T", contravariant=True)

@runtime_checkable
class Visitor(Protocol[T]):
    def visit(self, visitee: T):
        '''
        Dynamically dispatching according to the subclasses of T
        '''
        pass
