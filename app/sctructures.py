from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Union

if TYPE_CHECKING:
    from pathlib import Path

ImageType = Union[Path, str]
UrlType = str


class LocalPostImage(TypedDict):
    text: str
    image: ImageType


class LocalPostFood(LocalPostImage):
    pass


class LocalPostAnimals(LocalPostImage):
    pass


class LocalPostPersons(LocalPostImage):
    pass


class LocalPostMeme(TypedDict):
    image: ImageType


class LocalPostArt(TypedDict):
    title: str
    artist: str
    year: int
    location: str
    image: ImageType
    description: str


class LocalPostMovie(TypedDict):
    title: str
    image: ImageType
    original_title: str
    director: str
    genre: str
    year: int
    country: str
    language: str
    runtime: str
    budget: str
    box_office: str
    rating_IMDB: str
    kinopoisk_url: UrlType


class LocalPostLocation(TypedDict):
    image: ImageType
    name: str
    location: str
    coordinates: str
    latitude: str
    longitude: str
    description: str


class LocalPostMusic(TypedDict):
    title: str
    band: str
    album: str
    year: int
    genre: str
    description: str
    url: UrlType


class LocalPostPoem(TypedDict):
    автор: str
    название: str
    год: int
    текст: str


LocalPost = Union[
    LocalPostImage,
    LocalPostFood,
    LocalPostAnimals,
    LocalPostPersons,
    LocalPostMeme,
    LocalPostArt,
    LocalPostMovie,
    LocalPostLocation,
    LocalPostMusic,
    LocalPostPoem
]
