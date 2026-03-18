# async def get_post_or_404(
#     post_id: int,
#     db: Session = Depends(get_db)
# ) -> Post:
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise HTTPException(404, "Post not found")
#     return post

# @app.get("/posts/{post_id}")
# async def get_post(post: Post = Depends(get_post_or_404)):
#     return post  # Already validated!
# @app.put("/posts/{post_id}")
# async def update_post(
#     post: Post = Depends(get_post_or_404),
#     data: PostUpdate = ...
# ):
#     # No need to check if post exists!
# update_post_in_db(post, data)
