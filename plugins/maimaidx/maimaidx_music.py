import json
import os
import random
from typing import Dict, List, Literal, Optional, Union, Tuple, Any
from copy import deepcopy

from configs.path import TXT_PATH


def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    if type(checker[0]) != type(checker[-1]):
        print('Detected different data types')
        checker = [x for x in checker if not isinstance(x, str)]
    # print(checker, elem, diff)
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        # print(elem)
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self['notes'][0]
        elif item == 'hold':
            return self['notes'][1]
        elif item == 'slide':
            return self['notes'][2]
        elif item == 'touch':
            return self['notes'][3] if len(self['notes']) == 5 else 0
        elif item == 'brk':
            return self['notes'][-1]
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)


class Stats(Dict):
    count: Optional[int] = None
    avg: Optional[float] = None
    sss_count: Optional[int] = None
    difficulty: Optional[str] = None
    rank: Optional[int] = None
    total: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'sss_count':
            return self['sssp_count']
        elif item == 'rank':
            return self['v'] + 1
        elif item == 'total':
            return self['t']
        elif item == 'difficulty':
            return self['tag']
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class MaiMusic(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Literal["SD", "DX"] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    charts: Optional[Chart] = None
    stats: Optional[List[Stats]] = None

    release_date: Optional[str] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version'}:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class MaiMusicList(List[MaiMusic]):
    def by_id(self, music_id: str) -> Optional[MaiMusic]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[MaiMusic]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, seed: Optional[str] = None) -> Optional[MaiMusic]:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(
        self,
        *,
        level: Optional[Union[str, List[str]]] = ...,
        ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
        title_search: Optional[str] = ...,
        genre: Optional[Union[str, List[str]]] = ...,
        bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
        type: Optional[Union[str, List[str]]] = ...,
        diff: List[int] = ...,
        version: Optional[Union[str, List[str]]] = ...,
    ) -> Optional["MaiMusicList"]:
        new_list = MaiMusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue

            # print(f'music.ds:{music.ds}, ds:{ds}, diff2:{diff2}')
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if not in_or_equal(music.version, version):
                continue
            if title_search is not Ellipsis and title_search.lower(
            ) not in music.title.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list


# ??????DX2021
stats = json.load(
    open(TXT_PATH / 'maimai' / 'maimaimusic_stats.json', 'r',
         encoding="utf8")) if os.path.exists(TXT_PATH / 'maimai' /
                                             'maimaimusic_stats.json') else {}
total_list: MaiMusicList = MaiMusicList(
    json.load(
        open(TXT_PATH / 'maimai' / 'maimaimusic.json', 'r', encoding="utf8")))
for __i in range(len(total_list)):
    total_list[__i] = MaiMusic(total_list[__i])
    if stats != {}:
        total_list[__i]['stats'] = stats[total_list[__i].id]
    for __j in range(len(total_list[__i].charts)):
        total_list[__i].charts[__j] = Chart(total_list[__i].charts[__j])
        if stats != {}:
            total_list[__i].stats[__j] = Stats(total_list[__i].stats[__j])

# maimai DX UNiVERSE                                                                                  'maimaimusic_stats.json') else {}
total_list_jp: MaiMusicList = MaiMusicList(
    json.load(
        open(TXT_PATH / 'maimai' / 'maimusic_universe.json',
             'r',
             encoding="utf8")))
for __i in range(len(total_list_jp)):
    total_list_jp[__i] = MaiMusic(total_list_jp[__i])
    for __j in range(len(total_list_jp[__i].charts)):
        total_list_jp[__i].charts[__j] = Chart(total_list_jp[__i].charts[__j])

all_plate_id = {
    "??????": 6101,
    "?????????": 6103,
    "??????": 6102,
    "??????": 6104,
    "??????": 6105,
    "?????????": 6107,
    "??????": 6106,
    "??????": 6108,
    "??????": 6109,
    "?????????": 6111,
    "??????": 6110,
    "??????": 6112,
    "??????": 6113,
    "?????????": 6115,
    "??????": 6114,
    "??????": 6116,
    "??????": 6117,
    "?????????": 6119,
    "??????": 6118,
    "??????": 6120,
    "??????": 6121,
    "?????????": 6123,
    "??????": 6122,
    "??????": 6124,
    "??????": 6125,
    "?????????": 6127,
    "??????": 6126,
    "??????": 6128,
    "??????": 6129,
    "?????????": 6131,
    "??????": 6130,
    "??????": 6132,
    "??????": 6133,
    "?????????": 6135,
    "??????": 6134,
    "??????": 6136,
    "??????": 6137,
    "?????????": 6139,
    "??????": 6138,
    "??????": 6140,
    "??????": 6141,
    "?????????": 6143,
    "??????": 6142,
    "??????": 6144,
    "??????": 6145,
    "?????????": 6147,
    "??????": 6146,
    "??????": 6148,
    "??????": 55101,
    "??????": 55102,
    "?????????": 55104,
    "??????": 55103,
    "??????": 109101,
    "??????": 109102,
    "?????????": 109104,
    "??????": 109103,
    "??????": 159101,
    "??????": 159102,
    "?????????": 159104,
    "??????": 159103,
    "??????": 6149,
    "??????": 6150,
    "?????????": 6152,
    "??????": 6151,
    "kop19FL": 50002,
    "kop19T1": 50001,
    "kop20FL": 100003,
    "kop20T1": 100001,
    "kop20SC": 100004,
}

maimai_versions = {
    "maimai": '100',
    "maimai PLUS": '110',
    "maimai GreeN": '120',
    "maimai GreeN PLUS": '130',
    "maimai ORANGE": '140',
    "maimai ORANGE PLUS": '150',
    "maimai PiNK": '160',
    "maimai PiNK PLUS": '170',
    "maimai MURASAKi": '180',
    "maimai MURASAKi PLUS": '185',
    "maimai MiLK": '190',
    "maimai MiLK PLUS": '195',
    "MiLK PLUS": '195',
    "maimai FiNALE": '199',
    "maimai DX": '200',
    "maimai DX PLUS": '210',
    "maimai DX Splash": '214',
    "maimai DX Splash PLUS": '215',
    "maimai DX UNiVERSE": '220',
    "maimai DX UNiVERSE PLUS": '225',
    "maimai \u3067\u3089\u3063\u304f\u3059": 'CN200',
    "maimai \u3067\u3089\u3063\u304f\u3059 Splash": 'CN210',
    "maimai \u3067\u3089\u3063\u304f\u3059 Splash PLUS": 'CN220',
}

maiversion = {
    '0': 'maimai',
    '1': 'maimai PLUS',
    '2': 'maimai GreeN',
    '3': 'maimai GreeN PLUS',
    '4': 'maimai ORANGE',
    '5': 'maimai ORANGE PLUS',
    '6': 'maimai PiNK',
    '7': 'maimai PiNK PLUS',
    '8': 'maimai MURASAKi',
    '9': 'maimai MURASAKi PLUS',
    '10': 'maimai MiLK',
    '11': 'maimai MiLK PLUS',
    '12': 'maimai FiNALE',
    '13': 'maimai DX',
    '14': 'maimai DX PLUS',
    '15': 'maimai DX Splash',
    '16': 'maimai DX Splash PLUS',
    '17': 'maimai DX UNiVERSE',
    '18': 'maimai DX UNiVERSE PLUS',
}

mai_region = {'SDEZ': 'DX', 'SDGA': 'EX', 'SDGB': 'CH'}
