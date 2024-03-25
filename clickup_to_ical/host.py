TRUE_VALUES = ("true", "1", "yes", "y", "on")


def main():
    import os
    import logging
    from clickup_to_ical.web import app

    debug_enabled = os.environ.get("DEBUG", "").lower() in TRUE_VALUES
    logging.basicConfig(
        style="{",
        format="{asctime} - {levelname:^8} - {name} - {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if debug_enabled else logging.INFO
    )

    app.run(port=os.environ.get("FLASK_PORT", 8080), debug=debug_enabled)


if __name__ == '__main__':
    main()
