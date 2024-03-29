import json

import psycopg
from flask import render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_cors import cross_origin

from app.db.db_connection import db_connection
from app.utils.event_tasks import get_events_for_user, get_event_task, update_event_task, create_event_task, delete_event_task
from app.utils.user_tasks import authenticate_user
from app.event import event


@event.route("/api/events", methods=["GET"])
@cross_origin()
@db_connection
def get_events(*args, connection: psycopg.Connection, **kwargs):
    """


    :param connection:
    :param args:
    :param kwargs:
    :return:
    """
    user = authenticate_user(request=request, connection=connection)
    if user:
        return jsonify({
            "token": user["token"],
            "events": get_events_for_user(user_uuid=user['user_uuid'], connection=connection)
        })
    return jsonify({
        "loggedOut": True
    })


@event.route("/api/event/<event_uuid>", methods=["GET"])
@cross_origin()
@db_connection
def get_single_event(*args, event_uuid: str, connection: psycopg.Connection,**kwargs):
    """


    :param connection:
    :param args:
    :param event_uuid:
    :param kwargs:
    :return:
    """
    user = authenticate_user(request=request, connection=connection)
    if user:
        return jsonify({
            "token": user["token"],
            "event": get_event_task(user_uuid=user['user_uuid'], connection=connection, event_uuid=event_uuid)
        })
    return jsonify({
        "loggedOut": True
    })


@event.route("/api/event", methods=["PUT"])
@cross_origin()
@db_connection
def update_event(*args, connection: psycopg.Connection,**kwargs):
    """


    :param connection:
    :param args:
    :param kwargs:
    :return:
    """
    user = authenticate_user(request=request, connection=connection)
    if user:
        event_data = json.loads(request.data)
        return jsonify({
            "token": user["token"],
            "event": update_event_task(user_uuid=user['user_uuid'], connection=connection, event=event_data)
        })
    return jsonify({
        "loggedOut": True
    })


@event.route("/api/event", methods=["POST"])
@cross_origin()
@db_connection
def create_event(*args, connection: psycopg.Connection, **kwargs):
    """


    :param connection:
    :param args:
    :param kwargs:
    :return:
    """
    user = authenticate_user(request=request, connection=connection)
    if user:
        event_data = json.loads(request.data)
        return jsonify({
            "token": user["token"],
            "event": create_event_task(user_uuid=user['user_uuid'], connection=connection, event=event_data)
        })
    return jsonify({
        "loggedOut": True
    })


@event.route("/api/event/<event_uuid>", methods=["DELETE"])
@cross_origin()
@db_connection
def delete_event(*args, event_uuid: str, connection: psycopg.Connection, **kwargs):
    """


    :param connection:
    :param args:
    :param event_uuid:
    :param kwargs:
    :return:
    """
    user = authenticate_user(request=request, connection=connection)
    if user:
        return jsonify({
            "token": user["token"],
            "eventDeleted": delete_event_task(user_uuid=user['user_uuid'], connection=connection, event_uuid=event_uuid)
        })
    return jsonify({
        "loggedOut": True
    })
