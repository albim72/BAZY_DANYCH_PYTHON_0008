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
   

