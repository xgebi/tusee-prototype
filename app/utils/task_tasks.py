import uuid
from datetime import datetime
from typing import List, Dict

from flask import jsonify
from psycopg import Cursor

from app import db
from app.utils.audit_log_tasks import log_permission_violation


def get_standalone_tasks_for_user(user_uuid: str) -> List:
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT task_uuid, creator, board, title, description, updated, created, deadline, start_time 
            FROM tusee_tasks WHERE creator = %s AND board = %s""",
            (user_uuid, None)
        )
        temps = cur.fetchall()
        return [task_to_dict(temp) for temp in temps]


def get_tasks_for_board(board_uuid, user_uuid):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("""SELECT board FROM tusee_encrypted_keys WHERE board = %s AND tusee_user = %s""",
                    (board_uuid, user_uuid))
        temp = cur.fetchall()
        if len(temp) == 0:
            raise Exception("Cannot access tasks for this board")
        cur.execute(
            """SELECT task_uuid, creator, board, title, description, updated, created, deadline, start_time 
            FROM tusee_tasks WHERE creator = %s AND board = %s""",
            (user_uuid, board_uuid)
        )
        temps = cur.fetchall()
        return [task_to_dict(temp) for temp in temps]


def create_task(user_uuid, board_uuid, title, description, deadline, start_time):
    task_dict = None
    conn = db.get_connection()
    with conn.cursor() as cur:
        task_uuid = str(uuid.uuid4())
        cur.execute(
            """INSERT INTO tusee_tasks 
            (task_uuid, creator, board, title, description, updated, created, deadline, start_time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING task_uuid, creator, board, title, description, updated, created, deadline, start_time""",
            (task_uuid, user_uuid, board_uuid, title, description, datetime.now(),
             datetime.now(), deadline, start_time))
        temp = cur.fetchone()
        task_dict = task_to_dict(temp)
    conn.commit()
    return task_dict


def get_single_task(task_uuid, user_uuid):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT task_uuid, creator, board, title, description, updated, created, deadline, start_time 
            FROM tusee_tasks WHERE task_uuid = %s""",
            (task_uuid, )
        )
        temp = cur.fetchone()
        if temp is None:
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to access non-existent task {task_uuid} by {user_uuid}"
            )
            return jsonify({}), 403

        task_dict = task_to_dict(temp)

        if task_dict.get('board'):
            cur.execute("""SELECT tusee_user FROM tusee_encrypted_keys WHERE board = %s""",
                        (task_dict.get('board'),))
            temp = cur.fetchall()
            if len(temp) > 0:
                return jsonify(task_dict)
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to access task {task_uuid} on board {task_dict.get('board')} by {user_uuid}"
            )
            return jsonify({}), 403
        else:
            if task_dict.get("creator") == user_uuid:
                return jsonify(task_dict)
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to access task {task_uuid} by {user_uuid}"
            )
            return jsonify({}), 403


def update_task(task, user_uuid):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT task_uuid, creator, board, title, description, updated, created, deadline, start_time 
            FROM tusee_tasks WHERE task_uuid = %s""",
            (task['task_uuid'], )
        )
        temp = cur.fetchone()
        if temp is None:
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to update non-existent task {task['task_uuid']} by {user_uuid}"
            )
            return jsonify({}), 403

        task_dict = task_to_dict(temp)

        if task_dict.get('board'):
            cur.execute("""SELECT tusee_user FROM tusee_encrypted_keys WHERE board = %s""",
                        (task_dict.get('board'),))
            temp = cur.fetchall()
            if len(temp) > 0:
                return jsonify(update_task_db(task_dict)), 200
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to update task {task['task_uuid']} on board {task_dict.get('board')} by {user_uuid}"
            )
            return jsonify({}), 403
        else:
            if task_dict.get("creator") == user_uuid:
                return jsonify(update_task_db(task_dict)), 200
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to update task {task['task_uuid']} by {user_uuid}"
            )
            return jsonify({}), 403


def delete_task(task_uuid, user_uuid):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT task_uuid, creator, board, title, description, updated, created, deadline, start_time 
            FROM tusee_tasks WHERE task_uuid = %s""",
            (task_uuid,)
        )
        temp = cur.fetchone()
        if temp is None:
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to update non-existent task {task_uuid} by {user_uuid}"
            )
            return jsonify({}), 403

        task_dict = task_to_dict(temp)

        if task_dict.get('board'):
            cur.execute("""SELECT tusee_user FROM tusee_encrypted_keys WHERE board = %s""",
                        (task_dict.get('board'),))
            temp = cur.fetchall()
            if len(temp) > 0:
                return jsonify(delete_task_db(cur,task_uuid=task_uuid))
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to update task {task_uuid} on board {task_dict.get('board')} by {user_uuid}"
            )
            return jsonify({}), 403
        else:
            if task_dict.get("creator") == user_uuid:
                return jsonify(delete_task_db(cur,task_uuid=task_uuid))
            log_permission_violation(
                cur=cur,
                user_uuid=user_uuid,
                event=f"Attempted to update task {task_uuid} by {user_uuid}"
            )
            return jsonify({}), 403


def task_to_dict(temp: List) -> Dict:
    return {
        "task_uuid": temp[0],
        "creator": temp[1],
        "board": temp[2],
        "title": temp[3],
        "description": temp[4],
        "updated": temp[5],
        "created": temp[6],
        "deadline": temp[7],
        "start_time": temp[8],
    }


def update_task_db(cur: Cursor, task: Dict):
    cur.execute(
        """UPDATE tusee_tasks 
        SET creator = %s, board = %s, title = %s, description = %s, updated = %s, deadline = %s, start_time = %s
        WHERE task_uuid = %s
        RETURNING task_uuid, creator, board, title, description, updated, created, deadline, start_time""",
        (task["user_uuid"], task["board_uuid"], task["title"], task["description"], datetime.now(),
         task["created"], task["deadline"], task["start_time"], task["task_uuid"]))
    temp = cur.fetchone()
    return task_to_dict(temp)


def delete_task_db(cur: Cursor, task_uuid: str):
    cur.execute(
        """DELETE FROM tusee_tasks WHERE task_uuid = %s""",
        (task_uuid, ))
    return {"deleted": task_uuid}