import os
from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, DateTime, ForeignKey, Text, Enum, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import Session

from .DatabaseHandler import DatabaseHandler
from .ModelEnums import (CommentDownload, NsfwFilter, LimitOperator, PostSortMethod, CommentSortMethod)
from .Exceptions import ExistingNameException
from ..Core import Const
from ..Utils import SystemUtil, Injector


Base = DatabaseHandler.base


class BaseModel(Base):

    __abstract__ = True

    def get_session(self):
        return Session.object_session(self)

    def get_display_date(self, date_time):
        try:
            return date_time.strftime('%m/%d/%Y %I:%M %p')
        except AttributeError:
            return None


class ListAssociation(BaseModel):

    __tablename__ = 'reddit_object_list_association'

    id = Column(Integer, primary_key=True)
    reddit_object_list_id = Column(ForeignKey('reddit_object_list.id'))
    reddit_object_list = relationship('RedditObjectList', backref=backref('list_subscriptions',
                                                                          cascade='all, delete-orphan'))
    reddit_object_id = Column(ForeignKey('reddit_object.id'))
    reddit_object = relationship('RedditObject', backref=backref('list_subscriptions', cascade='all, delete-orphan'))
    date_added = Column(DateTime, default=datetime.now())


class RedditObjectList(BaseModel):

    __tablename__ = 'reddit_object_list'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_created = Column(DateTime, default=datetime.now())
    list_type = Column(String, nullable=False)
    reddit_objects = relationship('RedditObject', secondary='reddit_object_list_association', lazy='dynamic')

    # region List Download Defaults
    post_limit = Column(SmallInteger, default=25)
    post_score_limit = Column(Integer, default=1000)
    post_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    post_sort_method = Column(Enum(PostSortMethod), default=PostSortMethod.NEW)
    avoid_duplicates = Column(Boolean, default=True)
    extract_self_post_links = Column(Boolean, default=False)
    download_self_post_text = Column(Boolean, default=False)
    self_post_file_format = Column(String, default='txt')
    download_videos = Column(Boolean, default=True)
    download_images = Column(Boolean, default=True)
    download_gifs = Column(Boolean, default=True)
    download_nsfw = Column(Enum(NsfwFilter), default=NsfwFilter.INCLUDE)
    extract_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comment_content = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    comment_limit = Column(Integer, default=100)
    comment_score_limit = Column(Integer, default=1000)
    comment_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    comment_sort_method = Column(Enum(CommentSortMethod), default=CommentSortMethod.NEW)
    date_limit = Column(DateTime, nullable=True)
    post_download_naming_method = Column(String, default='%[title]')
    post_save_structure = Column(String, default='%[author_name]')
    comment_naming_method = Column(String, default='%[author_name]-comment')
    comment_save_structure = Column(String, default='%[post_author_name]/Comments/%[post_title]')
    # endregion

    object_type = 'REDDIT_OBJECT_LIST'

    def __str__(self):
        return f'{self.list_type} List: {self.name}'

    def get_default_dict(self):
        return {
            'post_limit': self.post_limit,
            'post_score_limit': self.post_score_limit,
            'post_score_limit_operator': self.post_score_limit_operator,
            'post_sort_method': self.post_sort_method,
            'avoid_duplicates': self.avoid_duplicates,
            'extract_self_post_links': self.extract_self_post_links,
            'download_self_post_text': self.download_self_post_text,
            'self_post_file_format': self.self_post_file_format,
            'download_videos': self.download_videos,
            'download_images': self.download_images,
            'download_gifs': self.download_gifs,
            'download_nsfw': self.download_nsfw,
            'extract_comments': self.extract_comments,
            'download_comments': self.download_comments,
            'download_comment_content': self.download_comment_content,
            'comment_limit': self.comment_limit,
            'comment_score_limit': self.comment_score_limit,
            'comment_score_limit_operator': self.comment_score_limit_operator,
            'comment_sort_method': self.comment_sort_method,
            'date_limit': self.date_limit,
            'post_download_naming_method': self.post_download_naming_method,
            'post_save_structure': self.post_save_structure,
            'comment_naming_method': self.comment_naming_method,
            'comment_save_structure': self.comment_save_structure
        }


class RedditObject(BaseModel):

    __tablename__ = 'reddit_object'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_created = Column(DateTime, nullable=True)
    post_limit = Column(SmallInteger, default=25)
    post_score_limit = Column(Integer, default=1000)
    post_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    post_sort_method = Column(Enum(PostSortMethod), default=PostSortMethod.NEW)
    avoid_duplicates = Column(Boolean, default=True)
    extract_self_post_links = Column(Boolean, default=False)
    download_self_post_text = Column(Boolean, default=False)
    self_post_file_format = Column(String, default='txt')
    download_videos = Column(Boolean, default=True)
    download_images = Column(Boolean, default=True)
    download_gifs = Column(Boolean, default=True)
    download_nsfw = Column(Enum(NsfwFilter), default=NsfwFilter.INCLUDE)
    extract_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comment_content = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    comment_limit = Column(Integer, default=100)
    comment_score_limit = Column(Integer, default=1000)
    comment_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    comment_sort_method = Column(Enum(CommentSortMethod), default=CommentSortMethod.NEW)
    date_added = Column(DateTime, default=datetime.now())
    lock_settings = Column(Boolean, default=False)
    absolute_date_limit = Column(DateTime, default=datetime.fromtimestamp(Const.FIRST_POST_EPOCH))
    date_limit = Column(DateTime, nullable=True)
    download_enabled = Column(Boolean, default=True)
    last_download = Column(DateTime, nullable=True)
    significant = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    inactive_date = Column(DateTime, nullable=True)
    post_download_naming_method = Column(String, default='%[title]')
    post_save_structure = Column(String, default='%[author_name]')
    comment_naming_method = Column(String, default='%[author_name]-comment')
    comment_save_structure = Column(String, default='%[post_author_name]/Comments/%[post_title]')
    new = Column(Boolean, default=True)
    lists = relationship(RedditObjectList, secondary='reddit_object_list_association', lazy='dynamic')

    object_type = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity': 'REDDIT_OBJECT',
        'polymorphic_on':  object_type,
    }

    def __str__(self):
        try:
            return f'{self.object_type}: {self.name}'
        except AttributeError:
            return f'{self.object_type}: {self.id}'

    @property
    def date_created_display(self):
        return self.get_display_date(self.date_created)

    @property
    def date_added_display(self):
        return self.get_display_date(self.date_added)

    @property
    def absolute_date_limit_display(self):
        return self.get_display_date(self.absolute_date_limit)

    @property
    def date_limit_display(self):
        return self.get_display_date(self.date_limit)

    @property
    def last_download_display(self):
        return self.get_display_date(self.last_download)

    @property
    def inactive_date_display(self):
        return self.get_display_date(self.inactive_date)

    @property
    def run_comment_operations(self):
        return any((self.extract_comments != CommentDownload.DO_NOT_DOWNLOAD,
                    self.download_comments != CommentDownload.DO_NOT_DOWNLOAD,
                    self.download_comment_content != CommentDownload.DO_NOT_DOWNLOAD))

    def set_date_limit(self, epoch):
        """
        Tests the supplied epoch time to see if it is newer than the already established absolute date limit, and if so
        sets the absolute date limit to the time of the supplied epoch.
        :param epoch: A datetime in epoch seconds that should be the time of an extracted submission.
        """
        date_limit_epoch = self.absolute_date_limit.timestamp()
        if epoch > date_limit_epoch:
            self.absolute_date_limit = datetime.fromtimestamp(epoch)
            self.get_session().commit()

    def set_inactive(self):
        self.active = False
        self.inactive_date = datetime.now()
        self.get_session().commit()

    def toggle_enable_download(self):
        self.download_enabled = not self.download_enabled
        self.get_session().commit()

    def get_post_count(self):
        return len(self.posts)

    def get_downloaded_posts(self):
        session = self.get_session()
        posts = session.query(Post).filter(Post.author == self)

    def get_non_downloaded_posts(self):
        pass

    def get_downloaded_comments(self):
        pass

    def get_downloaded_content(self):
        pass

    def get_non_downloaded_content(self):
        pass


@event.listens_for(RedditObject.name, 'set')
def check_duplicate_name(target, value, oldValue, initiator):
    match = target.get_session().query(RedditObject.id)\
        .filter(RedditObject.object_type == target.object_type)\
        .filter(RedditObject.name == value).first()
    if match is not None:
        raise ExistingNameException(f'A {target.object_type} with the name {value} already exists in the database')


class User(RedditObject):

    __tablename__ = 'user'

    id = Column(ForeignKey('reddit_object.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'USER',
    }


class Subreddit(RedditObject):

    __tablename__ = 'subreddit'

    id = Column(ForeignKey('reddit_object.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'SUBREDDIT',
    }


class DownloadSession(BaseModel):

    __tablename__ = 'download_session'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    extraction_thread_count = Column(Integer, nullable=True)
    download_thread_count = Column(Integer, nullable=True)

    def __str__(self):
        return f'DownloadSession: {self.id}'

    @property
    def start_time_display(self):
        return self.get_display_date(self.start_time)

    @property
    def end_time_display(self):
        return self.get_display_date(self.end_time)

    @property
    def duration(self):
        try:
            return SystemUtil.get_duration_str(self.start_time.timestamp(), self.end_time.timestamp())
        except AttributeError:
            return 'Never finished'

    @property
    def duration_epoch(self):
        return self.start_time.timestamp() - self.end_time.timestamp()

    def get_session_users(self):
        pass

    def get_session_subreddits(self):
        pass

    def get_downloaded_reddit_object_count(self, session=None):
        if session is None:
            session = self.get_session()
        subquery = session.query(Post.significant_reddit_object_id).filter(Post.download_session_id == self.id)
        return session.query(RedditObject.id).filter(RedditObject.id.in_(subquery)).count()

    def get_downloaded_reddit_objects(self, session=None):
        if session is None:
            session = self.get_session()
        subquery = session.query(Post.significant_reddit_object_id).filter(Post.download_session_id == self.id)
        return session.query(RedditObject).filter(RedditObject.id.in_(subquery))


@event.listens_for(DownloadSession, 'before_insert')
def set_download_session_name(mapper, connection, target):
    try:
        number = target.get_session().query(DownloadSession.id).order_by(DownloadSession.id.desc()).first()[0] + 1
    except TypeError:
        number = 1
    target.name = f'Download Session {number}'


class Post(BaseModel):

    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    date_posted = Column(DateTime)
    domain = Column(String)
    score = Column(Integer)
    nsfw = Column(Boolean, default=False)
    reddit_id = Column(String, unique=True)
    url = Column(String)

    is_self = Column(Boolean, default=False)
    text = Column(Text, nullable=True)
    text_html = Column(Text, nullable=True)

    extracted = Column(Boolean, default=False)
    extraction_date = Column(DateTime, nullable=True)
    extraction_error = Column(String, nullable=True)

    author_id = Column(ForeignKey('user.id'))
    author = relationship('User', foreign_keys=author_id, backref='posts')
    subreddit_id = Column(ForeignKey('subreddit.id'))
    subreddit = relationship('Subreddit', foreign_keys=subreddit_id, backref='posts')
    significant_reddit_object_id = Column(ForeignKey('reddit_object.id'))
    significant_reddit_object = relationship('RedditObject', foreign_keys=significant_reddit_object_id,
                                             backref='significant_posts')
    download_session_id = Column(ForeignKey('download_session.id'))
    download_session = relationship('DownloadSession', backref='posts')  # session where the post was extracted

    def __str__(self):
        return f'Post: {self.title}'

    @property
    def short_title(self):
        return self.title[:Injector.get_settings_manager().short_title_char_length]

    @property
    def date_posted_display(self):
        return self.get_display_date(self.date_posted)

    @property
    def score_display(self):
        return '{:,}'.format(self.score)

    def set_extracted(self):
        self.extracted = True
        self.extraction_date = datetime.now()
        self.get_session().commit()

    def set_extraction_failed(self, message):
        self.extracted = False
        self.extraction_date = datetime.now()
        self.extraction_error = message
        self.get_session().commit()


class Comment(BaseModel):

    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    body = Column(String)
    body_html = Column(String)
    score = Column(Integer)
    date_added = Column(DateTime, default=datetime.now())
    date_posted = Column(DateTime)
    reddit_id = Column(String, unique=True)

    extracted = Column(Boolean, default=False)
    has_content = Column(Boolean, default=False)
    extraction_date = Column(DateTime, nullable=True)
    extraction_error = Column(String, nullable=True)

    author_id = Column(ForeignKey('user.id'))
    author = relationship('User', foreign_keys=author_id, backref='comments')
    subreddit_id = Column(ForeignKey('subreddit.id'))
    subreddit = relationship('Subreddit', foreign_keys=subreddit_id, backref='comments')
    post_id = Column(ForeignKey('post.id'))
    post = relationship('Post', backref='comments')
    parent_id = Column(ForeignKey('comment.id'), nullable=True)
    parent = relationship('Comment', remote_side=[id], backref='children')
    download_session_id = Column(ForeignKey('download_session.id'))
    download_session = relationship('DownloadSession', backref='comments')  # session where the comment was extracted

    def __str__(self):
        return f'Comment: {self.id}'

    @property
    def date_posted_display(self):
        return self.get_display_date(self.date_posted)

    @property
    def score_display(self):
        return '{:,}'.format(self.score)

    @property
    def post_title(self):
        return self.post.title

    @property
    def short_post_title(self):
        return self.post.short_title

    def set_extracted(self):
        self.extracted = True
        self.extraction_date = datetime.now()
        self.get_session().commit()

    def set_extraction_failed(self, message):
        self.extracted = False
        self.extraction_date = datetime.now()
        self.extraction_error = message
        self.get_session().commit()


class Content(BaseModel):

    __tablename__ = 'content'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    download_title = Column(String, nullable=True)
    extension = Column(String)
    url = Column(String)
    directory_path = Column(String, nullable=True)

    downloaded = Column(Boolean, default=False)
    download_date = Column(DateTime, nullable=True)
    download_error = Column(String, nullable=True)

    user_id = Column(ForeignKey('user.id'))
    user = relationship('User', backref='content')
    subreddit_id = Column(ForeignKey('subreddit.id'))
    subreddit = relationship('Subreddit', backref='content')
    post_id = Column(ForeignKey('post.id'), nullable=True)
    post = relationship('Post', backref='content')
    comment_id = Column(ForeignKey('comment.id'), nullable=True)
    comment = relationship('Comment', backref='content')
    download_session_id = Column(ForeignKey('download_session.id'), nullable=True)
    # The session in which this content was actually downloaded.  May differ from the parent post/comment
    # download_session if the content was unable to be downloaded during the same session, and was downloaded at a
    # later date.
    download_session = relationship('DownloadSession', backref='content')

    def __str__(self):
        return f'Content: {self.title}'

    @property
    def short_title(self):
        return self.title[:Injector.get_settings_manager().short_title_char_length]

    def get_full_file_path(self, download_title=None):
        if not download_title:
            download_title = self.download_title
        return os.path.join(self.directory_path, f'{download_title}.{self.extension}')

    def set_downloaded(self, download_session_id):
        self.download_session_id = download_session_id
        self.downloaded = True
        self.download_date = datetime.now()
        self.get_session().commit()

    def set_download_error(self, message):
        self.downloaded = False
        self.download_error = message
        self.get_session().commit()
