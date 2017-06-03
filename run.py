from app import create_app
app = create_app('default')

if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(debug=False)
