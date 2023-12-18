## Lendme Platform
Lendme is a light-weight lending platform to allow lenders to offer loans of different kinds.

## How Lendme works!

lendme inner workings is very intuitive and straightforward,
First of all a borrower should create a loan request for borrowers to view, study and probably accept
Then, it's up to the lender to choose whatever loan to fund, if his balance meets the requirements he can fund the loan via Lendme payment gateway!
Lendme internally handle all the payments to make sure all payments are delivered successfully, or refused for some reason! 

## Configuration

#### Redis: Lendme uses redis as a caching provider and as a message broker to interact with celery
#### make sure redis is installed on the system!
redis conigurations are in settings.py file in cache section and celery section

#### Celery: to ensure payment delivery and achieve some kind of reliability Lendme needs Celery workers for two reasons:
 1. Simulate External payment gateway behavior.
 2. celery beat to periodically check for payments status.
 


## How to Start the project
 1. Clone the Repository    `git clone https://github.com/sayedazp/lenme.git`
 2. Start a new virtual environment  `python3 -m venv venv`
 3. Activate the virtual environment `source venv/bin/activate` 
 4. Make migration to prepare the database `python manage.py makemigrations`
 5. Migrate those migrations to create the database `python manage.py migrate`
 6. Run the server via `python manage.py runserver`
 7. Run celery worker via ` celery -A mycelery.celery worker -l info`
 8. Run celery beat via `celery -A mycelery.celery beat -l info`  

## Future Improvements

 - More tests should be added to enhance the test coverage.
 - Functions and modules should be better documented.


## Docs
 - for Api and models documentation I user swagger, once application starts visit `serverurl:port/docs/`
 - if the app is running locally visit `127.0.0.1:8000/docs/`

## Database Schema
 - link will be placed once ready!


