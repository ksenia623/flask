from flask import Flask, request, render_template
import random

print("все работает")
app = Flask(__name__)
numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
phone_book = []
while len(phone_book) < 1000:
    number = "8"
    random.shuffle(numbers)
    for num in numbers:
        number += num
    if number not in phone_book:
        phone_book.append(number)


@app.route("/")
def search():
    return render_template('index.html', phone_book=phone_book)


@app.route("/number")
def number():
    phone = request.args.get("number")
    return f"<h1>Номер {phone} - это мошенники!!!</h1>"


@app.route("/result")
def result():
    poisk = request.args.get("query")
    if poisk in phone_book:
        return f'<a href ="/number?number={poisk}">{poisk}</a>'
    else:
        return f"<h2>Ничего не найдено</h2>"


print("Ok")

if __name__ == "__main__":
    app.run(debug=True)
