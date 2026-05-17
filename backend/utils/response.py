"""
统一 API 响应格式模块
"""
from fastapi.responses import JSONResponse


def success_response(data=None, message: str = "success") -> JSONResponse:
    """
    成功响应

    Args:
        data: 响应数据
        message: 响应消息

    Returns:
        JSONResponse: 统一格式的成功响应
    """
    return JSONResponse(
        content={
            "code": 0,
            "message": message,
            "data": data
        }
    )


def error_response(message: str, code: int = 400) -> JSONResponse:
    """
    错误响应

    Args:
        message: 错误消息
        code: 错误码

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        content={
            "code": code,
            "message": message,
            "data": None
        }
    )


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int
) -> JSONResponse:
    """
    分页响应

    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页条数

    Returns:
        JSONResponse: 统一格式的分页响应
    """
    return JSONResponse(
        content={
            "code": 0,
            "message": "success",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
            }
        }
    )
