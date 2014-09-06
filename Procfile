web: gunicorn app:app -p $PORT --preload
init: python db_create.py
populate: python db_populate.py