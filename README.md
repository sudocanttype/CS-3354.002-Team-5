Class: 3354.002
Team: 05
Professor: Srimathi Srinivasan

# Team Details
Team 05
Team Name: TBD

Team Names:
Ahmed Sherwani
Elsha Valluru
Oscar Lay
Uma Uppuloori
Jenny Chan
Anush Kambala
Veronika Mangotic
Antony Sajesh
Elsha Valluru

# How to Boot Website Locally on Your Computer(Without Installations)
1. Just click this link to see the web app: https://nom-nombitesapp.onrender.com
2. Use login credentials username: asherwani1, password: abc or make a new account and login to see the features of the web app.

# How to Boot Website Locally on Your Computer
Prerequisites: Python IDE of your choice and installing Python libarys from https://www.python.org/

1. Click the green button "Code" and click "Download ZIP" or clone using GitBash from the repository. Check where the repository was cloned or downloaded, feel free to move the project anywhere on your computer.
2. Start up your IDE and open the project where it is saved. NOTE some IDE's require to click import project to recognize it as a python project.
3. Find the terminal in your IDE or open the Command Prompt and cd into the project. Should be something like this Ahmeds-MacBook-Air CS-3354.002-Team-5 % .
4. Check if python has been installed do "python --version".
5. If installed, do "pip install Flask". This will install Flask Framework for python.
6. Check if Flask Framework has been installed. Do "pip show Flask". Should show detailed info about the Flask package if it's installed.
7. If installed, do "pip install boto3". This will install the Amazon DynamoDB connection.
8. Check if boto3 is installed do "pip show boto3". Should show the details of boto3.
9. If installed, do "pip install stripe". This will install Stripe payment packages.
10. Check if Stripe has been installed do "pip show stripe". This should show the details.
11. If installed do, "pip install python-dotenv". This will install the environmental variables for Python.
12. Check if the environmental variables for Python have been installed. Do "pip show python-dotenv". This should show the details.
13. In the root of the project create a ".env" file. Open the terminal in you IDE and check you are in the project and type "touch .env" . This should create a .env file.
14. Open the .env file in your IDE or terminal and paste this "STRIPE_SECRET_KEY=sk_test_your_real_secret_key_here". Please reach out to Team 5 for the secret key. 
9. Run the application by clicking the play button in your IDE or do "python app.py". This will run the application, and you should see something like this "Running on http://127.0.0.1:5000/" . Copy and paste the link into your browser of choice, and you should see the website. NOTE setup is NOT complete.
10. Next, do "aws configure" in your terminal to set up DB connection details. If you get an error, you need to install the AWS command line interface. https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
11. For the "aws_access_key_id" please reach out to Team 5 if you don't have secret details. This will be emailed in a excel sheet and will not be in repository for security reasons.
12. For the "aws_secret_access_key" please reach out to Team 5 if you don't have secret details. This will be emailed in a excel sheet and will not be in repository for security reasons.
13. For "region" please reach out please reach out to Team 5 if you don't have secret details. This will be emailed in a excel sheet and will not be in repository for security reasons.
14. For "output" enter: "json" .
15. Next cat the files to see if the AWS configure file is there do "cat ~/.aws/credentials" and "cat ~/.aws/config"
16. Test the connection of the DB. Go to the project and find "test_dynamodb". Run that script file and should print "Connected to DynamoDB!"

You can now run the application!

## Statement of Work: 
Our project aims to help people compile their recipies and generate shopping lists as simply as possible.
