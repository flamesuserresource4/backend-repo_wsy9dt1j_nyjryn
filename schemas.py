"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# District 2nd Cafe specific schemas

class MenuItem(BaseModel):
    """
    Menu items for the cafe
    Collection name: "menuitem"
    """
    name: str = Field(..., description="Menu item name")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in local currency")
    category: str = Field(..., description="Category, e.g., Coffee, Tea, Pastry")
    image_url: HttpUrl = Field(..., description="Accessible image URL for the item")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")

class ChatMessage(BaseModel):
    """
    Stores chat messages for the AI assistant
    Collection name: "chatmessage"
    """
    session_id: str = Field(..., description="Session identifier for the chat")
    role: str = Field(..., description="user or assistant")
    text: str = Field(..., description="Message content")
    language: Optional[str] = Field(None, description="IETF language tag, e.g., en, vi, ja")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
