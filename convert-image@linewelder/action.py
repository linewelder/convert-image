#!/usr/bin/python3

import sys
import gi
import subprocess
from pathlib import Path


gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk


FORMAT_TO_EXTENSION = {
    'PNG': '.png',
    'JPEG': '.jpg',
    'WebP': '.webp',
    'HEIF': '.heif'
}

EXTENSION_TO_FORMAT = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.png': 'PNG',
    '.webp': 'WebP',
    '.heif': 'HEIF'
}


if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <file1>')
    exit(1)

FILE_PATH = Path(sys.argv[1])
ORIGINAL_FORMAT = EXTENSION_TO_FORMAT[FILE_PATH.suffix]


class ConverterWindow(Gtk.Dialog):
    def __init__(self):
        super().__init__(title='Convert Image')
        self.set_border_width(6)
        self.set_icon_name('emblem-photos')
        self.set_resizable(False)
        self.set_default_size(340, 210)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        form_box.set_border_width(12)
        form_box.add(self.create_format_chooser())
        form_box.add(self.create_quality_scale())
        form_box.add(self.create_replace_check())
        self.vbox.add(form_box)

        self.add_button('Cancel', Gtk.ResponseType.CANCEL)
        self.convert_button = self.add_button('Convert', Gtk.ResponseType.OK)

        self.connect('response', self.on_response)

        # Must be done after setting convert_button
        self.format_combo.set_active(0)
        if self.format_combo.get_active_text() == ORIGINAL_FORMAT:
            self.format_combo.set_active(1)

    def create_format_chooser(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add(Gtk.Label(label='Format:', halign=Gtk.Align.START))

        self.format_combo = Gtk.ComboBoxText()
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
        self.quality_scale.set_tooltip_text('Compression level of the resulting picture')
        box.add(self.quality_scale)

        return box

    def create_replace_check(self):
        self.replace_check = Gtk.CheckButton(label='Replace Original')
        self.replace_check.set_active(True)
        self.replace_check.set_tooltip_text('When enabled, the original file will be deleted')
        return self.replace_check

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.on_convert_clicked(self.convert_button)
        else:
            dialog.destroy()

    def on_format_changed(self, combo):
        chosen_format = combo.get_active_text()
        self.convert_button.set_label('Convert to ' + chosen_format)

    def on_convert_clicked(self, widget):
        target_format = FORMAT_TO_EXTENSION[self.format_combo.get_active_text()]
        output = FILE_PATH.with_suffix(target_format)
        quality = self.quality_scale.get_value()

        if output.is_file():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                title='File Already Exists',
                text=f'Do you want to replace {output.name}?')
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.CANCEL:
                return

        subprocess.run(
            ['convert', '-quality', str(quality), FILE_PATH, str(output)],
            check=True)

        if self.replace_check.get_active() and output != FILE_PATH:
            FILE_PATH.unlink()

        self.destroy()

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

