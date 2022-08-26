from pymongo import MongoClient
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
import requests
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)


client = MongoClient('localhost', 27017)
db = client.dbjungle

# 초반 경로 설정


@app.route('/')
def home():
    return render_template('index.html')

# todo 입력하기


@app.route('/todo/create', methods=['POST'])
def post_todo():
    # 1. 클라이언트로부터 데이터를 받기
    todo_receive = request.form['todo_give']  # 클라이언트로부터 받는 부분
    # print(todo_receive)
    string = todo_receive.replace(' ', '+')

    url = 'https://www.google.co.kr/search?q='+string
    # print(url)
    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    # print(soup)

    luckyUrl = soup.find('div', class_='yuRUbf').find('a')['href']
    # luckyUrl_use = "'" + luckyUrl + "'"
    # print(luckyUrl_use)

    realData = requests.get(luckyUrl, headers=headers)
    realSoup = BeautifulSoup(realData.text, 'html.parser')

    og_title = realSoup.select_one('meta[property="og:title"]')
    og_description = realSoup.select_one('meta[property="og:description"]')
    og_image = realSoup.select_one('meta[property="og:image"]')

    if(og_image == None or og_title == None or og_description == None):
        return jsonify({'result': 'fail', 'msg': 'not found'})

    url_title = og_title['content']
    url_description = og_description['content']
    url_image = og_image['content']
    # print(url_title, url_description, url_image)

    todo = {'todoText': todo_receive, 'title': url_title,
            'desc': url_description, 'image': url_image, 'url': luckyUrl, 'done': False}
    # print(todo)

    # 3. mongoDB에 데이터를 넣기
    db.todos.insert_one(todo)

    return jsonify({'result': 'success'})

# API 역할을 하는 부분

# todo 목록 읽어오기


@app.route('/todo/read', methods=['GET'])
def read_todos():
    result = list(db.todos.find({}))
    for i in range(len(result)):
        result[i]['_id'] = str(result[i]['_id'])
    return jsonify({'result': 'success', 'todos': result})

# todo 삭제하기


@app.route('/todo/delete', methods=['POST'])
def delete_todos():
    id_receive = request.form['id_give']

    db.todos.delete_one({'_id': ObjectId(id_receive)})
    return jsonify({'result': 'success'})

# todo 완료하기


@app.route('/todo/success', methods=['POST'])
def done_todos():
    id_receive = request.form['id_give']
    if(db.todos.find_one({'_id': ObjectId(id_receive)})['done'] == False):
        db.todos.update_one({'_id': ObjectId(id_receive)},
                            {'$set': {'done': True}})
    elif(db.todos.find_one({'_id': ObjectId(id_receive)})['done'] == True):
        db.todos.update_one({'_id': ObjectId(id_receive)},
                            {'$set': {'done': False}})
    return jsonify({'result': 'success'})

# todo 수정하기


@app.route('/todo/edit', methods=['POST'])
def edit_todos():
    id_receive = request.form['id_give']

    edit_receive = request.form['edit_give']

    print(id_receive, edit_receive)

    string = edit_receive.replace(' ', '+')

    url = 'https://www.google.co.kr/search?q='+string

    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    # print(soup)

    luckyUrl = soup.find('div', class_='yuRUbf').find('a')['href']
    # luckyUrl_use = "'" + luckyUrl + "'"
    # print(luckyUrl)

    realData = requests.get(luckyUrl, headers=headers)
    realSoup = BeautifulSoup(realData.text, 'html.parser')

    og_title = realSoup.select_one('meta[property="og:title"]')
    og_description = realSoup.select_one('meta[property="og:description"]')
    og_image = realSoup.select_one('meta[property="og:image"]')

    # if(og_image == None or og_title == None or og_description == None):
    #     return jsonify({'result': 'fail', 'msg': 'not found'})

    url_title = og_title['content']
    url_description = og_description['content']
    url_image = og_image['content']
    # print(url_title, url_description, url_image)

    db.todos.update_one({'_id': ObjectId(id_receive)}, {'$set': {'todoText': edit_receive,
                        'title': url_title, 'desc': url_description, 'image': url_image, 'url': luckyUrl}})

    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
