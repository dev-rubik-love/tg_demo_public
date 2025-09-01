from app.postconfig import app_logger
from app.tg.ptb import bot
from app.tg.ptb.app import create_ptb_app


def main():
    """
    To run the code use python -m app
    """
    app_logger.info(msg='Main started', )
    application = create_ptb_app(bot=bot, )
    application.run_polling()  # Infinite blocking operation


if __name__ == '__main__':
    main()
