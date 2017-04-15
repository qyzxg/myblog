from app import create_app

app = create_app()

if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(debug=True)
