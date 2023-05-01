from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2

router = APIRouter(
    prefix="/likes",
    tags=['Likes']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def likes(likes: schemas.Likes, db: Session = Depends(database.get_db), 
          current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.post_id == likes.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"🚫🚫🚫Post with id: {likes.post_id} does not exist🚫🚫🚫")
    
    likes_query = db.query(models.Like).filter(models.Like.post_id == likes.post_id, models.Like.user_id == current_user.user_id)
    found_like = likes_query.first()
    
    if (likes.dir == 1):
        if found_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.user_id} already liked the post {likes.post_id}🤙🤙🤙")
        
        new_vote = models.Like(post_id = likes.post_id, user_id= current_user.user_id)
        db.add(new_vote)
        db.commit()
        return {"message": "👍"}

    else:
        if not found_like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌❌❌")
        
        likes_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "👎"}
