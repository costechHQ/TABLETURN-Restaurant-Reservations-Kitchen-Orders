import time

from fastapi import Request


async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    print(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} "
        f"({duration:.3f}s)"
    )

    return response