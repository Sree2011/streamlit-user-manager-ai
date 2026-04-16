from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Data model
class Book(BaseModel):
    title: str
    author: str
    year: int

# In-memory "database"
books = []

@app.get("/books")
def get_books():
    return books

@app.post("/books")
def add_book(book: Book):
    books.append(book)
    return {"message": "Book added successfully!"}

@app.put("/books/{index}")
def update_book(index: int, book: Book):
    if index < len(books):
        books[index] = book
        return {"message": "Book updated successfully!"}
    return {"error": "Book not found"}

@app.delete("/books/{index}")
def delete_book(index: int):
    if index < len(books):
        books.pop(index)
        return {"message": "Book deleted successfully!"}
    return {"error": "Book not found"}
