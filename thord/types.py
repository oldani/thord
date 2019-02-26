from typing import *


Scope = Dict[str, Any]
Message = Dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]

HTMLResponse = TypeVar("HTMLResponse")
