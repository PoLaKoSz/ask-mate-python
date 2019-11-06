import DAL.answers
import DAL.questions
import os
import uuid

__ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def route_list(request):
    order_direction = 'DESC'
    if 'order_direction' in request.args:
        order_direction = request.args.get('order_direction')
    column_name = 'submission_time'
    if 'order_by' in request.args:
        column_name = request.args.get('order_by')
    sorted_questions = DAL.questions.get_questions(column_name, order_direction)
    if order_direction == 'DESC':
        order_direction = 'ASC'
    else:
        order_direction = 'DESC'
    return sorted_questions, order_direction


def add_question(request, upload_image_func, app):
    request_form = dict(request.form)
    __upload_file_if_any(request, request_form, upload_image_func, app)
    DAL.questions.add_new(request_form)


def get_one_question(question_id):
    question_data = DAL.questions.select_one(question_id)
    return question_data


def get_answers_for_a_question(question_id):
    answers = DAL.answers.get_answers_for_a_question(question_id)
    return answers

#
#
# def add_new_answer(question_id):
#     if request.method == 'POST':
#         answer = dict(request.form)
#         answer['question_id'] = question_id
#         __upload_file_if_any(request, answer)
#         data_handler.insert_answer(answer)
#         return redirect(f'/question/{question_id}')
#     question_id = int(question_id)
#     questions = data_handler.get_data('questions')
#     question_row_index = data_handler.get_row_index_by_id(question_id, questions)
#     question = questions[question_row_index]
#     # questions = data_handler.get_data('questions')
#     # title = ''.join([question['title'] for question in questions if question['id'] == int(question_id)])
#     return render_template('answer/create.html', question=question)


def edit_question(request, question_data, send_from_directory, app):
    form_request = dict(request.form)
    __delete_image(question_data, app)
    __upload_file_if_any(request, form_request, send_from_directory, app)
    form_request['view_number'] = question_data['view_number']
    form_request['vote_number'] = question_data['vote_number']
    form_request['id'] = question_data['id']
    DAL.questions.update(form_request)


def question_vote_up(question_id):
    question = DAL.questions.select_one(question_id)
    question['vote_number'] = question['vote_number'] + 1
    DAL.questions.update(question)


def question_vote_down(question_id):
    question = DAL.questions.select_one(question_id)
    question['vote_number'] = question['vote_number'] - 1
    DAL.questions.update(question)


def answer_vote_up(answer_id):
    answer = DAL.answers.select_one(answer_id)
    answer['vote_number'] = answer['vote_number'] + 1
    DAL.answers.update(answer)
    return answer


def answer_vote_down(answer_id):
    answer = DAL.answers.select_one(answer_id)
    answer['vote_number'] = answer['vote_number'] - 1
    DAL.answers.update(answer)
    return answer


def delete_question(question_id, app):
    question = DAL.questions.select_one(question_id)
    question_answers = DAL.answers.get_answers_for_a_question(question_id)
    for answer in question_answers:
        __delete_image(answer, app)
    __delete_image(question, app)
    DAL.questions.delete(question)


def delete_answer(answer_id, app):
    answer = DAL.answers.select_one(answer_id)
    question_id = answer['question_id']
    __delete_image(answer, app)
    DAL.answers.delete(answer)
    return question_id


def __upload_file_if_any(form_request, item, send_from_directory, app):
    """
    Uploads the POST-ed file if the request contains an image.
    :param form_request: POST request from a HTML form.
    :param item: (dict) Question or an Answer entity.
    :return: (None) item['image'] key gets updated with the image ID.
    """

    if form_request.method != 'POST':
        item['image'] = ''
        return None

    if 'image' not in form_request.files:
        item['image'] = ''
        return None

    image = form_request.files['image']

    if image.filename == '':
        item['image'] = ''
        return None

    if image and __allowed_file(image.filename):
        file_extension = os.path.splitext(image.filename)[1]
        filename = str(uuid.uuid1()) + file_extension
        item['image'] = filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    item['image'] = ''


def __allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS


def __delete_image(item, app):
    """Remove image from the disk.

    :param item: (dict) Answer or Question entity.
    :return: (None
    """

    if item['image']:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item['image']))