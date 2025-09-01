#!/bin/bash
source ../.env

export PGPASSWORD=$DB_PASSWORD  # Password can't be specified over psql param key, only via env

psql -U $DB_USER -d $DB_NAME -p $DB_PORT -h $DB_HOST -c "
DROP TABLE IF EXISTS public.collections CASCADE;
DROP TABLE IF EXISTS public.m2m_collections_posts CASCADE;
DROP TABLE IF EXISTS public.personal_posts CASCADE;
DROP TABLE IF EXISTS public.personal_votes CASCADE;
DROP TABLE IF EXISTS public.photos CASCADE;
DROP TABLE IF EXISTS public.posts_base CASCADE;
DROP TABLE IF EXISTS public.public_posts CASCADE;
DROP TABLE IF EXISTS public.public_votes CASCADE;
DROP TABLE IF EXISTS public.shown_users CASCADE;
DROP TABLE IF EXISTS public.user_photos CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;
DROP TABLE IF EXISTS public.m2m_managers_chats CASCADE;
"

