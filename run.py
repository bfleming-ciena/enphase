from app import app

class color:
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'


if __name__ == '__main__':
    print color.RED + "Follow the white rabbit: " + color.BLUE
    app.run(debug=True, host='0.0.0.0', port=5000)


