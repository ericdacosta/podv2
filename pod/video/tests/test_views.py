from django.test import TestCase
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from pod.video.models import Channel
from pod.video.models import Theme
from pod.video.models import Video
from pod.video.models import Type
from pod.video.models import Discipline
from pod.video.models import Notes

import os
import re


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class ChannelTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        c = Channel.objects.create(title="ChannelTest1")
        Channel.objects.create(title="ChannelTest2")
        Theme.objects.create(
            title="Theme1", slug="blabla",
            channel=Channel.objects.get(title="ChannelTest1"))
        user = User.objects.create(username="pod", password="pod1234pod")
        v = Video.objects.create(
            title="Video1", owner=user, video="test.mp4", is_draft=False,
            type=Type.objects.get(id=1))
        v.channel.add(c)
        v.save()

    def test_get_channel_view(self):
        self.client = Client()
        response = self.client.get(
            "/%s/" % Channel.objects.get(title="ChannelTest1").slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["channel"],
            Channel.objects.get(title="ChannelTest1"))
        self.assertEqual(
            response.context["theme"], None)
        self.assertEqual(
            response.context["videos"].paginator.count, 1)
        print(
            "   --->  test_channel_without_theme"
            "_in_argument of ChannelTestView : OK !"
        )
        response = self.client.get(
            "/%s/" % Channel.objects.get(title="ChannelTest2").slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["channel"],
            Channel.objects.get(title="ChannelTest2"))
        self.assertEqual(
            response.context["theme"], None)
        self.assertEqual(
            response.context["videos"].paginator.count, 0)
        print(
            "   --->  test_channel_2_without_theme_in_argument"
            " of ChannelTestView : OK !")
        response = self.client.get(
            "/%s/%s/" % (
                Channel.objects.get(title="ChannelTest1").slug,
                Theme.objects.get(title="Theme1").slug)
        )
        self.assertEqual(response.status_code, 200)
        print(
            "   --->  test_channel_with_theme_in_argument"
            " of ChannelTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class MyChannelsTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        User.objects.create(username="pod2", password="pod1234pod")
        c1 = Channel.objects.create(title="ChannelTest1")
        c1.owners.add(user)
        c2 = Channel.objects.create(title="ChannelTest2")
        c2.owners.add(user)
        print(" --->  SetUp of MyChannelsTestView : OK !")

    def test_get_mychannels_view(self):
        self.client = Client()
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/my_channels/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["channels"].count(), 2)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/my_channels/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["channels"].count(), 0)
        print(" --->  test_get_mychannels_view of MyChannelsTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class ChannelEditTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        User.objects.create(username="pod2", password="pod1234pod")
        c1 = Channel.objects.create(title="ChannelTest1")
        c1.owners.add(user)
        print(" --->  SetUp of ChannelEditTestView : OK !")

    def test_channel_edit_get_request(self):
        self.client = Client()
        channel = Channel.objects.get(title="ChannelTest1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/channel_edit/slugauhasard/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/channel_edit/%s/" % channel.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, channel)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/channel_edit/%s/" % channel.slug)
        self.assertEqual(response.status_code, 403)
        print(
            " --->  test_channel_edit_get_request"
            " of ChannelEditTestView : OK !")

    def test_channel_edit_post_request(self):
        self.client = Client()
        channel = Channel.objects.get(title="ChannelTest1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.post(
            '/channel_edit/%s/' % channel.slug, {
                'title': "ChannelTest1",
                'description': '<p>bl</p>\r\n'
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"The changes have been saved." in response.content)
        c = Channel.objects.get(title="ChannelTest1")
        self.assertEqual(c.description, '<p>bl</p>')
        print(
            "   --->  test_channel_edit_post_request"
            " of ChannelEditTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class ThemeEditTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        c1 = Channel.objects.create(title="ChannelTest1")
        c1.owners.add(user)
        Theme.objects.create(
            title="Theme1", slug="theme1",
            channel=Channel.objects.get(title="ChannelTest1"))
        Theme.objects.create(
            title="Theme2", slug="theme2",
            channel=Channel.objects.get(title="ChannelTest1"))
        Theme.objects.create(
            title="Theme3", slug="theme3",
            channel=Channel.objects.get(title="ChannelTest1"))
        print(" --->  SetUp of ThemeEditTestView : OK !")

    def test_theme_edit_get_request(self):
        self.client = Client()
        channel = Channel.objects.get(title="ChannelTest1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/theme_edit/%s/" % channel.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['channel'], channel)
        self.assertEqual(
            response.context['form_theme'].initial['channel'], channel)
        self.assertEqual(channel.themes.all().count(), 3)
        print(" --->  test_theme_edit_get_request of ThemeEditTestView : OK !")

    def test_theme_edit_post_request(self):
        self.client = Client()
        channel = Channel.objects.get(title="ChannelTest1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        # action new
        response = self.client.post(
            '/theme_edit/%s/' % channel.slug, {
                'action': "new"
            }, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['channel'], channel)
        self.assertEqual(
            response.context['form_theme'].initial['channel'], channel)
        # action modify
        response = self.client.post(
            '/theme_edit/%s/' % channel.slug, {
                'action': "modify",
                'id': 1
            }, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['channel'], channel)
        theme = Theme.objects.get(id=1)
        self.assertEqual(response.context['form_theme'].instance, theme)
        # action delete
        self.assertEqual(channel.themes.all().count(), 3)
        response = self.client.post(
            '/theme_edit/%s/' % channel.slug, {
                'action': "delete",
                'id': 1
            }, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['channel'], channel)
        self.assertEqual(
            Channel.objects.get(title="ChannelTest1").themes.all().count(), 2)
        # action save
        # save new one
        response = self.client.post(
            '/theme_edit/%s/' % channel.slug, {
                'action': "save",
                'title': "Theme4",
                'channel': Channel.objects.get(title="ChannelTest1").id
            }, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['channel'], channel)
        theme = Theme.objects.get(title="Theme4")
        self.assertEqual(
            Channel.objects.get(title="ChannelTest1").themes.all().count(), 3)
        # save existing one
        response = self.client.post(
            '/theme_edit/%s/' % channel.slug, {
                'action': "save",
                'theme_id': 3,
                'title': "Theme3-1",
                'channel': Channel.objects.get(title="ChannelTest1").id
            }, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['channel'], channel)
        theme = Theme.objects.get(id=3)
        self.assertEqual(theme.title, "Theme3-1")
        print(
            " --->  test_theme_edit_post_request of ThemeEditTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class MyVideosTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        user2 = User.objects.create(username="pod2", password="pod1234pod")
        Video.objects.create(
            title="Video1", owner=user, video="test1.mp4", is_draft=False,
            type=Type.objects.get(id=1))
        Video.objects.create(
            title="Video2", owner=user, video="test2.mp4",
            type=Type.objects.get(id=1))
        Video.objects.create(
            title="Video3", owner=user, video="test3.mp4", is_draft=False,
            type=Type.objects.get(id=1))
        Video.objects.create(
            title="Video4", owner=user2, video="test4.mp4", is_draft=False,
            type=Type.objects.get(id=1))
        print(" --->  SetUp of MyChannelsTestView : OK !")

    def test_get_myvideos_view(self):
        self.client = Client()
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/my_videos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 3)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/my_videos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 1)
        print(" --->  test_get_myvideos_view of MyVideosTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class VideosTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        # type, discipline, owner et tag
        user = User.objects.create(username="pod", password="pod1234pod")
        user2 = User.objects.create(username="pod2", password="pod1234pod")
        t1 = Type.objects.create(title="Type1")
        t2 = Type.objects.create(title="Type2")
        d1 = Discipline.objects.create(title="Discipline1")
        d2 = Discipline.objects.create(title="Discipline2")

        v = Video.objects.create(
            title="Video1", type=t1, tags='tag1 tag2', owner=user,
            video="test1.mp4", is_draft=False)
        v.discipline.add(d1, d2)
        v = Video.objects.create(
            title="Video2", type=t2, tags='tag1 tag2', owner=user,
            video="test2.mp4")
        v.discipline.add(d1, d2)
        v = Video.objects.create(
            title="Video3", type=t1, owner=user, video="test3.mp4",
            is_draft=False)
        v = Video.objects.create(
            title="Video4", type=t2, tags='tag1', owner=user2,
            video="test4.mp4", is_draft=False)
        v.discipline.add(d1)
        v = Video.objects.create(
            title="Video5", type=t1, tags='tag2', owner=user2,
            video="test4.mp4", is_draft=False)
        v.discipline.add(d2)
        print(" --->  SetUp of VideosTestView : OK !")

    def test_get_videos_view(self):
        self.client = Client()
        response = self.client.get("/videos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 4)
        # type
        response = self.client.get("/videos/?type=type1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 3)
        response = self.client.get("/videos/?type=type2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 1)
        response = self.client.get("/videos/?type=type2&type=type1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 4)
        # discipline
        response = self.client.get("/videos/?discipline=discipline1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 2)
        response = self.client.get("/videos/?discipline=discipline2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 2)
        response = self.client.get(
            "/videos/?discipline=discipline1&discipline=discipline2"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 3)
        # owner
        response = self.client.get("/videos/?owner=pod")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 2)
        response = self.client.get("/videos/?owner=pod2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 2)
        response = self.client.get("/videos/?owner=pod&owner=pod2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 4)
        # tag
        response = self.client.get("/videos/?tag=tag1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 2)
        response = self.client.get("/videos/?tag=tag2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 2)
        response = self.client.get("/videos/?tag=tag1&tag=tag2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["videos"].paginator.count, 3)
        print(" --->  test_get_videos_view of VideosTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class VideoTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        # type, discipline, owner et tag
        user = User.objects.create(username="pod", password="pod1234pod")
        User.objects.create(username="pod2", password="pod1234pod")
        Group.objects.create(name='student')
        Group.objects.create(name='employee')
        Group.objects.create(name='member')
        Video.objects.create(
            title="Video1", owner=user,
            video="test1.mp4", type=Type.objects.get(id=1))

    def test_video_get_request(self):
        v = Video.objects.get(title="Video1")
        self.assertEqual(v.is_draft, True)
        # test draft
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 302)
        self.client = Client()
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 200)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 403)
        # test normal
        self.client.logout()
        v.is_draft = False
        v.save()
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 200)
        # test restricted
        v.is_restricted = True
        v.save()
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 302)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 200)
        # test restricted group
        v.restrict_access_to_groups.add(Group.objects.get(name='employee'))
        v.restrict_access_to_groups.add(Group.objects.get(name='member'))
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 403)
        self.user.groups.add(Group.objects.get(name='student'))
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 403)
        self.user.groups.add(Group.objects.get(name='employee'))
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 200)
        # TODO test with password
        v.is_restricted = False
        v.restrict_access_to_groups = []
        v.password = "password"
        v.save()
        self.client.logout()
        response = self.client.get("/video/%s/" % v.slug)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"])
        # TODO test with hashkey
        response = self.client.get("/video/%s/%s/" % (v.slug, v.get_hashkey()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual("form" in response.context.keys(), False)
        v.is_draft = True
        v.save()
        response = self.client.get("/video/%s/%s/" % (v.slug, v.get_hashkey()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual("form" in response.context.keys(), False)


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class VideoEditTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        User.objects.create(username="pod2", password="pod1234pod")
        Video.objects.create(
            title="Video1", owner=user,
            video="test1.mp4", type=Type.objects.get(id=1))
        print(" --->  SetUp of VideoEditTestView : OK !")

    def test_video_edit_get_request(self):
        self.client = Client()
        response = self.client.get("/video_edit/")
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(title="Video1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/video_edit/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/video_edit/slugauhasard/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/video_edit/%s/" % video.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, video)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/video_edit/%s/" % video.slug)
        self.assertEqual(response.status_code, 403)
        print(
            " --->  test_video_edit_get_request"
            " of VideoEditTestView : OK !")

    def test_video_edit_post_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        # modify one
        response = self.client.post(
            '/video_edit/%s/' % video.slug, {
                'title': "VideoTest1",
                'description': '<p>bl</p>\r\n',
                'main_lang': 'fr',
                'cursus': "0",
                'type': 1
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        # print(response.context["form"].errors)
        self.assertTrue(b"The changes have been saved." in response.content)
        v = Video.objects.get(title="VideoTest1")
        self.assertEqual(v.description, '<p>bl</p>')
        videofile = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4")
        response = self.client.post(
            '/video_edit/%s/' % v.slug, {
                'video': videofile,
                'title': "VideoTest1",
                'main_lang': 'fr',
                'cursus': "0",
                'type': 1
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"The changes have been saved." in response.content)
        v = Video.objects.get(title="VideoTest1")
        p = re.compile(r'^videos/([\d\w]+)/file([_\d\w]*).mp4$')
        self.assertRegexpMatches(v.video.name, p)
        # new one
        videofile = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4")
        self.client.post(
            '/video_edit/',
            {
                'video': videofile,
                'title': "VideoTest2",
                'description': '<p>coucou</p>\r\n',
                'main_lang': 'fr',
                'cursus': "0",
                'type': 1
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"The changes have been saved." in response.content)
        v = Video.objects.get(title="VideoTest2")

        print(
            "   --->  test_video_edit_post_request"
            " of VideoEditTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class video_deleteTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        User.objects.create(username="pod2", password="pod1234pod")
        Video.objects.create(
            title="Video1", owner=user,
            video="test1.mp4", type=Type.objects.get(id=1))
        print(" --->  SetUp of video_deleteTestView : OK !")

    def test_video_delete_get_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        response = self.client.get("/video_delete/%s/" % video.slug)
        self.assertEqual(response.status_code, 302)
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/video_delete/slugauhasard/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/video_delete/%s/" % video.slug)
        self.assertEqual(response.status_code, 200)
        self.user = User.objects.get(username="pod2")
        self.client.force_login(self.user)
        response = self.client.get("/video_delete/%s/" % video.slug)
        self.assertEqual(response.status_code, 403)
        print(
            " --->  test_video_edit_get_request"
            " of video_deleteTestView : OK !")

    def test_video_delete_post_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.post(
            "/video_delete/%s/" % video.slug,
            {
                'agree': True,
            })
        self.assertRedirects(response, '/my_videos/')
        self.assertEqual(Video.objects.all().count(), 0)
        print(
            " --->  test_video_edit_post_request"
            " of video_deleteTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class video_notesTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        Video.objects.create(
            title="Video1", owner=user,
            video="test1.mp4", type=Type.objects.get(id=1))
        print(" --->  SetUp of video_notesTestView : OK !")

    def test_video_notesTestView_get_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        response = self.client.get("/video/%s/" % video.slug)
        note = Notes.objects.get(
            user=User.objects.get(username="pod"),
            video=video)
        self.client.logout()
        response = self.client.get("/video_notes/%s/" % note.id)
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get("/video_notes/%s/" % note.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notesForm'].instance, note)
        print(
            " --->  test_video_notesTestView_get_request"
            " of video_notesTestView : OK !")

    def test_video_notesTestView_post_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        self.user = User.objects.get(username="pod")
        self.client.force_login(self.user)
        note = Notes.objects.create(
            user=User.objects.get(username="pod"),
            video=video)
        self.assertEqual(note.note, None)
        response = self.client.post(
            "/video_notes/%s/" % note.id,
            {
                'user': self.user.id,
                'video': video.id,
                'note': 'coucou'
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"The note has been saved." in response.content)
        note = Notes.objects.get(
            user=User.objects.get(id=self.user.id),
            video=video)
        self.assertEqual(note.note, 'coucou')
        print(
            " --->  test_video_notesTestView_post_request"
            " of video_notesTestView : OK !")


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class video_countTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(username="pod", password="pod1234pod")
        Video.objects.create(
            title="Video1", owner=user,
            video="test1.mp4", type=Type.objects.get(id=1))
        print(" --->  SetUp of video_countTestView : OK !")

    def test_video_countTestView_get_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        response = self.client.get("/video_count/2/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/video_count/%s/" % video.id)
        self.assertEqual(response.status_code, 403)
        print(
            " --->  test_video_countTestView_get_request"
            " of video_countTestView : OK !")

    def test_video_countTestView_post_request(self):
        self.client = Client()
        video = Video.objects.get(title="Video1")
        print("count : %s" % video.get_viewcount())
        self.assertEqual(video.get_viewcount(), 0)
        response = self.client.post(
            "/video_count/%s/" % video.id,
            {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"ok" in response.content)
        self.assertEqual(video.get_viewcount(), 1)
        print(
            " --->  test_video_countTestView_post_request"
            " of video_countTestView : OK !")
