import os
from dataclasses import dataclass
from typing import Iterable,Callable
from collections import defaultdict,Counter
from functools import reduce
from itertools import groupby
from operator import attrgetter

print(os.getcwd())

# _____ OBIEKTOWO ________
@dataclass(frozen=True)
class Workout:
    day: str #data zawodów
    kind: str #typ zawodów: trail/road/gym
    distance_km: float #długość zawodów w km
    climb_m: int #wysokość wzniosu w m
    duration_min: int #limit czasowy
    
class TrainingLog:
    def __init__(self,workouts:Iterable[Workout]):
        self.workouts=list(workouts)
        
    def total_distance(self) -> float:
        return sum(w.distance_km for w in self.workouts)
    
    def by_kind(self)->dict[str,list[Workout]]:
        buckets:dict[str,list[Workout]]=defaultdict(list)
        for w in self.workouts:
            buckets[w.kind].append(w)
        return buckets
    
    def fastest(self) -> Workout:
        #najszybszy bieg - szukamy minimalnego pace (min/km)
        return min(self.workouts,key=lambda w:w.duration_min/max(w.distance_km,0.01))
    
    def filter(self,predicate:Callable[[Workout],bool]) -> 'TrainingLog':
        return TrainingLog(filter(predicate,self.workouts))
   
# ____DANE____
ws = [
    Workout("2025-02-10","trail",38,1200,270),
    Workout("2025-03-16","road",12,23,64),
    Workout("2025-04-02","gym",0,0,30),
    Workout("2025-04-26","trail",33,2100,265),
    Workout("2025-05-06","road",21,60,112),
    Workout("2025-05-21","trail",15,300,137),
    Workout("2025-06-13","road",10,21,49),
    Workout("2025-06-30","gym",0,0,55),
    Workout("2025-07-26","trail",45,3400,550),
]

log = TrainingLog(ws)

#___ funkcyjnie____
#1->przeliczenie tempa (min/km) dla biegow z dystansem >0
paces = list(map(lambda w:(w.day,round(w.duration_min/w.distance_km,2)),filter(lambda w:w.distance_km>0,log.workouts)))

#2 -> reduce: całkowite przewyższenie trail+szosa
total_climb = reduce(lambda acc,w:acc+(w.climb_m if w.kind in {"trail","road"} else 0),log.workouts,0)

#3 -> groupby -  sumy wg typów
sorted_ws = sorted(log.workouts,key=attrgetter("kind"))
km_by_kind = {k:round(sum(w.distance_km for w in g),2) for k,g in groupby(sorted_ws,key=attrgetter("kind"))}


# ____KOLEKCJE____
kinds_counter = Counter(w.kind for w in log.workouts) #ile sesji z każdego typu biegu
unique_days = {w.day for w in log.workouts} #ile różnych dni
buckets = log.by_kind()

#__program glowny_____

import os
from dataclasses import dataclass
from typing import Iterable,Callable
from collections import defaultdict,Counter
from functools import reduce
from itertools import groupby
from operator import attrgetter

print(os.getcwd())

# _____ OBIEKTOWO ________
@dataclass(frozen=True)
class Workout:
    day: str #data zawodów
    kind: str #typ zawodów: trail/road/gym
    distance_km: float #długość zawodów w km
    climb_m: int #wysokość wzniosu w m
    duration_min: int #limit czasowy
    
class TrainingLog:
    def __init__(self,workouts:Iterable[Workout]):
        self.workouts=list(workouts)
        
    def total_distance(self) -> float:
        return sum(w.distance_km for w in self.workouts)
    
    def by_kind(self)->dict[str,list[Workout]]:
        buckets:dict[str,list[Workout]]=defaultdict(list)
        for w in self.workouts:
            buckets[w.kind].append(w)
        return buckets
    
    def fastest(self) -> Workout:
        #najszybszy bieg - szukamy minimalnego pace (min/km)
        return min(self.workouts,key=lambda w:w.duration_min/max(w.distance_km,0.01))
    
    def filter(self,predicate:Callable[[Workout],bool]) -> 'TrainingLog':
        return TrainingLog(filter(predicate,self.workouts))
   
# ____DANE____
ws = [
    Workout("2025-02-10","trail",38,1200,270),
    Workout("2025-03-16","road",12,23,64),
    Workout("2025-04-02","gym",0,0,30),
    Workout("2025-04-26","trail",33,2100,265),
    Workout("2025-05-06","road",21,60,112),
    Workout("2025-05-21","trail",15,300,137),
    Workout("2025-06-13","road",10,21,49),
    Workout("2025-06-30","gym",0,0,55),
    Workout("2025-07-26","trail",45,3400,550),
]

log = TrainingLog(ws)

#___ funkcyjnie____
#1->przeliczenie tempa (min/km) dla biegow z dystansem >0
paces = list(map(lambda w:(w.day,round(w.duration_min/w.distance_km,2)),filter(lambda w:w.distance_km>0,log.workouts)))

#2 -> reduce: całkowite przewyższenie trail+szosa
total_climb = reduce(lambda acc,w:acc+(w.climb_m if w.kind in {"trail","road"} else 0),log.workouts,0)

#3 -> groupby -  sumy wg typów
sorted_ws = sorted(log.workouts,key=attrgetter("kind"))
km_by_kind = {k:round(sum(w.distance_km for w in g),2) for k,g in groupby(sorted_ws,key=attrgetter("kind"))}


# ____KOLEKCJE____
kinds_counter = Counter(w.kind for w in log.workouts) #ile sesji z każdego typu biegu
unique_days = {w.day for w in log.workouts} #ile różnych dni
buckets = log.by_kind()

#__program glowny_____
print(f"łaczny dystans [km]: {round(log.total_distance(),1)}")
print(f"Przewyższenie razem [m]: {total_climb}")
print(f"Tempo (pace): {paces}")
print(f"suma km wg.typów {km_by_kind}")
print(f"licznik typów: {kinds_counter}")
print(f"najszybszy trening: {log.fastest()}")
print(f"unikalne dni: {unique_days}")
print(f"Tylko trail >15: {[w for w in log.filter(lambda w:w.kind=='trail' and w.distance_km>15).workouts]}")
