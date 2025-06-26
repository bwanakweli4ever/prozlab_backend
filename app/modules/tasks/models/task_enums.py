
# app/modules/tasks/models/task_enums.py
from enum import Enum
from pydantic import field_validator



class TaskStatusEnum(str, Enum):
    """Task status enum - values must match database enum exactly"""
    PENDING = "pending"        # lowercase to match DB
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TaskPriorityEnum(str, Enum):
    """Task priority enum - values must match database enum exactly"""
    LOW = "low"               # lowercase to match DB
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
class ServiceRequestCreate(ServiceRequestBase):
    # Add these validators to force lowercase conversion
    
    @field_validator('status', mode='before')
    @classmethod
    def convert_status_to_lowercase(cls, v):
        if v is None:
            return 'pending'  # Default value
        if isinstance(v, str):
            return v.lower()  # Convert any string to lowercase
        if hasattr(v, 'value'):
            return v.value.lower()  # Handle enum objects
        return str(v).lower()  # Fallback
    
    @field_validator('priority', mode='before')
    @classmethod
    def convert_priority_to_lowercase(cls, v):
        if v is None:
            return 'medium'  # Default value
        if isinstance(v, str):
            return v.lower()  # Convert any string to lowercase
        if hasattr(v, 'value'):
            return v.value.lower()  # Handle enum objects
        return str(v).lower()  # Fallback