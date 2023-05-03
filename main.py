import datetime
from flask import Flask, render_template, redirect, request, make_response, session, abort, url_for

from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.users import User
from data.news import News
from data.comments import Comments
from forms.newsform import NewsForm
from forms.user import RegisterForm
from forms.login import LoginForm

dict_of_used_comms = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    # db_session.global_init("db/news.db")

    # app.run()

    app.run(port=7777)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, title='FORUM1514')


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
    news = db_sess.query(News).filter(News.id == id).first()
    print(form.title.data)
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
    comments = db_sess.query(Comments).order_by('id')
    tree = make_tree(comments)
    # for i in make_tree(comments):
    #    print(i.text)
    comments_ben = []
    if tree:
        for i in tree:
            # print(i.created_date)
            user = db_sess.query(User)
            for j in user:
                if j.id == i.user_id:
                    comments_ben.append((i.created_date, j.name, i.text, i.id, i.vlog))
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
    news = db_sess.query(News).filter(News.id == id).first()
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
    comments = db_sess.query(Comments).order_by('id')
    tree = make_tree(comments)

    comments_ben = []
    if tree:
        for i in tree:
            # print(i.created_date)
            user = db_sess.query(User)
            for j in user:
                if j.id == i.user_id:
                    comments_ben.append((i.created_date, j.name, i.text, i.id, i.vlog))
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
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
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
        print(form.email.data)
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
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/<int:userid>')
def profil(userid):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == userid).first()
    news = db_sess.query(News).filter(News.user == user)
    return render_template('user.html', news=news, title=user.name)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
