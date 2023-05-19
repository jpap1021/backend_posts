# backend_posts

This is a Flask project.
This project has a local database running, at the moment this database has information about posts and comments abput a specific post.


#Steps to run this project. Run the following commenads in your terminal 

1. git clone -b master https://github.com/jpap1021/backend_posts.git
2. cd backend_posts
3. python3 -m venv venv
4. source venv/bin/activate
5. pip install -r requirements.txt
6. flask run
7. If you have problems with the library jwt.exceptions and his version: run the following command
7.1. pip uninstall jwt
7.2. pip install jwt
8 flask run
9. If you want to run the tes run the follogin command: pytest --cov

#How works this application: 
Note: you can use postman to test the endpoins.
the application has several enpoints:
1. /login (Post) in this endpoint you can create a token that you will need in other endpoints with the header Authorization, the body of this endpoind is:
username: user and password: password123, Content-type: x-www-form-urlencoded
2. /posts (GET) add the Header Authorization with the value of token that you create above.
3. /posts (POST) add the Header and the body in JSON format : 
{
  "title": "post ",
  "content": "Contenido"
}
4. /posts/{postId} (DELETE)
5. /posts/{postID}/comments (GET)
6. /posts/{postID}/comments (POST) body : 
7. {
 "comment": "comment"
 }
Regards
