from abc import ABCMeta
from typing import Any, List, Optional, Type, TypeVar, cast

import aiohttp_things as ahth
from aiohttp.web import View
from aiohttp.web_urldispatcher import AbstractRoute

from sqlmodel import SQLModel
from sqlmodel.main import _TSQLModel
from sqlmodel import delete, select, update
from sqlmodel.sql.expression import SelectOfScalar

from sqlmodel.ext.asyncio.session import AsyncSession



from sqlalchemy.orm import Mapped
from sqlalchemy.sql import Delete, Select, Update
from sqlalchemy_things.pagination import OffsetPage, OffsetPaginator


from aiohttp_sqlmodel.constants import SM_DEFAULT_KEY
from aiohttp_sqlmodel.utils import get_session


T = TypeVar("T")

class SMMixin(ahth.ContextMixin, metaclass=ABCMeta):
    sm_session_key: str = SM_DEFAULT_KEY

    def get_sm_session(self, key: Optional[str] = None) -> AsyncSession:
        return get_session(self.request, key or self.sm_session_key)



class SMModelMixin(SMMixin, metaclass=ABCMeta):
    sa_model: Optional[_TSQLModel] = None  # Not all developers use declarative mapping
    
    # My addition, Allows you to write custom subclass init styled code which is cleaner when it's inlined...
    def __init_subclass__(cls, sqlmodel:Optional[Type[_TSQLModel]] = None) -> None:
        cls.sa_model = sqlmodel
        return super().__init_subclass__()


    # TODO: Maybe move like() and ilike() documentation over here?
    
    
    # Since Sqlmodel lacks typehinting over it's own mapped varaibles 
    # this was the best solution in regards to regaining this typehinting 
    # over Sqlmodel attributes
    
    def like(self, attr:T, other: Any, escape: Optional[str] = None):
        """Used to safely map attributes off another Model for using the .like() function
        See: sqlalchemy.sql.elements.SQLCoreOperations.like()"""
        return cast(Mapped, attr).like(other=other, escape=escape)
    
    def ilike(self, attr:T, other: Any, escape: Optional[str] = None):
        """Used to safely map attributes off another Model for using the .like() function
        See: sqlalchemy.sql.elements.SQLCoreOperations.like()"""
        return cast(Mapped, attr).ilike(other=other, escape=escape)

    def mp(self, attr:T) -> Mapped[T]:
        """typecasts SQLModel Fields into a Mapped Attribute, Good for Static Typehinting/TypeChecking"""
        return cast(Mapped, attr)
    
    def asc(self, attr:T):
        """Order attribute given by ascending value"""
        return cast(Mapped, attr).asc()
    
    def desc(self, attr:T):
        """Order attribute given by descending value"""
        return cast(Mapped, attr).desc()



class DeleteStatementMixin(SMModelMixin):
    def get_delete_stmt(self, model: Optional[Type[_TSQLModel]] = None) -> Delete:
        return delete(model or self.sa_model)


class UpdateStatementMixin(SMModelMixin):
    def get_update_stmt(self, model: Optional[Type[_TSQLModel]] = None) -> Update:
        return update(model or self.sa_model)


class SelectStatementMixin(SMModelMixin):
    def get_select_stmt(self, model: Optional[Type[_TSQLModel]] = None) -> SelectOfScalar[_TSQLModel]:
        return select(model or self.sa_model)


class OffsetPaginationMixin(ahth.PaginationMixin, SelectStatementMixin):
    page_key: int = 1
    page_key_adapter = int
    paginator: OffsetPaginator = OffsetPaginator()

    async def execute_select_stmt(
        self,
        model: Optional[Type[_TSQLModel]] = None,
        key: Optional[str] = None,
    ) -> Optional[OffsetPage]:
        async with self.get_sm_session().begin():
            page = await self.paginator.get_page_async(
                self.get_sm_session(key or self.sa_session_key),
                self.get_select_stmt(model or self.sa_model),
                self.page_key,
            )
        return page

    # TODO: maybe exec_select_stmt only? I'll do this for now and let it be optional (Vizonex)
    exec_select_stmt = execute_select_stmt

    async def prepare_context(self) -> None:
        page: Optional[OffsetPage] = await self.execute_select_stmt()

        if page:
            route: AbstractRoute = self.request.match_info.route

            self.context['items'] = page.items

            if page.next:
                kw = {'page_key': page.next}
                self.context['next_url'] = route.url_for().with_query(kw)
            else:
                self.context['next_url'] = page.next

            if page.previous:
                kw = {'page_key': page.previous}
                self.context['previous_url'] = route.url_for().with_query(kw)
            else:
                self.context['previous_url'] = page.previous


class PrimaryKeyMixin(ahth.PrimaryKeyMixin, SMModelMixin, metaclass=ABCMeta):
    sm_pk_attr: Any = getattr(SMModelMixin.sa_model, 'pk', None)


class UnitAddMixin(SMModelMixin, ahth.ItemMixin, metaclass=ABCMeta):
    def sa_add(self, *, key: Optional[str] = None) -> None:
        self.get_sm_session(key).add(self.item)


class UnitDeleteMixin(
    DeleteStatementMixin,
    PrimaryKeyMixin,
    metaclass=ABCMeta,
):
    def get_delete_stmt(self, model: Optional[Type[_TSQLModel]] = None) -> Delete:
        return super(). \
            get_delete_stmt(model). \
            where(self.sm_pk_attr == self.pk)


class UnitEditMixin(
    ahth.ItemMixin,
    UpdateStatementMixin,
    PrimaryKeyMixin,
    metaclass=ABCMeta,
):
    def get_update_stmt(self, model: Optional[Type[_TSQLModel]] = None) -> Update:
        return super(). \
            get_update_stmt(model). \
            where(self.sm_pk_attr == self.pk)


class UnitViewMixin(
    ahth.ItemMixin,
    SelectStatementMixin,
    PrimaryKeyMixin,
    metaclass=ABCMeta,
):
    def get_select_stmt(self, model: Optional[Type[_TSQLModel]] = None) -> Select:
        return super(). \
            get_select_stmt(model). \
            where(self.sm_pk_attr == self.pk)


class ListAddMixin(ahth.ListMixin, SMModelMixin, metaclass=ABCMeta):
    items: List[Any]

    def sm_add_all(self, *, key: Optional[str] = None) -> None:
        self.get_sm_session(key).add_all(self.items)


class ListDeleteMixin(ahth.ListMixin, DeleteStatementMixin, metaclass=ABCMeta):
    pass


class ListEditMixin(ahth.ListMixin, UpdateStatementMixin, metaclass=ABCMeta):
    pass


class ListViewMixin(
    ahth.ListMixin,
    SelectStatementMixin,
    metaclass=ABCMeta,
):
    pass


class SMBaseView(View, SMMixin):
    pass


class SMModelView(View, SMModelMixin):
    pass
