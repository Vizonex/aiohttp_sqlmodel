"""
Inspired by aiohttp_sqlalchemy but for better help with handling Sqlmodel classes...
"""

# type hinting
from typing import Type, TypeVar, Union

# aiohttp
from aiohttp.web import Application
from aiohttp_things import web_handlers


# Sqlalchemy (Sqlmodel's backbone)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker


# sqlmodel
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from aiohttp_sqlmodel.utils import init_db

# aiohttp_sqlmodel modules
from aiohttp_sqlmodel.constants import DEFAULT_KEY, SM_DEFAULT_KEY
# Currently doesn't work right, TODO: Fix?
# from aiohttp_sqlmodel.web_handlers import (
#     ListAddMixin,
#     ListDeleteMixin,
#     ListEditMixin,
#     ListViewMixin,
#     OffsetPaginationMixin,
#     PrimaryKeyMixin,
#     SMBaseView,
#     SMMixin,
#     SMModelMixin,
#     SMModelView,
#     UnitAddMixin,
#     UnitDeleteMixin,
#     UnitEditMixin,
#     UnitViewMixin,
# )


# aiohttp_sqlalchemy for type definitions
from aiohttp_sqlalchemy.typedefs import TBind, TTarget, TBinds
from aiohttp_sqlalchemy.exceptions import *


# TODO: (Vizonex)  write our own sa_middleware so that our default key is used in it...
from aiohttp_sqlmodel.middlewares import sm_middleware


# Mirror of aiohttp_sqlalchemy but using sqlmodel's AsyncEngine Class
def bind(target: TTarget, key: str = SM_DEFAULT_KEY, *, middleware: bool = True):
    """
    From aiohttp_sqlalcemy's docs: Function wrapper for binding.

    :param target: argument can be database connection url, asynchronous engine
                   or asynchronous session factory.
    :param key: key of SQLAlchemy binding.
    :param middleware: `bool` for enable middleware. True by default.

    This is the Same as aiohttp_sqlalcemy's function, The only difference is that we're using
    Sqlmodel's `AsyncSession` Object to override the original one.
    """

    if isinstance(target, str):
        target = create_async_engine(target)

    if isinstance(target, AsyncEngine):
        # Seems Setting expire_on_commit to False fixes object loading.
        target = sessionmaker(bind=target, class_=AsyncSession, expire_on_commit=False)

    if isinstance(target, (AsyncSession, Engine, Session)):
        msg = f"{type(target)} is unsupported type of argument `target`."
        raise TypeError(msg)

    if not callable(target):
        msg = f"{target} is unsupported type of argument `target`."
        raise TypeError(msg)

    return target, key, middleware


def setup(app: Application, binds: TBinds) -> None:
    """Same Setup function as aiohttp_sqlalchemy for SQLAlchemy/SQLModel binding to AIOHTTP application.

    :param app: your AIOHTTP application.
    :param binds: iterable of `aiohttp_sqlmodel.bind()` calls.
    """
    for factory, key, middleware in binds:
        if key in app:
            raise DuplicateAppKeyError(key)

        app[key] = factory

        if middleware:
            app.middlewares.append(sm_middleware(key))


# Synonyms
sm_bind = bind


__author__ = "Vizonex"
__version__ = "0.1.0"

