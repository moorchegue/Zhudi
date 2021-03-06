# coding: utf-8
''' Zhudi provides a Chinese - language dictionnary based on the
    C[E|F]DICT project Copyright - 2011 - Ma Jiehong

    Zhudi is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Zhudi is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License
    If not, see <http://www.gnu.org/licenses/>.

'''

from gi.repository import Gtk, Pango, Gdk
import os

import zhudi


cangjie5Object = zhudi.chinese_table.Cangjie5Table()
array30Object = zhudi.chinese_table.Array30Table()
wubi86Object = zhudi.chinese_table.Wubi86Table()


class dictionary_widget_main(object):
    def __init__(self):
        self.hanzi = ""
        self.romanisation = ""
        self.language = ""
        self.results_list = []
        self.lock = False

    def build(self):
        # Search label
        search_label = Gtk.Label()
        search_label.set_text("<big>Searching area</big>")
        search_label.set_use_markup(True)

        # Search field
        search_field = Gtk.Entry()
        search_field.set_visible(True)
        search_field.connect("activate",
                             lambda x: self.search_asked(search_field))
        search_field.set_placeholder_text("Type your query here…")

        # Go, search! button
        go_button = Gtk.Button("Search")
        go_button.connect("clicked",
                          lambda x: self.search_asked(search_field))

        # Options button
        option_button = Gtk.Button("Options")
        option_button.connect("clicked", lambda x: self.open_option())

        # Search + button box
        SB_box = Gtk.Grid()
        SB_box.attach(search_field, 0, 0, 4, 1)
        SB_box.attach_next_to(go_button, search_field, Gtk.PositionType.RIGHT, 1, 1)
        SB_box.attach_next_to(option_button, go_button, Gtk.PositionType.RIGHT, 1, 1)
        SB_box.set_column_homogeneous(True)

        # Search label zone
        frame_search = Gtk.Frame()
        frame_search.set_label_widget(search_label)
        frame_search.add(SB_box)

        # Language box
        language_box = Gtk.Grid()
        Chinese = Gtk.RadioButton.new_with_label_from_widget(None, "From Chinese")
        Chinese.connect("clicked", lambda x: self.set_language("Chinese"))
        language_box.add(Chinese)
        Latin = Gtk.RadioButton.new_with_label_from_widget(Chinese, "To Chinese")
        Latin.connect("clicked", lambda x: self.set_language("Latin"))
        language_box.attach_next_to(Latin, Chinese, Gtk.PositionType.RIGHT, 1, 1)
        language_box.set_column_homogeneous(True)
        Chinese.set_active(True)

        # Results part in a list
        self.results_list = Gtk.ListStore(str)
        results_tree = Gtk.TreeView(self.results_list)
        renderer = Gtk.CellRendererText()
        results_tree.tvcolumn = Gtk.TreeViewColumn("Results", renderer, text=0)
        results_tree.append_column(results_tree.tvcolumn)
        self.results_list.cell = Gtk.CellRendererText()
        results_tree.tvcolumn.pack_start(self.results_list.cell, True)
        results_tree.set_enable_search(False)
        results_tree.tvcolumn.set_sort_column_id(False)
        results_tree.set_reorderable(False)
        select = results_tree.get_selection()
        select.connect("changed", self.display_another_result)

        results_scroll = Gtk.ScrolledWindow()
        # No horizontal bar, automatic vertical bar
        results_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        results_scroll.add_with_viewport(results_tree)

        frame_results = Gtk.Frame()
        frame_results.add(results_scroll)

        # Translation Label
        translation_label = Gtk.Label()
        translation_label.set_text("<big>Translation</big>")
        translation_label.set_use_markup(True)

        # Translation view
        self.translation_box = Gtk.TextView(buffer=None)
        self.translation_box.set_editable(False)
        self.translation_box.set_cursor_visible(False)

        # No horizontal bar, vertical bar if needed
        self.translation_box.set_wrap_mode(Gtk.WrapMode.WORD)
        tr = self.translation_box.get_buffer()
        bold = tr.create_tag(weight=Pango.Weight.BOLD)
        big = tr.create_tag(size=30*Pango.SCALE)
        medium = tr.create_tag(size=15*Pango.SCALE)
        blue = tr.create_tag(foreground="blue")

        translation_scroll = Gtk.ScrolledWindow()
        translation_scroll.add_with_viewport(self.translation_box)

        frame_translation = Gtk.Frame()
        frame_translation.set_label_widget(translation_label)
        frame_translation.add(translation_scroll)

        # Mapping of the main window
        left_vertical_box = Gtk.Grid()
        left_vertical_box.add(frame_search)
        left_vertical_box.attach_next_to(language_box,
                                         frame_search,
                                         Gtk.PositionType.BOTTOM, 1, 1)
        left_vertical_box.attach_next_to(frame_results,
                                         language_box,
                                         Gtk.PositionType.BOTTOM, 1, 7)
        left_vertical_box.set_row_homogeneous(True)
        left_vertical_box.set_column_homogeneous(True)

        right_vertical_box = Gtk.Grid()
        right_vertical_box.add(frame_translation)
        right_vertical_box.set_column_homogeneous(True)
        right_vertical_box.set_row_homogeneous(True)

        horizontal_box = Gtk.Grid()
        horizontal_box.attach(left_vertical_box, 0, 0, 1, 1)
        horizontal_box.attach_next_to(right_vertical_box,
                                      left_vertical_box,
                                      Gtk.PositionType.RIGHT, 1, 1)
        horizontal_box.set_column_homogeneous(True)
        horizontal_box.set_row_homogeneous(True)
        return horizontal_box

    def search_asked(self, searchfield):
        text = searchfield.get_text()
        if text == "":
            self.lock = True
            dictionaryToolsObject.index = []
            self.results_list.clear()
            self.display_translation(0)
        else:
            self.lock = False
            if self.language == "Latin":
                given_list = dataObject.translation
            elif self.hanzi == "Traditional":
                given_list = dataObject.traditional
            else:
                given_list = dataObject.simplified
            dictionaryToolsObject.search(given_list, text)
            self.update_results()
            self.display_translation(0)
    # end of search_asked

    def set_language(self, string):
        self.language = string

    def display_translation(self, which):
        tr = self.translation_box.get_buffer()
        if len(dictionaryToolsObject.index) == 0:
            tr.set_text("Nothing found.")
            if len(self.results_list) == 0:
                self.results_list.append(["Nothing found."])
            return
        else:
            index = dictionaryToolsObject.index[which]

        if self.hanzi == "Traditional":
            hanzi_dic = dataObject.traditional
        else:
            hanzi_dic = dataObject.simplified
        if self.romanisation == "Zhuyin":
            romanisation_dic = dataObject.zhuyin
        else:
            romanisation_dic = dataObject.pinyin

        slash_list = []
        t = dataObject.translation[index]
        for l in range(len(t)):
            if t[l] == "/":
                slash_list.append(l)
        temp = 0
        trans = []
        for k in range(len(slash_list)):
            trans.append(str(k+1)+". "+t[temp:slash_list[k]])
            temp = slash_list[k]+1
        trans.append(str(len(slash_list)+1)+". "+t[temp:len(t)])
        string = ""
        for i in range(len(slash_list)+1):
            string = string + trans[i]+"\n"

        # Add [] arround the pronounciation parts
        p_string = romanisation_dic[index].split()
        pronounciation_string = []
        for point in range(len(p_string)):
            if self.romanisation == "Pinyin":
                pronounciation_string.append(dictionaryToolsObject.unicode_pinyin(p_string[point]))
                pronounciation_string.append(" ")
            else:
                pronounciation_string.append("[")
                pronounciation_string.append(p_string[point])
                pronounciation_string.append("]")
        # Display the cangjie of the entry
        cangjie5_displayed = ""
        for hanzi in hanzi_dic[index]:
            if hanzi != "\n":
                key_code, displayed_code = cangjie5Object.proceed(hanzi, dataObject.cangjie5)
                cangjie5_displayed += "["
                cangjie5_displayed += displayed_code
                cangjie5_displayed += "]"
        # Display the array30 of the entry
        array30_displayed = ""
        for hanzi in hanzi_dic[index]:
            if hanzi != "\n":
                key_code, displayed_code = array30Object.proceed(hanzi, dataObject.array30)
                array30_displayed += "["
                array30_displayed += displayed_code
                array30_displayed += "]"
        # Display the array30 of the entry (here code = displayed)
        wubi86_code = ""
        for hanzi in hanzi_dic[index]:
            if hanzi != "\n":
                key_code, displayed_code = wubi86Object.proceed(hanzi, dataObject.wubi86)
                wubi86_code += "["
                wubi86_code += key_code
                wubi86_code += "]"
        # Display in the Translation box
        tr.set_text("Chinese\n" + hanzi_dic[index] + "\n\n" +
                    "Pronunciation\n" + ''.join(pronounciation_string) + "\n\n" +
                    "Meaning\n" + string +
                    "Input methods codes:\n" +
                    "Array30 (行列30): \n" + array30_displayed + "\n\n" +
                    "Cangjie5 (倉頡5): \n" + cangjie5_displayed + "\n\n" +
                    "Wubi86 (五筆86): \n" + wubi86_code)
        bold = tr.create_tag(weight=Pango.Weight.BOLD)
        big = tr.create_tag(size=30 * Pango.SCALE)
        medium = tr.create_tag(size=15 * Pango.SCALE)
        blue = tr.create_tag(foreground="blue")

        # "Chinese" in bold
        start_1 = tr.get_iter_at_line(0)
        end_1 = tr.get_iter_at_line(0)
        end_1.forward_to_line_end()
        tr.apply_tag(bold, start_1, end_1)

        # Bigger Chinese
        start_c = tr.get_iter_at_line(1)
        end_c = tr.get_iter_at_line(1)
        end_c.forward_to_line_end()
        tr.apply_tag(big, start_c, end_c)

        # "Pronunciation" in bold
        start_2 = tr.get_iter_at_line(4)
        end_2 = tr.get_iter_at_line(4)
        end_2.forward_to_line_end()
        tr.apply_tag(bold, start_2, end_2)

        # "Pronunciation" in blue
        start_3 = tr.get_iter_at_line(5)
        end_3 = tr.get_iter_at_line(5)
        end_3.forward_to_line_end()
        tr.apply_tag(blue, start_3, end_3)
        tr.apply_tag(medium,start_3, end_3)

        # "Meaning" in bold
        start_3 = tr.get_iter_at_line(7)
        end_3 = tr.get_iter_at_line(7)
        end_3.forward_to_line_end()
        tr.apply_tag(bold, start_3, end_3)
        guess = string.count("\n")

        # "Input methods codes" in bold
        start_4 = tr.get_iter_at_line(guess+7)
        end_4 = tr.get_iter_at_line(guess+7)
        end_4.forward_to_line_end()
        tr.apply_tag(bold, start_4, end_4)

    def update_results(self):
        self.results_list.clear()
        displayed_index = 1
        t = 40  # threshold for line wrap
        for k in dictionaryToolsObject.index:
            if self.language == "Latin":
                string = dataObject.translation[k]
            elif self.hanzi == "Traditional":
                string = dataObject.traditional[k]
            else:
                string = dataObject.simplified[k]
            if len(string) > t:
                string = str(displayed_index) + ". " + string[0:t] + "…"
            else:
                string = str(displayed_index) + ". " + string
            string = string[:-1]  # no \n
            self.results_list.append([string])
            displayed_index += 1

    def display_another_result(self, selection):
        if not self.lock:
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                row = model[treeiter][0]
                t = 0
                if row is not None:
                    while row[t] != ".":
                        t += 1
                    figure = int(row[0:t])
                    if figure > len(dictionaryToolsObject.index):
                        self.display_translation(0)
                    else:
                        self.display_translation(figure-1)

    def set_config(self, romanisation, hanzi):
        """
        This function saves values to the config file. The config file is
        overwritten if it already exists.
        """
        with open(os.environ["HOME"] + "/.zhudi/config", "w") as config_file:
            config_file.write("# This file is the configuration file" +
                              " used by Zhudi in order to remember\n")
            config_file.write("# user's configuration choices.\n")
            config_file.write("# This file has been created automatically" +
                              "by Zhudi.\n\n")
            config_file.write("romanisation:\n")
            config_file.write(romanisation+"\n\n")
            config_file.write("hanzi form:\n")
            config_file.write(hanzi+"\n\n")

    def open_option(self):
        opt = self.dictionary_widget_option(self)
        opt.hanzi = self.hanzi
        opt.romanisation = self.romanisation
        opt.build()

    class dictionary_widget_option(object):
        def kill_ok(self):
            self.window.hide()

        def __init__(self, main_window):
            self.hanzi = ""
            self.romanisation = ""
            self.mw = main_window
            # Definition of the options window
            self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
            self.window.set_size_request(300, 180)
            self.window.set_title("Options")
            self.window.set_position(Gtk.WindowPosition.CENTER)
            self.window.connect("destroy", lambda x: self.window.destroy)

        def build(self):
            # Hanzi label
            hanzi_label = Gtk.Label()
            hanzi_label.set_text("<big>Chinese characters form:</big>")
            hanzi_label.set_justify(Gtk.Justification.LEFT)
            hanzi_label.set_use_markup(True)
            # hanzi box
            hanzi_box = Gtk.Grid()
            Traditional = Gtk.RadioButton.new_with_label_from_widget(None, "Traditional")
            Traditional.connect("clicked", lambda x: self.set_hanzi("Traditional"))
            hanzi_box.add(Traditional)
            Simplified = Gtk.RadioButton.new_with_label_from_widget(Traditional, "Simplified")
            Simplified.connect("clicked", lambda x: self.set_hanzi("Simplified"))
            hanzi_box.attach_next_to(Simplified, Traditional, Gtk.PositionType.RIGHT, 1, 1)
            hanzi_box.set_column_homogeneous(True)

            # Romanisation label
            romanisation_label = Gtk.Label()
            romanisation_label.set_text("<big>Pronunciation system:</big>")
            romanisation_label.set_justify(Gtk.Justification.LEFT)
            romanisation_label.set_use_markup(True)

            # romanisation box
            romanisation_box = Gtk.Grid()
            Zhu = Gtk.RadioButton.new_with_label_from_widget(None, "Zhuyin Fuhao")
            Zhu.connect("clicked", lambda x: self.set_romanisation("Zhuyin"))
            romanisation_box.add(Zhu)
            Pin = Gtk.RadioButton.new_with_label_from_widget(Zhu, "Hanyu Pinyin")
            Pin.connect("clicked", lambda x: self.set_romanisation("Pinyin"))
            romanisation_box.attach_next_to(Pin, Zhu, Gtk.PositionType.RIGHT, 1, 1)
            romanisation_box.set_column_homogeneous(True)
            # Horizontal separator
            option_horizontal_separator = Gtk.Separator()
            # Ok button
            ok_button = Gtk.Button("Ok")
            ok_button.connect("clicked", lambda x:self.kill_ok())
            # Mapping of the option window
            loption_vertical_box = Gtk.Grid()
            loption_vertical_box.add(hanzi_label)
            loption_vertical_box.attach_next_to(hanzi_box, hanzi_label, Gtk.PositionType.BOTTOM, 1, 1)
            loption_vertical_box.attach_next_to(romanisation_label, hanzi_box, Gtk.PositionType.BOTTOM, 1, 1)
            loption_vertical_box.attach_next_to(romanisation_box, romanisation_label, Gtk.PositionType.BOTTOM, 1, 1)
            loption_vertical_box.attach_next_to(option_horizontal_separator, romanisation_box, Gtk.PositionType.BOTTOM, 1, 1)
            loption_vertical_box.attach_next_to(ok_button, option_horizontal_separator, Gtk.PositionType.BOTTOM, 1, 2)
            loption_vertical_box.set_column_homogeneous(True)
            loption_vertical_box.set_row_homogeneous(True)

            # Adding them in the main window
            self.window.add(loption_vertical_box)

            # Eventually, show the option window and the widgetss
            self.window.show_all()

            if self.hanzi == "Traditional":
                Traditional.set_active(True)
            else:
                Simplified.set_active(True)
            if self.romanisation == "Zhuyin":
                Zhu.set_active(True)
            else:
                Pin.set_active(True)

        def set_romanisation(self, string):
            self.mw.romanisation = string
            self.mw.set_config(self.mw.romanisation, self.mw.hanzi)

        def set_hanzi(self, string):
            self.mw.hanzi = string
            self.mw.set_config(self.mw.romanisation, self.mw.hanzi)
    # End of Option_window


class segmentation_widget(object):
    """ Class that defines the segmentation GUI layer.
    """

    def __init__(self, hanziForm, romanisationForm):
        self.hanzi = hanziForm
        self.romanisation = romanisationForm

    def build(self):
        # Frame label
        self.frame_label = Gtk.Label()
        self.frame_label.set_text("<big>Chinese text to process:</big>")
        self.frame_label.set_use_markup(True)

        # Horzontal separator
        self.horizontal_separator = Gtk.Separator()

        # Go! button
        self.go_button = Gtk.Button("Go!")
        self.go_button.connect("clicked",
                               lambda x: self.go(self.text_field.get_buffer()))
        # Frame title + Go! button
        self.title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.title_box.pack_start(self.frame_label, False, False, 0)
        self.title_box.pack_start(self.horizontal_separator, True, False, 0)
        self.title_box.pack_start(self.go_button, True, True, 0)

        # Text field (to process)
        self.text_field = Gtk.TextView()
        self.text_field.set_editable(True)
        self.text_field.set_cursor_visible(True)
        self.text_field.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.add(self.text_field)

        # Results part in a list
        self.results_list = Gtk.ListStore(str)
        results_tree = Gtk.TreeView(self.results_list)
        renderer = Gtk.CellRendererText()
        results_tree.tvcolumn = Gtk.TreeViewColumn("Results", renderer, text=0)
        results_tree.append_column(results_tree.tvcolumn)
        self.results_list.cell = Gtk.CellRendererText()
        results_tree.tvcolumn.pack_start(self.results_list.cell, True)
        results_tree.set_enable_search(False)
        results_tree.tvcolumn.set_sort_column_id(False)
        results_tree.set_reorderable(False)
        select = results_tree.get_selection()
        select.connect("changed", self.wordSelected)

        results_scroll = Gtk.ScrolledWindow()
        # No horizontal bar, automatic vertical bar
        results_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        results_scroll.add_with_viewport(results_tree)

        self.frame_results = Gtk.Frame()
        self.frame_results.add(results_scroll)

        # Mapping of window
        self.left_vertical_box = Gtk.Grid()
        self.left_vertical_box.add(self.title_box)
        self.left_vertical_box.attach_next_to(self.scrolledwindow,
                                              self.title_box,
                                              Gtk.PositionType.BOTTOM, 1, 2)
        self.left_vertical_box.attach_next_to(self.frame_results,
                                              self.scrolledwindow,
                                              Gtk.PositionType.BOTTOM, 1, 8)
        self.left_vertical_box.set_column_homogeneous(True)
        self.left_vertical_box.set_row_homogeneous(True)

        # Results frame
        self.results_label = Gtk.Label()
        self.results_label.set_text("<big>Translation</big>")
        self.results_label.set_use_markup(True)
        self.results_field = Gtk.TextView(buffer=None)
        self.results_field.set_editable(False)
        self.results_field.set_cursor_visible(False)
        # No horizontal bar, vertical bar if needed
        self.results_field.set_wrap_mode(Gtk.WrapMode.WORD)

        self.results_scroll = Gtk.ScrolledWindow()
        self.results_scroll.add_with_viewport(self.results_field)

        self.results_frame = Gtk.Frame()
        self.results_frame.set_label_widget(self.results_label)
        self.results_frame.add(self.results_scroll)

        self.right_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.right_vertical_box.pack_start(self.results_frame, True, True, 0)

        self.horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.horizontal_box.pack_start(self.left_vertical_box, False, True, 0)
        self.horizontal_box.pack_start(self.right_vertical_box, False, True, 0)
        self.horizontal_box.set_homogeneous(True)
        return self.horizontal_box

    def go(self, text_buffer):
        beginning = text_buffer.get_start_iter()
        end = text_buffer.get_end_iter()
        # grab hidden characters
        text = text_buffer.get_text(beginning, end, True)
        text = text.replace(" ", "")
        segmented_text = segmentationToolsObject.sentence_segmentation(text)
        self.display_results(segmented_text, text_buffer)
        self.displaySelectableWords(segmented_text)

    def displaySelectableWords(self, segmented_text):
        widget = self.results_list
        widget.clear()
        for word in segmented_text:
            widget.append([word])

    def display_results(self, text, results_buffer):
        """ Display the segmentation result directly in the input area.
        This has a nice side effect: allowing you to copy the result.

        """
        text_to_display = ""
        for item in text:
            text_to_display += item
            text_to_display += "    "
        results_buffer.set_text(text_to_display)

    def display_translation(self, index, byPass=False):
        """ Display the given index [of a word] in a nicely formatted output.
        If byPass is True, then the index variable is a string that has to
        be displayed as it.

        """
        tr = self.results_field.get_buffer()

        if byPass:
            tr.set_text(index)
            return

        if self.hanzi == "Traditional":
            hanzi_dic = dataObject.traditional
        else:
            hanzi_dic = dataObject.simplified

        if self.romanisation == "Zhuyin":
            romanisation_dic = dataObject.zhuyin
        else:
            romanisation_dic = dataObject.pinyin

        slash_list = []
        t = dataObject.translation[index]
        for l in range(len(t)):
            if t[l] == "/":
                slash_list.append(l)
        temp = 0
        trans = []
        for k in range(len(slash_list)):
            trans.append(str(k+1)+". "+t[temp:slash_list[k]])
            temp = slash_list[k]+1
        trans.append(str(len(slash_list)+1)+". "+t[temp:len(t)])
        string = ""
        for i in range(len(slash_list)+1):
            string = string + trans[i]+"\n"

        # Add [] arround the pronounciation parts
        p_string = romanisation_dic[index].split()
        pronounciation_string = []
        for point in range(len(p_string)):
            if self.romanisation == "Pinyin":
                pronounciation_string.append(dictionaryToolsObject.unicode_pinyin(p_string[point]))
                pronounciation_string.append(" ")
            else:
                pronounciation_string.append("[")
                pronounciation_string.append(p_string[point])
                pronounciation_string.append("]")
        # Display the cangjie of the entry
        cangjie5_displayed = ""
        for hanzi in hanzi_dic[index]:
            if hanzi != "\n":
                key_code, displayed_code = cangjie5Object.proceed(hanzi, dataObject.cangjie5)
                cangjie5_displayed += "["
                cangjie5_displayed += displayed_code
                cangjie5_displayed += "]"
        # Display the array30 of the entry
        array30_displayed = ""
        for hanzi in hanzi_dic[index]:
            if hanzi != "\n":
                key_code, displayed_code = array30Object.proceed(hanzi, dataObject.array30)
                array30_displayed += "["
                array30_displayed += displayed_code
                array30_displayed += "]"
        # Display the array30 of the entry (here code = displayed)
        wubi86_code = ""
        for hanzi in hanzi_dic[index]:
            if hanzi != "\n":
                key_code, displayed_code = wubi86Object.proceed(hanzi, dataObject.wubi86)
                wubi86_code += "["
                wubi86_code += key_code
                wubi86_code += "]"
        # Display in the Translation box
        tr.set_text("Chinese\n" + hanzi_dic[index] + "\n\n" +
                    "Pronunciation\n" + ''.join(pronounciation_string) + "\n\n"
                    "Meaning\n" + string +
                    "Input methods codes:\n" +
                    "Array30 (行列30): \n" + array30_displayed + "\n\n" +
                    "Cangjie5 (倉頡5): \n" + cangjie5_displayed + "\n\n" +
                    "Wubi86 (五筆86): \n" + wubi86_code)
        bold = tr.create_tag(weight=Pango.Weight.BOLD)
        big = tr.create_tag(size=30*Pango.SCALE)
        medium = tr.create_tag(size=15*Pango.SCALE)
        blue = tr.create_tag(foreground="blue")

        # "Chinese" in bold
        start_1 = tr.get_iter_at_line(0)
        end_1 = tr.get_iter_at_line(0)
        end_1.forward_to_line_end()
        tr.apply_tag(bold, start_1, end_1)

        # Bigger Chinese
        start_c = tr.get_iter_at_line(1)
        end_c = tr.get_iter_at_line(1)
        end_c.forward_to_line_end()
        tr.apply_tag(big, start_c, end_c)

        # "Pronunciation" in bold
        start_2 = tr.get_iter_at_line(4)
        end_2 = tr.get_iter_at_line(4)
        end_2.forward_to_line_end()
        tr.apply_tag(bold, start_2, end_2)

        # "Pronunciation" in blue
        start_3 = tr.get_iter_at_line(5)
        end_3 = tr.get_iter_at_line(5)
        end_3.forward_to_line_end()
        tr.apply_tag(blue, start_3, end_3)
        tr.apply_tag(medium, start_3, end_3)

        # "Meaning" in bold
        start_3 = tr.get_iter_at_line(7)
        end_3 = tr.get_iter_at_line(7)
        end_3.forward_to_line_end()
        tr.apply_tag(bold, start_3, end_3)
        guess = string.count("\n")

        # "Input methods codes" in bold
        start_4 = tr.get_iter_at_line(guess+7)
        end_4 = tr.get_iter_at_line(guess+7)
        end_4.forward_to_line_end()
        tr.apply_tag(bold, start_4, end_4)

    def wordSelected(self, selection):
        """ Display the selected word in the translation area.

        """
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            word = model[treeiter][0]
            if word is not None:
                index = segmentationToolsObject.searchUnique(word, dataObject)
                if index is None:
                    self.display_translation(word, True)
                else:
                    self.display_translation(index)


class main_window(object):
    """ Class that defines the welcome screen, and gives access to other layers.
    """

    def __init__(self, dataObject):
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_default_size(800, 494)  # Gold number ratio
        self.window.set_title("Zhudi")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("key-release-event", self.on_key_release)
        self.dataObject = dataObject
        self.hanzi = ""
        self.romanisation = ""
        self.language = ""

    def loop(self):
        Gtk.main()

    def build(self):
        global dataObject
        dataObject = self.dataObject
        global dictionaryToolsObject
        dictionaryToolsObject = zhudi.processing.DictionaryTools()
        global segmentationToolsObject
        segmentationToolsObject = zhudi.processing.SegmentationTools()
        segmentationToolsObject.load(dataObject)
        # Welcome tab
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.default_mode()
        self.vbox.pack_start(self.default_text, False, False, 0)

        # Dictionary tab
        self.dict_gui = self.dictionary_gui()

        # Segmentation tab
        self.seg_gui = self.segmentation_gui()

        # Build the tab frame
        self.tab_box = Gtk.Notebook()
        self.tab_box.set_tab_pos(Gtk.PositionType.TOP)
        self.tab_box.append_page(self.vbox, None)
        self.tab_box.set_tab_label_text(self.vbox, "Welcome")
        self.tab_box.append_page(self.dict_gui, None)
        self.tab_box.set_tab_label_text(self.dict_gui, "Dictionary")
        self.tab_box.append_page(self.seg_gui, None)
        self.tab_box.set_tab_label_text(self.seg_gui, "Segmentation")

        self.window.add(self.tab_box)
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

    def default_mode(self):
        """ This is the default mode, i.e. when no mode is selected."""
        self.default_text = Gtk.Frame(label_yalign=0.5, label_xalign=0.5)
        self.default_text.set_label("\n\n\n\n"
                                    "              Zhudi"
                                    "\n\n"
                                    "       Jiehong Ma, 2011–2013"
                                    "\n\n"
                                    "Zhudi has been designed in order to help\n"
                                    "people learning Chinese thanks to free tools.\n"
                                    "It aims at providing reliable, and useful\n"
                                    "informations to the Chinese learner.\n"
                                    "The author is also a Chinese learner as well,\n"
                                    "and he uses Zhudi almost everyday.\n"
                                    "\n"
                                    "This software is under the GNU GPLv3 licence.")

    def dictionary_gui(self):
        """ Start the dictionary widget. """
        self.main_widget = dictionary_widget_main()
        self.main_widget.hanzi = self.hanzi
        self.main_widget.romanisation = self.romanisation
        self.main_widget.language = self.language
        self.sub_gui = self.main_widget.build()
        return self.sub_gui

    def segmentation_gui(self):
        """ Start the segmentation widget. """
        self.main_widget = segmentation_widget(self.hanzi, self.romanisation)
        self.sub_gui = self.main_widget.build()
        return self.sub_gui

    def on_key_release(self, widget, event, data=None):
        if event.keyval == Gdk.KEY_w and event.state & Gdk.ModifierType.CONTROL_MASK:
            Gtk.main_quit()
