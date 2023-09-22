# YpoxreotikiErgasiaSept23_E18013_Nikolaos-Xaralampos-Arvanitis

To activate and use this web service, follow these steps:

1.Install Docker on your computer. Docker enables you to create and activate individual images and containers. The necessary creation commands can be found in the docker_compose and Dockerfile files.

2.Build the Docker images and containers by running the command "docker-compose up --build." This command will create the docker-compose_flask-service and mongo images along with their respective containers on your computer.

3.Once the installation is complete, the web service is automatically installed and ready to be used. The endpoints within the service_code.py file can now be executed.

4.Make sure your system has applications or programs that support HTTP methods like 'GET,' 'POST,' 'PUT,' 'PATCH,' and others. These methods are essential for implementing data endpoints. Web browsers typically only support the GET method.

5.After completing the above steps, you can choose and execute different endpoints according to your preference.

6. Install in your computer Postman and mongo db . Through postman you will be able to use the application in a friendly enviroment where you can add and extract data . Once you installed mongodb Create a new database "UnipyLibrary" and the collectons : admins , users , books , reservations . After the creation of the database run the DummyData.py so you can populate the database with some dummy data so you can use the application for testing . If you are done with your testing you can connect with the actual UnipyLibrary and the app will serve your desired purposes . 

Admin related Endpoints :

POST http://127.0.0.1:5000/admin/login : is used to access additional endpoints. Keep in mind that if you logout or if you are not loged in you will not be able to use the authorized endpoints. 

GET http://127.0.0.1:5000/admin/logout : is used to log out from the application .
 
POST http://127.0.0.1:5000/admin/add_book : Create a new book using JSON data.

POST http://127.0.0.1:5000/admin/update_loan_days/<string:ISBN>: Update loan days of a book my its ISBN

DELETE http://127.0.0.1:5000/admin/delete_book/<string:ISBN>: Delete a book by its ISBN

GET http://127.0.0.1:5000/admin/searchBooks: Search for books through the database

GET http://127.0.0.1:5000/admin/bookDetails/<string:ISBN> : See a book's details by it's unique ISBN


User related endpoints :

POST http://127.0.0.1:5000/createUser : is used for a new user creation , Keep in mind that an email can not be used for more than one user creations . 

POST http://127.0.0.1:5000/login : is used for user's login . Keep in mind that without Loging in you will not be able to use any endpoint . 

POST http://127.0.0.1:5000/logout : is used for user's log out . Once you log out you will not be able to use any endpoint until you log in again . 

DELETE http://127.0.0.1:5000/deleteUser/<string:user_id> : is used for deleting a user's account by it's users id . 

GET http://127.0.0.1:5000/getbook : is used for searching a book via certain characteristics like title , author , Publish day , ISBN or you can view every book in the database 

GET http://127.0.0.1:5000/viewbooks : is used for viewing every book in the database

GET http://127.0.0.1:5000/viewBookISBN/<string:ISBN> : is used for viewing details of a spesific book based on it's unique ISBN

POST http://127.0.0.1:5000/reserveBook : is used for reserving a book by its unique ISBN 

GET http://127.0.0.1:5000/userReservations/<string:user_email> : is used for displaying all the reservations for a specific user by it's email 

GET http://127.0.0.1:5000/getReservation/<string:reservation_code> : is used for viewing a reservations details by the unique reservation code 

POST http://127.0.0.1:5000/returnBook/<string:reservation_code> : is used for returning a book by the unique reservation code 
