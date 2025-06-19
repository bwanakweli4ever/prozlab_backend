# app/modules/tasks/schemas/task.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ServiceRequestCreate(BaseModel):
    """Schema for creating a service request"""
    company_name: str = Field(..., min_length=2, max_length=200)
    client_name: str = Field(..., min_length=2, max_length=100)
    client_email: EmailStr
    client_phone: Optional[str] = None
    service_title: str = Field(..., min_length=5, max_length=200)
    service_description: str = Field(..., min_length=20)
    service_category: str = Field(..., description="Service category/specialty")
    required_skills: Optional[str] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    expected_duration: Optional[str] = None
    deadline: Optional[datetime] = None
    location_preference: Optional[str] = None
    remote_work_allowed: bool = True
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM


class ServiceRequestResponse(BaseModel):
    """Service request response"""
    id: uuid.UUID
    company_name: str
    client_name: str
    client_email: str
    client_phone: Optional[str]
    service_title: str
    service_description: str
    service_category: str
    required_skills: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    expected_duration: Optional[str]
    deadline: Optional[datetime]
    location_preference: Optional[str]
    remote_work_allowed: bool
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    assignments_count: int = 0
    
    class Config:
        from_attributes = True


class TaskAssignmentCreate(BaseModel):
    """Schema for assigning a task to a professional"""
    service_request_id: uuid.UUID
    proz_id: uuid.UUID
    assignment_notes: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    proposed_rate: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None


class TaskAssignmentResponse(BaseModel):
    """Task assignment response"""
    id: uuid.UUID
    service_request_id: uuid.UUID
    proz_id: uuid.UUID
    assigned_by_user_id: Optional[uuid.UUID]
    assignment_notes: Optional[str]
    estimated_hours: Optional[float]
    proposed_rate: Optional[float]
    status: TaskStatusEnum
    proz_response: Optional[str]
    proz_response_at: Optional[datetime]
    assigned_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Nested objects
    service_request: ServiceRequestResponse
    professional_name: str
    professional_email: str
    
    class Config:
        from_attributes = True


class ProfessionalTaskResponse(BaseModel):
    """Task response for professional dashboard"""
    assignment_id: uuid.UUID
    service_title: str
    company_name: str
    client_name: str
    service_description: str
    service_category: str
    budget_range: Optional[str]
    estimated_hours: Optional[float]
    proposed_rate: Optional[float]
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    assignment_notes: Optional[str]
    assigned_at: datetime
    due_date: Optional[datetime]
    deadline: Optional[datetime]
    is_remote: bool


class TaskResponseUpdate(BaseModel):
    """Professional's response to task assignment"""
    response_action: str = Field(..., description="accept, reject, request_info")
    response_message: Optional[str] = None
    proposed_changes: Optional[dict] = None


class NotificationResponse(BaseModel):
    """Notification response"""
    id: uuid.UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
    task_assignment_id: Optional[uuid.UUID]
    
    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    """Professional dashboard statistics"""
    total_assignments: int
    pending_assignments: int
    active_assignments: int
    completed_assignments: int
    unread_notifications: int
    this_week_earnings: float
    this_month_earnings: float
    average_rating: float


class AdminTaskStatsResponse(BaseModel):
    """Admin task management statistics"""
    total_requests: int
    pending_requests: int
    assigned_requests: int
    completed_requests: int
    urgent_requests: int
    unassigned_requests: int
    active_professionals: int
    requests_this_week: int


class BulkAssignmentRequest(BaseModel):
    """Bulk task assignment"""
    service_request_ids: List[uuid.UUID]
    assignment_criteria: dict = Field(..., description="Criteria for auto-assignment")
    notify_professionals: bool = True


class TaskSearchFilters(BaseModel):
    """Search filters for tasks"""
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    service_category: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    location: Optional[str] = None
    remote_only: Optional[bool] = None