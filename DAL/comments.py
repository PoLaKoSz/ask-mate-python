import connection


@connection.connection_handler
def get_comments_for_a_question(cursor, question_id):
    cursor.execute("""
                    SELECT * FROM comment
                    WHERE question_id = %(question_id)s
                    ORDER BY id ASC;
                    """,
                   {
                       'question_id': question_id
                   })
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def add_new(cursor, data):
    cursor.execute("""
                    INSERT INTO comment (question_id, answer_id, message)
                    VALUES
                        (%(question_id)s, %(answer_id)s, %(message)s);
                    """,
                   {
                       'question_id': data['question_id'],
                       'answer_id': data['answer_id'],
                       'message': data['message'],
                   })