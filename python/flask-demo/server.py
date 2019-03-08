# remember to import your stuff!!!
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'

@app.route('/')
def index():
    return render_template("index.html")

# always redirect on a post route. Otherwise data can be 
# resubmitted accidentally by the client if they refresh
@app.route('/process', methods=['post'])
def process():
    # request.form information from the client only lasts 
    # one request-response cycle, so we have to stuff it into 
    # the session object using key-value pairs
    session['email'] = request.form['email']
    session['password'] = request.form['password']

    user_info = { # this data will be lost once the route redirects below
        'email': request.form['email'],
        'password': request.form['password']
    }

    return redirect('/success')

@app.route('/success')
def success():
    # this if-else statement below will come in handy with 
    # counter and great number game any time you 
    # need to check if the client has hit your app before
    # restructure it to suit the assignment's needs
    if 'email' not in session:
        return redirect('/')
    else:
        # once you create your session key-value pairs, you have automatic access
        # to it. You don't need to add it to the render_template function below
        return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)