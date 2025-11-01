from flask import Flask, request
import random
print("все работает")
app = Flask(__name__)
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
phone_book = []
while len(phone_book) < 1000:
    number = '8'
    random.shuffle(numbers)
    for num in numbers:
        number += num 
    if number not in phone_book:
        phone_book.append(number)

@app.route('/')
def search():
    search_html = '''<h1>Поиск</h1> <form action="/result" method="GET">
        <input type="text" name="query">
        <button>Найти</button>
    </form>'''

    number_html = "<h1>Телефонная книга:</h1>"
    for i, number in enumerate(phone_book):
        number_html += f'<a href="/number?number={number}">{number}</a> '
    # Каждые 10 номеров - перенос строки
        if (i + 1) % 10 == 0:
            number_html += '<br>'
    
    return search_html + number_html
@app.route('/number')
def number():
    phone = request.args.get('number')
    return f"<h1>Номер {phone} - это мошенники!!!</h1>"
@app.route('/result')
def result():
    poisk = request.args.get('query')
    if poisk in phone_book:
        return f'<a href ="/number?number={poisk}">{poisk}</a>'
    else:
        return f'<h2>Ничего не найдено</h2>'
print("Ok")

if __name__ == "__main__":
    app.run(debug=True)