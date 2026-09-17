from enum import Enum

class OrderitemStatus(str, Enum)
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"