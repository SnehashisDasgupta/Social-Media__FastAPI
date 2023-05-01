from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts'] 
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    '''
    fetch all posts from database. 
    If you give limit in url then it will return 'limit' no. of posts [default limit = 10]
    skip is used to skip no. of posts and return next no. of posts
    'search' keyword fetch post on basis of title of post 
    '''
    #! posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()


    '''
    ----{joins posts and users TABLE using owner_id & user_id and gives total no. of likes of each post [sqlalchemy-> LEFT JOIN(by default)]}---
    The mySQL command :
    SELECT posts.post_id AS posts_post_id, posts.title AS posts_title, posts.content AS posts_content, posts.date AS posts_date, posts.owner_id AS posts_owner_id, count(likes.post_id) AS likes 
    FROM posts LEFT OUTER JOIN likes ON likes.post_id = posts.post_id GROUP BY posts.post_id
    '''
    posts = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.post_id, isouter=True).group_by(models.Post.post_id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user)):

    #create new post with given details
    new_post = models.Post(owner_id=current_user.user_id, **post.dict())
    db.add(new_post) #add in the database
    db.commit() # commit the changes
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post_by_id(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # find the post with the given id
    #! post = db.query(models.Post).filter(models.Post.post_id == id).first()

    post = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.post_id, isouter=True).group_by(models.Post.post_id).filter(models.Post.post_id == id).first()

    #find the post with given id present or not
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):

    # find the post with the given id
    deleted_post = db.query(models.Post).filter(models.Post.post_id == id)

    #finds whether the post with given id present or not
    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    #checks whether the user deleting the post belong to that user only or not 
    if deleted_post.first().owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # find the post with the given id
    post_query = db.query(models.Post).filter(models.Post.post_id == id)

    #finds whether the post with given id present or not
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    #checks whether the user updating the post belong to that user only or not
    if post_query.first().owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
     
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

