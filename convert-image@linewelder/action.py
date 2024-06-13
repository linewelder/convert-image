#!/usr/bin/python3

import sys
import gi
import os
from pathlib import Path


gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk


FORMAT_TO_EXTENSION = {
    'PNG': '.png',
    'JPEG': '.jpg',
    'WEBP': '.webp',
    'HEIF': '.heif'
}

EXTENSION_TO_FORMAT = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.png': 'PNG',
    '.webp': 'WEBP',
    '.heif': 'HEIF'
}


if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <file1>')
    exit(1)

FILE_PATH = Path(sys.argv[1])
ORIGINAL_FORMAT = EXTENSION_TO_FORMAT[FILE_PATH.suffix]


class ConverterWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title='Convert Image')
        self.set_border_width(12)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=32)
        self.add(box)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        form_box.set_border_width(12)
        form_box.add(self.create_format_chooser())
        form_box.add(self.create_quality_scale())
        box.add(form_box)

        box.pack_end(self.create_buttons(), False, False, 0)

        # Must be done after setting convert_button
        self.format_combo.set_active(0)
        if self.format_combo.get_active_text() == ORIGINAL_FORMAT:
            self.format_combo.set_active(1)

    def create_format_chooser(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add(Gtk.Label(label='Format:', halign=Gtk.Align.START))

        self.format_combo = Gtk.ComboBoxText()
        self.format_combo.set_size_request(300, -1)
        self.format_combo.set_entry_text_column(0)

        for file_format in FORMAT_TO_EXTENSION.keys():
            self.format_combo.append_text(file_format)

        self.format_combo.connect('changed', self.on_format_changed)
        box.add(self.format_combo)

        return box

    def create_quality_scale(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add(Gtk.Label(label='Quality:', halign=Gtk.Align.START))

        self.quality_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 100, 1)
        self.quality_scale.set_value(90)
        box.add(self.quality_scale)

        return box

    def create_buttons(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.convert_button = Gtk.Button(label='Convert')
        self.convert_button.connect('clicked', self.on_convert_clicked)
        box.pack_end(self.convert_button, False, False, 0)

        cancel_button = Gtk.Button(label='Cancel')
        cancel_button.connect('clicked', Gtk.main_quit)
        box.pack_end(cancel_button, False, False, 0)

        return box

    def on_format_changed(self, combo):
        chosen_format = combo.get_active_text()
        self.convert_button.set_label('Convert to ' + chosen_format)

    def on_convert_clicked(self, widget):
        target_format = FORMAT_TO_EXTENSION[self.format_combo.get_active_text()]
        output = FILE_PATH.with_suffix(target_format)
        quality = self.quality_scale.get_value()

        os.system(f'convert -quality {quality} {FILE_PATH} {output}')
        # self.destroy()

    def move_to_mouse_pointer(self):
        pointer = Gdk.Display.get_default() \
            .get_default_seat() \
            .get_pointer()
        screen, x, y = pointer.get_position()

        self.set_screen(screen)
        width, height = self.get_size()
        self.move(x - width / 2, y - height / 2)


if __name__ == '__main__': 
    win = ConverterWindow()
    win.connect('destroy', Gtk.main_quit)
    win.show_all()
    win.move_to_mouse_pointer()
    Gtk.main()

