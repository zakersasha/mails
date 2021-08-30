from flask import Flask, request, render_template, flash, redirect, url_for
from celery import Celery
from flask_mail import Mail, Message

from config import broker

app = Flask(__name__)

mail = Mail(app)

celery = Celery(app.name, broker=broker)


@app.route("/mail")
def send_mail():
    msg = Message('Привет', sender='sasha@mailtrap.io', recipients=['sasha@mailtrap.io'])
    msg.body = "hey dude"
    mail.send(msg)
    return "Письмо отправленно"


users = [{'id': '1', 'name': 'sasha', 'email': 'test@mail.ru'}, {'id': '2', 'name': 'paul', 'email': 'test2@mail.ru'}]


@app.route("/mails")
def several_recipients():
    with mail.connect() as conn:
        for user in users:
            message = 'Мое сообщение тебе'
            subject = "Привет"
            msg = Message(sender='sasha@mailtrap.io',
                          recipients=[user['email']],
                          body=message,
                          subject=subject)

            conn.send(msg)
    return "done"


@celery.task
def send_mail_task(data):
    with app.app_context():
        msg = Message("Ping!",
                      sender="sasha",
                      recipients=[data['email']])
        msg.body = data['message']
        mail.send(msg)


@app.route('/celery', methods=['GET', 'POST'])
def start_celery_task():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        data = {}
        data['email'] = request.form['email']
        data['first_name'] = request.form['first_name']
        data['last_name'] = request.form['last_name']
        data['message'] = request.form['message']
        duration = int(request.form['duration'])
        duration_unit = request.form['duration_unit']

        if duration_unit == 'minutes':
            duration *= 60
        elif duration_unit == 'hours':
            duration *= 3600
        elif duration_unit == 'days':
            duration *= 86400

        send_mail.apply_async(args=[data], countdown=duration)
        flash(f"Email will be sent to {data['email']} in {request.form['duration']} {duration_unit}")

        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
