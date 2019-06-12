from tkinter.filedialog import *
from tkinter.scrolledtext import *
from PIL import ImageTk, Image
from program_constants import *

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


# ****************************************GUI Functions*************************************************************
class CheckBar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
        # build 'Checkbutton' objects inside a Frame for GUIMenu - inheritance from 'Frame'
        Frame.__init__(self, parent)
        self.vars = []
        self.config(background=BLACK)

        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var, font=(LUCIDA, 8, BOLD))
            chk.config(background=BLACK, foreground=RED)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append(var)

    def state(self):
        return map((lambda var: var.get()), self.vars)


class GuiMenu(Tk):
    def __init__(self):
        # build object that handles the GUI of the program - inheritance from Tk object
        super().__init__()
        self.title(GUI_TITLE)
        self.resizable(0, 0)
        self.iconbitmap(ICO_PATH)
        self.config(background=BLACK)
        self.profiles_lst = []
        self.collection_opts = []
        # TRY SOMETHING$$$$$$$$$$$$$$$$$$$$$$$$
        self.fb_urls = []
        self.fb_mobile_urls = []
        self.check_on_tineye = False
        self.build_profiles = False
        # self.convert_users = False

        # *******************************Menu*******************************
        menu = Menu(self)
        file_menu = Menu(menu)
        menu.add_cascade(label=FILE_L, menu=file_menu)

        file_menu.add_command(label=OPEN_L, command=self.open_file)
        file_menu.add_command(label=SAVE_L, command=self.save_file)
        file_menu.add_command(label=CLEAR_L, command=self.clear_text)
        file_menu.add_separator()
        file_menu.add_command(label=EXIT_L, command=self.destroy)

        help_menu = Menu(menu)
        menu.add_cascade(label=HELP_L, menu=help_menu)
        help_menu.add_command(label=ABOUT_L, command=self.about)

        special_menu = Menu(menu)
        menu.add_cascade(label="Special Options", menu=special_menu)
        # self.special_menu.add_command(label="Create reports", command=self.set_build_profiles)
        # special_menu.add_checkbutton(label=CONVERT_L, command=self.convert_users)
        special_menu.add_checkbutton(label="Create reports", command=self.set_build_profiles)

        self.config(menu=menu)

        img = ImageTk.PhotoImage(Image.open(IMG_PATH))
        panel = Label(self, image=img, background=BLACK)
        panel.pack()
        # *******************************Labels*******************************
        """
        Label(self, text="Facebook Crawler", background='black', foreground='red',
              font=("Lucida Grande", 30, 'bold')).pack()
        """
        Label(self, text=ENTER_TARGETS, background=BLACK, foreground=WHITE, font=(LUCIDA, 10, BOLD)).pack()
        # *******************************Scrolled Text*******************************
        self.text = ScrolledText(self, background=BLACK, foreground=RED, insertbackground=RED, font=(LUCIDA, 10),
                                 width=60, height=5)
        self.text.pack()
        # *******************************CheckBars*******************************
        self.c_bar1 = CheckBar(self, ALL_CHK_BUTTONS[0])
        self.c_bar2 = CheckBar(self, ALL_CHK_BUTTONS[1])
        self.c_bar3 = CheckBar(self, ALL_CHK_BUTTONS[2])
        self.c_bar4 = CheckBar(self, ALL_CHK_BUTTONS[3])
        self.c_bar5 = CheckBar(self, ALL_CHK_BUTTONS[4])
        self.c_bar6 = CheckBar(self, ALL_CHK_BUTTONS[5])

        self.c_bar1.pack(side=TOP,  fill=X)
        self.c_bar2.pack(side=TOP,  fill=X)
        self.c_bar3.pack(side=TOP,  fill=X)
        self.c_bar4.pack(side=TOP,  fill=X)
        self.c_bar5.pack(side=TOP,  fill=X)

        Label(self, text=Q_NOTE, background=BLACK, foreground=WHITE, font=(LUCIDA, 8, BOLD, UNDER_L)).pack()

        self.c_bar6.pack(side=LEFT)
        # *******************************Buttons*******************************
        Button(self, text=QUIT_BUTTON, background=BLACK, foreground=WHITE, font=(LUCIDA, 12, BOLD),
               command=self.destroy).pack(side=RIGHT)

        Button(self, text=START_BUTTON, background=BLACK, foreground="white", font=(LUCIDA, 12, BOLD),
               command=self.crawl_entered_users).pack(side=RIGHT)

        mainloop()

    def set_target_urls(self):
        # take the chosen options and profiles and create 2 lists with target urls to crawl
        # self.fb_urls -> js version 'https://www.facebook.com...'
        # self.fb_mobile_urls -> disabled js in mobile version 'https://mbasic.facebook.com...'
        if self.profiles_lst and len(self.collection_opts) == 2:
            if self.collection_opts[0][0] == 1:
                for index in range(len(self.profiles_lst)):
                    for opt in range(len(self.collection_opts[1])):
                        if self.collection_opts[1][opt] == 1:
                            url = val_to_q(opt)
                            if url:
                                if "--reverse_image_tineye" in url:
                                    self.check_on_tineye = True
                                elif MOBILE_FACEBOOK not in url:
                                    self.fb_urls.append(url.replace("[fid]", self.profiles_lst[index]))
                                else:
                                    self.fb_mobile_urls.append(url.replace("[fid]", self.profiles_lst[index]))

            if (self.collection_opts[0][1] == 1) and len(self.profiles_lst) >= 2:
                for index in range(len(self.profiles_lst)-1):
                    for index2 in range(index+1, len(self.profiles_lst)):
                        for opt in range(len(self.collection_opts[1])):
                            if self.collection_opts[1][opt] == 1:
                                url = val_to_q_common(opt)
                                if url:
                                    self.fb_urls.append(replace_id(url, self.profiles_lst[index],
                                                                   self.profiles_lst[index2]))

    def crawl_entered_users(self):
        # read the input (of profile uids) from ScrolledText and the values in all 'Checkbutton' objects
        # in order to to run fb_scraper as required by the user
        if self.text:
            profiles = (self.text.get(0.0, END)).split("\n")
            for row in profiles:
                stripped_profile = row.strip()
                ok = (stripped_profile is not "") and (stripped_profile is not " ") and (stripped_profile.isdigit())
                if ok:
                    self.profiles_lst.append(stripped_profile)

            if self.profiles_lst:
                tmp_list1 = list(self.c_bar6.state())

                tmp_list2 = list(self.c_bar1.state()) + list(self.c_bar2.state()) + list(self.c_bar3.state()) \
                            + list(self.c_bar4.state()) + list(self.c_bar5.state())

                if tmp_list1.count(1) > 0 and tmp_list2.count(1) > 0:
                    if not (tmp_list1[0] == 0 and tmp_list1[1] == 1 and len(self.profiles_lst) == 1):
                        self.collection_opts.append(tmp_list1)
                        self.collection_opts.append(tmp_list2)
                        self.set_target_urls()
                        self.destroy()
                    else:
                        del self.profiles_lst[:]

                elif self.build_profiles:
                    self.destroy()

                else:
                    del self.profiles_lst[:]

    def clear_text(self):
        # Clears all written text from ScrolledText
        if self.text:
            self.text.delete(0.0, END)

    def open_file(self):
        # Opens a .txt file and shows it in ScrolledText
        try:

            f = askopenfile(title="Select file", filetypes=TXT_TYPE)
            t = f.read()
            self.text.delete(0.0, END)
            self.text.insert(0.0, t)
        except AttributeError:
            pass

    def save_file(self):
        # Saves the profiles list in a text file
        try:
            f = asksaveasfile(mode='w', filetypes=TXT_TYPE)
            if f is None:
                return
            profiles = (self.text.get(0.0, END)).split("\n")
            for row in range(len(profiles)):
                stripped_profile = profiles[row].strip()
                ok = (stripped_profile is not "") and (stripped_profile is not " ") and (stripped_profile.isdigit())
                if ok:
                    f.write(stripped_profile+"\n")
            f.close()
        except AttributeError:
            pass

    def about(self):
        # Instructions about the program
        if self.text:
            instructions_str = CRAWLER_INSTRUCTIONS
            self.text.delete(0.0, END)
            self.text.insert(0.0, instructions_str)

    def about_convert_users(self):
        # Explains how to convert facebook users to fids
        if self.text:
            instructions_str = USR_TO_ID_INSTRUCTIONS
            self.text.delete(0.0, END)
            self.text.insert(0.0, instructions_str)

    def set_build_profiles(self):
        # label = "Create reports"
        if self.build_profiles:
            self.build_profiles = False
        else:
            self.build_profiles = True
        print(self.build_profiles)


def val_to_q(x):
    # Queries On Specific Profile
    return {
        0: GROUPS_Q, 1: PAGES_LIKED_Q, 2: FRIENDS_Q, 3: FOLLOWERS_Q,
        4: STORIES_LIKED_Q, 5: PHOTOS_LIKED_Q, 6: VIDEOS_LIKED_Q,
        7: STORIES_COMMENTED_Q, 8: PHOTOS_COMMENTED_Q, 9: VIDEOS_COMMENTED_Q,
        10: APPS_USED_Q, 11: SCREENSHOTS_Q, 12: POSTS_Q, 13: ABOUT_Q, 14: EXIST_Q,
        15: PROFILE_PHOTOS_Q, 16: SEARCH_IMAGE_GOOGLE, 17: SEARCH_IMAGE_TINEYE
    }[x]


def val_to_q_common(x):
    # Queries Used To Compare Between Profiles
    return {
        0: COMMON_GROUPS_Q, 1: COMMON_PAGES_LIKED_Q, 2: COMMON_FRIENDS_Q, 3: COMMON_FOLLOWERS_Q,
        4: COMMON_STORIES_LIKED_Q, 5: COMMON_PHOTOS_LIKED_Q, 6: COMMON_VIDEOS_LIKED_Q,
        7: COMMON_STORIES_COMMENTED_Q, 8: COMMON_PHOTOS_COMMENTED_Q, 9: COMMON_VIDEOS_COMMENTED_Q,
        10: COMMON_APPS_USED_Q, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None
        # COMMON_FRIENDS2 = FB_URL+"/friendship/"+FID_QUERY+"/"+FID_QUERY
        # COMMON_FRIENDS3 = FB_SEARCH_URL+FID_QUERY+BASIC_Q[2]+"/"+FID_QUERY+BASIC_Q[2]+INTERSECT
    }[x]


def replace_id(url, uid1, uid2):
    # Inserts the ids to url, instead of '[fid]'
    tmp_query = url.replace("[fid]", uid1, 1)
    return tmp_query.replace("[fid]", uid2, 1)
