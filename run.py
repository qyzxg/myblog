from app import create_app

app = create_app('default')

if __name__ == '__main__':
    app.jinja_env.cache = {}
    # app.run(host='192.168.1.109', debug=True, port=8080)
    app.run(host='www.qyzxg.com', debug=True, port=80)
