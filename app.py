from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def landingpage():  # homepage of application
    return render_template('practicelandingwebpage.html')



@app.route('/loginpage') # when "Get Started" button is clicked redirected to login page
def loginpage():
    return render_template('loginpage.html')

@app.route('/createaccount') #when you click "dont have an account? create one!" in login page
def createaccount():
    return render_template('createaccount.html')

if __name__ == '__main__':
    app.run()
