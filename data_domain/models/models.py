from typing import Dict, List, Optional

from pydantic import BaseModel


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class Month(str, Enum):
    jan = "jan"
    feb = "feb"
    mar = "mar"
    apr = "apr"
    may = "may"
    jun = "jun"
    jul = "jul"
    aug = "aug"
    sep = "sep"
    oct = "oct"
    nov = "nov"
    dec = "dec"


