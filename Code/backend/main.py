import api

if __name__ == "__main__":
    # Picoweb doesn't use debug parameter
    api.app.run(host='0.0.0.0', port=5000)
