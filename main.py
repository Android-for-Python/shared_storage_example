from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.logger import Logger
from os.path import exists, join
from shutil import rmtree
from textwrap import fill
from android import mActivity, autoclass, api_version

from androidstorage4kivy import SharedStorage, Chooser
from android_permissions import AndroidPermissions

Environment = autoclass('android.os.Environment')

#######################################################################
# Not a real world example, this is the unit tests.
#
# One test (8) depends on Pictures/CHART_4.jpg belonging to another app
# Expect this test to likely fail on some random device.
#######################################################################


class SharedStorageExample(App):

    def build(self):
        Window.bind(on_keyboard=self.quit_app)
        # create chooser listener
        self.chooser = Chooser(self.chooser_callback)

        # cleanup from last time if Android didn't
        temp = SharedStorage().get_cache_dir()
        if temp and exists(temp):
            rmtree(temp)

        # layout
        self.label = Label(text='Greetings Earthlings')
        self.button = Button(text='Choose an image file',
                             on_press=self.chooser_start,
                             size_hint=(1, .15))
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button)
        return self.layout

    def on_start(self):
        self.dont_gc = AndroidPermissions(self.start_app)

    def quit_app(self, window, key, *args):
        if key == 27:
            mActivity.finishAndRemoveTask()
            return True
        return False

    def start_app(self):
        self.dont_gc = None
        ss = SharedStorage()
        app_title = str(ss.get_app_title())
        self.label_lines = []
        self.display()
        self.append("Cache Dir Exists:  " + str(exists(ss.get_cache_dir())))

        ############################################################
        # copy to app shared storage   copy_to_shared(private_file)
        ############################################################

        share0 = ss.copy_to_shared('./test.txt')
        share1 = ss.copy_to_shared('test.txt',
                                   filepath='a/b/test1.txt')
        share2 = ss.copy_to_shared('test.jpg',
                                   filepath=join('c', 'test1.jpg'))
        share3 = ss.copy_to_shared('test.mp3')
        # For .ogg, collection depends on the Android version
        # On newer devices default is DIRECTORY_MUSIC, so DIRECTORY_ALARMS
        # is a legal place.
        # On older devices default is DIRECTORY_DOCUMENTS, so DIRECTORY_ALARMS
        # is not legal and will go to the default, see test 'path4' below.
        share4 = ss.copy_to_shared('test.ogg',
                                   collection=Environment.DIRECTORY_ALARMS)
        share5 = ss.copy_to_shared('test.mp4')
        # Illegal collection names for .mp4 default to the automatic
        # collection name DIRECTORY_MOVIES
        share6 = ss.copy_to_shared('test.mp4',
                                   collection='Video',
                                   filepath='renamed.mp4')
        share7 = ss.copy_to_shared('test.mp4',
                                   collection=None,
                                   filepath='newname.mp4')

        ################################################################
        # copy from app shared storage    copy_from_shared(shared_file)
        ################################################################

        path0 = ss.copy_from_shared(share0)
        path1 = ss.copy_from_shared(share1)
        path2 = ss.copy_from_shared(join(Environment.DIRECTORY_PICTURES,
                                         app_title, 'c', 'test1.jpg'))
        path3 = ss.copy_from_shared(share3)

        # See note above about .ogg
        # Not certain the change is exactly Androoid 10, but close enough.
        if api_version > 29:
            path4 = ss.copy_from_shared(join(Environment.DIRECTORY_ALARMS,
                                             app_title, 'test.ogg'))
        else:
            path4 = ss.copy_from_shared(join(Environment.DIRECTORY_DOCUMENTS,
                                             app_title, 'test.ogg'))

        path5 = ss.copy_from_shared(share5)
        path6 = ss.copy_from_shared(join(Environment.DIRECTORY_MOVIES,
                                         app_title, 'renamed.mp4'))
        path7 = ss.copy_from_shared(share7)

        ###############################################################
        # Delete from App Shared Storage    delete_shared(shared_file)
        ###############################################################

        # Keep two (share0, share1) to test persistence between app installs
        del2 = ss.delete_shared(share2)
        del3 = ss.delete_shared(share3)
        del4 = ss.delete_shared(share4)
        del5 = ss.delete_shared(join(Environment.DIRECTORY_MOVIES,
                                     app_title, 'test.mp4'))
        del6 = ss.delete_shared(share6)
        del7 = ss.delete_shared(join(Environment.DIRECTORY_MOVIES,
                                     app_title, 'newname.mp4'))

        #############################################################
        # Copy file created by other app to this app then delete copy
        #############################################################

        # on my phones CHART_4.jpg exists
        path8 = ss.copy_from_shared(join(Environment.DIRECTORY_PICTURES,
                                         'CHART_4.jpg'))
        share8 = ss.copy_to_shared(path8)
        del8 = ss.delete_shared(share8)

        #################################
        # Report Results
        #################################
        self.append("copy_to_shared test.txt       "
                    f"{share0 is not None}")
        self.append(f"copy_to_shared a/b/test.txt: {share1 is not None}")
        self.append(f"copy_to_shared c/test.jpg    {share2 is not None}")
        self.append(f"copy_to_shared test.mp3:     {share3 is not None}")
        self.append(f"copy_to_shared test.ogg:     {share4 is not None}")
        self.append(f"copy_to_shared test.mp4:     {share5 is not None}")
        self.append(f"copy_to_shared renamed.mp4:  {share6 is not None}")
        self.append(f"copy_to_shared newname.mp4:  {share7 is not None}")

        self.append("copy_from_shared test.txt     "
                    f"{path0 is not None and exists(path0)}")
        self.append("copy_from_shared a/b/test.txt "
                    f"{path1 is not None and exists(path1)}")
        self.append("copy_from_shared c/test1.jpg  "
                    f"{path2 is not None and exists(path2)}")
        self.append("copy_from_shared test.mp3     "
                    f"{path3 is not None and exists(path3)}")
        self.append("copy_from_shared test.ogg     "
                    f"{path4 is not None and exists(path4)}")
        self.append("copy_from_shared test.mp4     "
                    f"{path5 is not None and exists(path5)}")
        self.append("copy_from_shared renamed.mp4  "
                    f"{path6 is not None and exists(path6)}")
        self.append("copy_from_shared newname.mp4  "
                    f"{path7 != None and exists(path6)}")

        self.append(f"deleted c/test.jpg     {del2}")
        self.append(f"deleted test.mp3       {del3}")
        self.append(f"deleted test.ogg       {del4}")
        self.append(f"deleted test.mp4       {del5}")
        self.append(f"deleted renamed.mp4    {del6}")
        self.append(f"deleted newname.mp4    {del7}")

        self.append("copy_from_shared other app    "
                    f"{path8 is not None and exists(path8)}")
        self.append("copy_to_shared this app       "
                    f"{share8 is not None}")
        self.append("delete copy from other " + str(del8))
        self.display()

    # Chooser interface
    def chooser_start(self, bt):
        self.chooser.choose_content("image/*")

    def chooser_callback(self, uri_list):
        try:
            ss = SharedStorage()
            for uri in uri_list:
                # copy to private
                path = ss.copy_from_shared(uri)
                if path:
                    # then to app shared
                    shared = ss.copy_to_shared(path)
                    self.append("Result copied to app shared "
                                f"{str(exists(path) and shared is not None)}")
            self.display()
        except Exception as e:
            Logger.warning('SharedStorageExample.chooser_callback(): %s', e)

    # Label text
    def append(self, name):
        self.label_lines.append(name)

    @mainthread
    def display(self):
        if self.label:
            self.label.text = ''
            for r in self.label_lines:
                self.label.text += fill(r, 40) + '\n'


SharedStorageExample().run()
