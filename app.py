from flask import Flask

from common import init_config
from common.database import config
from routers import init_routers


def main():
    """ Main """

    app = Flask(__name__)

    init_config()

    init_routers(app)

    env = config["environment"]
    app.run(host="0.0.0.0", port=env["port"], debug=int(env["debug"]))


if __name__ == "__main__":
    main()
