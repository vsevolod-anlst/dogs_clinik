from enum import Enum
from pydantic import BaseModel
from typing import List

from fastapi import FastAPI, Path, HTTPException

import time

class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"

class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType

class Timestamp(BaseModel):
    id: int
    timestamp: int

dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]

description = """
Через него можно:

1) получить приветсвие сервиса
2) отправить пустой запрос, инфа о времени получения которого запишется в БД
3) получить всех собак или всех собак одной породы
4) создать новую собаку
5) получить одну собаку по ее pk
6) обновить инфу по собаке, или заменить ее на другую
"""
tags_metadata = [
    {
        "name": "not_Dogs",
        "description": "Иные операции (не с собаками)"
    },
    {
        "name": "Dogs",
        "description": "Операции с собаками",

    }
]

app = FastAPI(
    title="Клиника собак",
    description=description,
    summary="Данный АПИ позволяет работать с собаками в БД клиники",
    version="0.0.1",
    openapi_tags=tags_metadata
)


def check_kind_dog(kind: str) -> bool:
    """
    # Функция для проверки породы собаки
    Функция проверит переданную породу, и если этой породы нет среди допустимых - то вренет Фолс
    """

    if kind in DogType.__members__:
        return True
    else:
        return False


def is_pk_in_bd(pk: int) -> bool:
    """
    # Функция для проверки наличия pk в БД
    Функция проверит переданный первичный ключ, и если этот ключ УЖЕ есть в БД - вернет тру
    """

    cnt_elememt_db = len(dogs_db)

    for strok in range(cnt_elememt_db):
        pk_this_dog = dogs_db[strok].pk

        if pk == pk_this_dog:
            return True

    else:
        return False

def find_str_dog_for_pk(pk: int) -> int:
    """
    # Функция для нахождения номера строки, в которой соджится собака с переданным первичным ключом
    Функция найдет строку, в которой содержится собака с pk, переданным на вход и вернет номер этой строки
    """

    cnt_elememt_db = len(dogs_db)

    for strok in range(cnt_elememt_db):
        pk_this_dog = dogs_db[strok].pk

        if pk == pk_this_dog:
            return strok


@app.get("/", tags=["not_Dogs"], summary="Root")
def root():
    """
    # Метод вернет приветствие
    Скажет Ку
    """

    return {"message": "Привет, собаковед!"}

@app.post("/post", tags=["not_Dogs"], summary="Get Post")
def post() -> Timestamp:

    """
    # Метод запишет в бд строку о совершенном запросе
    Запишет новую строку с id запроса и UNIX временем создания и вернет записанные значения
    """

    cnt_str_post_db = len(post_db)
    post_db.append(Timestamp(id=cnt_str_post_db, timestamp=int(time.time()+946684800)))

    return post_db[cnt_str_post_db]

@app.get("/dogs", tags=["Dogs"], summary="Get Dogs")
def get_many_dogs(kind='all') -> List[Dog]:
    """
    # Метод вернет массив собак
    Метод проверяет переданную породу, и возвращает всех собак этой породы, или же возвращает всех собак, если порода не была передана. Если такая порода не поддерживается в БД, то метод вернет ошибку
    """

    rez_list = list()

    if kind != 'all':
        if check_kind_dog(kind) == False:
            raise HTTPException(status_code=422, detail='Такая порода не поддерживается БД')
            #return
        else:
            for strok in range(len(dogs_db)):
                if dogs_db[strok].kind.value == kind:
                    rez_list.append(dogs_db[strok])

    else:
        for strok in range(len(dogs_db)):
            rez_list.append(dogs_db[strok])

    return rez_list


@app.post("/dog", tags=["Dogs"],
          summary="Create Dog")
def create_dog(dog_object: Dog) -> Dog:
    """
    # Метод создаст новую запись о собаке в БД
    Метод проверяет переданную породу, и если порода не поддерживается в БД - то вернет ошибку, потом функция проверит переданный pk, и если он уникален для БД - то создаст новую собаку, иначе - вернет ошибку.
    """

    kind = dog_object.kind.value
    name = dog_object.name
    pk = dog_object.pk

    if check_kind_dog(kind) == False:
        raise HTTPException(status_code=422, detail='Такая порода не поддерживается БД')
        #return
    else:
        if is_pk_in_bd(pk) == True:
            raise HTTPException(status_code=422, detail=f'Данный pk ={pk}, уже используется в БД')
            #return
        else:
            new_stroka_for_dog = len(dogs_db)
            dogs_db[new_stroka_for_dog] = Dog(name=name, pk=pk, kind=kind)
            return dogs_db[new_stroka_for_dog]

@app.get("/dog/{pk}", tags=["Dogs"], summary="Get Dog By Pk")
def get_one_dog(pk: int) -> Dog:

    """
    # Метод находит собаку по pk и возвращает ее
    Метод получает pk собаки, проверяет есть ли собака с таким pk в БД, и если есть возвращает ее
    """

    if is_pk_in_bd(pk) == False:
        raise HTTPException(status_code=404, detail=f'Собаки с таким pk = {pk} не найдено')
        #return
    else:
        find_dog_srtoka = find_str_dog_for_pk(pk)

        return dogs_db[find_dog_srtoka]


@app.patch("/dog/{pk}", tags=["Dogs"], summary="Update Dog")
def change_dog(pk: int, dog_object: Dog) -> Dog:
    """
    # Метод находит в БД собаку с переданным pk, и заменяет данную строку на новую.
    Метод проверит переданную породу, и если она ок - то проверит есть ли собака с переданным pk в БД, потом проверит не используется ли уже - новый переданный pk, на который надо заменить текущий pk и если все ок - то обновит ее имя и породу
    """

    pk_dog_to_change = pk
    kind_new = dog_object.kind.value
    name_new = dog_object.name
    pk_new = dog_object.pk

    if is_pk_in_bd(pk_dog_to_change) == False:
        raise HTTPException(status_code=404, detail=f'Собаки для обновления с таким pk ={pk_dog_to_change} не найдено')
        #return

    if check_kind_dog(kind_new) == False:
        raise HTTPException(status_code=422, detail='Такая порода не поддерживается БД')
        #return

    if is_pk_in_bd(pk_new) != False:
        raise HTTPException(status_code=422, detail=f'pk = {pk_new}, который вы хотите дать собаке после изменения, уже используется в БД')
        #return

    find_dog_srtoka = find_str_dog_for_pk(pk_dog_to_change)

    dogs_db[find_dog_srtoka] = Dog(name=name_new, pk=pk_new, kind=kind_new)
    return dogs_db[find_dog_srtoka]

