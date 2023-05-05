import base64
import datetime
import flask
from flask import Flask, render_template, redirect, request, make_response, session, abort, url_for
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.users import User
from data.news import News
from data.images import Images
from data.comments import Comments
from forms.editacc import EditForm
from forms.newsform import NewsForm
from forms.user import RegisterForm
from forms.login import LoginForm

dict_of_used_comms = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/update/<id>")
def what_kol_comment(id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comments).filter(Comments.news_id == id).order_by('id')
    tree = make_tree(comments)
    comments_ben = []
    if tree:
        for i in tree:
            user = db_sess.query(User)
            for j in user:
                if j.id == i.user_id:
                    img = db_sess.query(Images).filter(Images.user_id == j.id).first()
                    if not img:
                        with open("static/img/1.gif", "rb") as image:
                            f = image.read()
                            b = base64.b64encode(bytearray(f)).decode('ascii')
                            m = 'image/jpg'
                            comments_ben.append(
                                (i.created_date, j.name, i.text, i.id, i.vlog, j.id, b, m))
                    comments_ben.append((i.created_date, j.name, i.text, i.id, i.vlog, id, img.img, img.mimetype))
    db_sess.close()
    return comments_ben


@app.route("/to_our_time/<data>")
def to_strf(data):
    return datetime.datetime.strptime(data, '%a, %d %b %Y %X %Z').strftime('%d.%m.%Y %H:%M')


def main():
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(
           (News.user == current_user) | (News.is_private != True)).order_by(desc(News.created_date)).all()
    else:
        news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(News.is_private != True).join(Images, Images.user_id == News.user_id).order_by(desc(News.created_date)).all()
    return render_template("index.html", news=news, title='FORUM1514')


@app.route('/search')
def search():
    rec = request.args.get('Search')
    message = ''
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(
           ((News.user == current_user) | (News.is_private != True)),
            ((News.title.like(f"%{rec}%")) | (News.content.like(f"%{rec}%")))).order_by(desc(News.created_date)).all()
    else:
        news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(
          News.is_private != True, ((
            News.title.like(f"%{rec}%")) | (News.content.like(f"%{rec}%")))).join(
          Images, Images.user_id == News.user_id).order_by(desc(News.created_date)).all()
    if not news:
        message = "Таких постов не нашлось("
    return render_template("index.html", news=news, title='FORUM1514', message=message)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def news_comment(id):
    form = NewsForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(
        News.id == id).order_by(desc(News.created_date)).first()
    if form.title.data is not None:
        text = form.title.data
        news_id = id
        user_id = current_user.id
        comment = Comments()
        comment.text = text
        comment.user_id = user_id
        comment.news_id = news_id
        comment.created_date = datetime.datetime.now()
        db_sess.add(comment)
        db_sess.commit()
    comments = db_sess.query(Comments).filter(Comments.news_id == id).order_by('id')
    tree = make_tree(comments)
    comments_ben = []
    if tree:
        for i in tree:
            user = db_sess.query(User).all()
            for j in user:
                if j.id == i.user_id:
                    img = db_sess.query(Images).filter(Images.user_id == j.id).first()
                    if not img:
                        with open("static/img/1.gif", "rb") as image:
                            f = image.read()
                            b = base64.b64encode(bytearray(f)).decode('ascii')
                            m = 'image/jpg'
                            comments_ben.append(
                                (i.created_date, j.name, i.text, i.id, i.vlog, j.id, b, m))

                    comments_ben.append((i.created_date, j.name, i.text, i.id, i.vlog, j.id, img.img, img.mimetype))
    if form.validate_on_submit():
        return redirect(f'/news_comment/{id}')
    else:
        return render_template('comment.html',
                               title='Комментирование новости', news=news, form=form, comments=comments_ben)


def make_tree(items):
    tree = []
    for item in items:
        item.children = []
        item.level = 1
        if item.comment_id is None:
            tree.append(item)
        else:
            try:
                parent = [p for p in items if p.id == item.comment_id][0]
                parent.children.append(item)
                item.level = parent.level + 1
            except ValueError:
                tree.append(item)
    return make_all_tree(tree, [])


def make_all_tree(list, ben):
    for i in list:
        ben.append(i)
        if i.children:
            make_all_tree(i.children, ben)
    return ben


@app.route('/news_comment/<int:id>/<int:com_id>', methods=['GET', 'POST'])
@login_required
def news_comment_replay(id, com_id):
    form = NewsForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(
        News.id == id).order_by(desc(News.created_date)).first()
    com = db_sess.query(Comments).filter(Comments.id == com_id).first()
    if form.title.data is not None:
        text = form.title.data
        news_id = id
        user_id = current_user.id
        comment = Comments()
        comment.text = text
        comment.user_id = user_id
        comment.news_id = news_id
        comment.vlog = com.vlog + 3
        comment.comment_id = com_id
        comment.created_date = datetime.datetime.now()
        db_sess.add(comment)
        db_sess.commit()
    comments = db_sess.query(Comments).filter(Comments.news_id == id).order_by('id')
    tree = make_tree(comments)

    comments_ben = []
    if tree:
        for i in tree:
            user = db_sess.query(User).all()
            for j in user:
                if j.id == i.user_id:
                    img = db_sess.query(Images).filter(Images.user_id == j.id).first()
                    if not img:
                        with open("static/img/1.gif", "rb") as image:
                            f = image.read()
                            b = base64.b64encode(bytearray(f)).decode('ascii')
                            m = 'image/jpg'
                            comments_ben.append(
                                (i.created_date, j.name, i.text, i.id, i.vlog, j.id, b, m))
                    comments_ben.append((i.created_date, j.name, i.text, i.id, i.vlog, j.id, img.img, img.mimetype))

    if form.validate_on_submit():
        return redirect(f'/news_comment/{id}')
    else:
        return render_template('comment.html',
                               title='Комментирование новости', news=news, form=form, comments=comments_ben)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            (User.email == form.name_email.data) | (User.name == form.name_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин/имя или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.created_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        with open("static/img/1.gif", "rb") as image:
            f = image.read()
            b = base64.b64encode(bytearray(f)).decode('ascii')
            m = 'image/jpg'
            u = db_sess.query(User).filter(User.email == form.email.data).first().id
            img = Images(img=b, name="1.gif", mimetype=m, user_id=u)
            db_sess.add(img)
            db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/<int:userid>')
def account(userid):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == userid).first()
    news = db_sess.query(News, User, Images).filter(News.user_id == User.id).filter(User.id == Images.user_id).filter(
        User.id == userid).order_by(desc(News.created_date)).all()
    img = db_sess.query(Images).filter(Images.user_id == userid).first()
    if not img:
        with open("static/img/1.gif", "rb") as image:
            f = image.read()
            b = base64.b64encode(bytearray(f)).decode('ascii')
            m = 'image/jpg'
        return render_template('user.html', news=news, title=user.name, img=b, mim=m, user=user)
    return render_template('user.html', news=news, title=user.name, img=img.img, mim=img.mimetype, user=user)


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


@app.route('/editacc/<int:userid>', methods=['GET', 'POST'])
@login_required
def edit_account(userid):
    form = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == userid).first()
        if user:
            form.name.data = user.name
            form.email.data = user.email
            form.about.data = user.about
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        pic = form.avatar.data
        if pic:
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype
            if not filename or not mimetype:
                return 'Bad upload!', 400
            image = db_sess.query(Images).filter(Images.user_id == userid).first()
            if image:
                image.img = render_picture(pic.read())
                image.name = filename
                image.mimetype = mimetype
            else:
                img = Images(img=pic.read(), name=filename, mimetype=mimetype, user_id=userid)
                db_sess.add(img)
            db_sess.commit()

        if db_sess.query(User).filter(((User.email == form.email.data) | (
                User.name == form.name.data)), (User.id != userid)).first():
            return render_template("editacc.html", title='edit',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = db_sess.query(User).filter(User.id == userid).first()
        if user:
            user.name = form.name.data
            user.email = form.email.data
            user.about = form.about.data
            db_sess.commit()
            return redirect(f'/{userid}')
        else:
            abort(404)
    return render_template("editacc.html", title='edit', form=form, userid=userid)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
