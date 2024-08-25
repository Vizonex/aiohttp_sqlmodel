# Aiohttp_Sqlmodel

A Build-off from [aiohttp_sqlalchemy](https://github.com/ri-gilfanov/aiohttp-sqlalchemy) for sqlmodel/sqlalchemy things. 
This library attempts to make Sqlachemy's Mapping typehints to be regained making it 
easier for users using aiohttp_sqlalchemy to migrate to sqlmodel or vice-versa if 
and when required.



# Pros/Cons of SQLModel

## Pros
- Easiest Static Typechecking and easiest management of dataclass fields.
- Compatable with sqlalchemy since it's built on top of it as is mine with [aiohttp_sqlalchemy](https://github.com/ri-gilfanov/aiohttp-sqlalchemy) to aiohttp_sqlmodel
- aiohttp is a lot less heavy than fastapi when it comes to quite a few things hence my willingness to write this 
library.



## Cons
- Pydantic can be a very bulky choice to compile with pyinstaller leading to alot of unwanted sizes and bulk 
during the production of any application that requires the creation of a server.


## TODOS
- Fix View Types and implement my own web.View Types for fixing these problems and thier short-comings.
- Provide examples on how to use (You will find it is very simillar to aiohttp_sqlalchemy)
