#! /usr/bin/env python3

import datetime
from dataclasses import dataclass


@dataclass
class Message:
    text: str
    sender: str = ""
    msg_type: str = "info"
    timestamp: datetime.datetime = datetime.datetime.now()
