import json
import os.path
import re
import shutil
import sys
from json import JSONDecodeError

from pydub import AudioSegment

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QListWidget, QLineEdit, QListWidgetItem, QPushButton, \
    QFileDialog, QDialog, QDesktopWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox

wd = os.path.dirname(__file__)

def deactivate_sound(selectedSound, config, tf2_path):
    selectedSoundAbsolutePathDir = f"{tf2_path}/tf/custom/TF2 Hitsound Manager/sound/{os.path.dirname(selectedSound)}"
    selectedSoundAbsolutePath = f"{selectedSoundAbsolutePathDir}/{os.path.basename(selectedSound)}"
    selectedSoundStorePathDir = f"{wd}/data/sound/{os.path.dirname(selectedSound)}"
    base_name = os.path.basename(selectedSound).split('.')

    export_path = None
    if os.path.exists(selectedSoundAbsolutePath):
        selectedSound_name = base_name[0]
        if selectedSound not in config:
            copy_num = 2
            export_path = f"{selectedSound_name}.{base_name[1]}"
            while os.path.exists(f"{selectedSoundStorePathDir}/{export_path}"):
                export_path = f"{selectedSound_name} ({copy_num}).{base_name[1]}"
                copy_num += 1
            os.makedirs(selectedSoundStorePathDir, exist_ok=True)
            shutil.copy(selectedSoundAbsolutePath, f"{selectedSoundStorePathDir}/{export_path}")
        if os.path.exists(selectedSoundAbsolutePath):
            os.remove(selectedSoundAbsolutePath)
    config.pop('key', None)
    write_config(config)
    return export_path

def export_sound (selectedSoundAbsolutePath, selectedSoundStorePath):
    audio = AudioSegment.from_file(selectedSoundStorePath)
    audio = audio.set_frame_rate(44100)
    audio = audio.set_sample_width(2)
    audio.export(selectedSoundAbsolutePath, format=os.path.basename(selectedSoundAbsolutePath).split('.')[1])

def import_sound (selected_file, selected_sound):
    copy_num = 2
    base_name = os.path.basename(selected_file)
    name = base_name.split('.')[0]
    extension = base_name.split('.')[1]
    export_path = base_name
    while export_path in os.listdir(f"{wd}/data/sound/{os.path.dirname(selected_sound)}"):
        export_path = f"{name} ({copy_num}).{extension}"
        copy_num += 1
    shutil.copy(selected_file, f"{wd}/data/sound/{os.path.dirname(selected_sound)}/{export_path}")
    return export_path

def set_all_visible(visible, *widgets):
    for widget in widgets:
        widget.setVisible(visible)


class BackButton (QPushButton):
    def __init__ (self, label, parent, function):
        super(QPushButton, self).__init__(label, parent)
        self.setStyleSheet("background-color : crimson")
        self.move(5, 5)
        self.resize(60, 40)
        self.clicked.connect(function)
        self.setFont(QFont("TF2 Build", 15))


class ChangeAllDialog (QDialog):
    def __init__ (self, config, custom_sounds):
        super().__init__()

        self.config = config
        self.customSounds = custom_sounds
        self.relatedSounds = {}
        self.validRelatedSounds = []

        sizeObject = QDesktopWidget().screenGeometry(-1)
        self.resize(sizeObject.width(), sizeObject.height())
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.backButton = BackButton('<-', self, self.backButtonPressed)

        self.relatedList = QListWidget(self)
        self.relatedList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.relatedList.itemPressed.connect(self.relatedListPressed)
        self.relatedList.setFont(QFont("TF2 Build", 20))
        self.relatedList.move(int(self.width() * 0.25), int(self.height() * 0.15))
        self.relatedList.resize(int(self.width() * 0.5), int(self.height() * 0.5))

        self.rangeStartLabel = QLabel("Range start (inclusive):", self)
        self.rangeStartLabel.setFont(QFont("TF2 Build", 15))
        self.rangeStartLabel.move(int(self.relatedList.x() * 1.2), self.relatedList.y() + self.relatedList.height() + 20)
        self.rangeStartLabel.resize(int(self.relatedList.width() * 0.5), 50)

        self.rangeStartCombo = QComboBox(self)
        self.rangeStartCombo.setFont(QFont("TF2 Build", 15))
        self.rangeStartCombo.move(int(self.rangeStartLabel.x() + self.rangeStartLabel.width() + 10), self.relatedList.y() + self.relatedList.height() + 20)
        self.rangeStartCombo.resize(int(self.relatedList.width() * 0.2 - 10), 50)
        self.rangeStartCombo.setStyleSheet("background-color: darkcyan; color: white;")
        self.rangeStartCombo.currentIndexChanged.connect(self.rangeStartChanged)

        self.rangeEndLabel = QLabel("Range end (inclusive):", self)
        self.rangeEndLabel.setFont(QFont("TF2 Build", 15))
        self.rangeEndLabel.move(self.rangeStartLabel.x(), self.rangeStartLabel.y() + self.rangeStartLabel.height() + 20)
        self.rangeEndLabel.resize(int(self.relatedList.width() / 0.5), 50)

        self.rangeEndCombo = QComboBox(self)
        self.rangeEndCombo.setFont(QFont("TF2 Build", 15))
        self.rangeEndCombo.move(self.rangeStartCombo.x(), self.rangeStartCombo.y() + self.rangeStartCombo.height() + 20)
        self.rangeEndCombo.resize(int(self.relatedList.width() * 0.2 - 10), 50)
        self.rangeEndCombo.setStyleSheet("background-color: darkcyan; color: white;")
        self.rangeEndCombo.currentIndexChanged.connect(self.rangeEndChanged)

        self.changeAllButton = QPushButton("Change all", self)
        self.changeAllButton.setFont(QFont("TF2 Build", 20))
        self.changeAllButton.move(int(self.width() * 0.5 - self.relatedList.width() * 0.25), self.rangeEndLabel.y() + self.rangeEndLabel.height() + 40)
        self.changeAllButton.resize(int(self.relatedList.width() * 0.5), 50)
        self.changeAllButton.setStyleSheet("background-color: darkcyan;")
        self.changeAllButton.clicked.connect(self.changeAllPressed)

        self.resultsTable = QTableWidget(1, 3, self)
        self.resultsTable.move(int(self.width() * 0.1), int(self.height() * 0.1))
        self.resultsTable.resize(int(self.width() * 0.8), int(self.height() * 0.8))
        self.resultsTable.horizontalHeader().setVisible(False)
        self.resultsTable.verticalHeader().setVisible(False)
        self.resultsTable.setFont(QFont("TF2 Build", 15))
        self.resultsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.resultsTable.setVisible(False)

        with open(f"{wd}/data/related_sounds.csv", 'r') as csv:
            next(csv)
            while True:
                try:
                    related_sound = next(csv).split(',')
                except StopIteration:
                    break
                else:
                    self.relatedSounds[related_sound[0]] = (eval(related_sound[1]), int(related_sound[2]))
                    QListWidgetItem(related_sound[0], self.relatedList)

        self.exec_()

    def backButtonPressed (self, event):
        if self.relatedList.isVisible():
            self.close()
        else:
            self.resultsTable.setVisible(False)
            set_all_visible(True, self.relatedList, self.rangeStartLabel, self.rangeStartCombo, self.rangeEndLabel, self.rangeEndCombo)

    def changeAllPressed (self, event):
        selected_item = self.relatedList.selectedItems()
        if not selected_item:
            return
        user_relatedSound = selected_item[0].text()
        if user_relatedSound is None:
            return
        user_relatedSound_split = user_relatedSound.split('.')
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(f"Select {1 + int(self.rangeEndCombo.currentText()) - int(self.rangeStartCombo.currentText())} files")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setDirectory(f"{wd}/data/sound/{user_relatedSound.split('/')[0]}")

        if file_dialog.exec():
            set_all_visible(False, self.relatedList, self.rangeStartLabel, self.rangeStartCombo, self.rangeEndLabel, self.rangeEndCombo)
            self.relatedList.setVisible(False)
            self.resultsTable.clear()
            selected_files = file_dialog.selectedFiles()
            combo_difference = int(self.rangeEndCombo.currentText()) - int(self.rangeStartCombo.currentText())

            self.resultsTable.setRowCount(combo_difference + 2 if len(selected_files) > self.rangeEndCombo.count() else len(selected_files) + 1)
            self.resultsTable.setItem(0, 0, QTableWidgetItem("Custom Sound"))
            self.resultsTable.item(0, 0).setForeground(QColor(255,255,255))
            self.resultsTable.item(0, 0).setBackground(QColor(255,192,203))
            self.resultsTable.item(0, 0).setTextAlignment(Qt.AlignCenter)
            self.resultsTable.setItem(0, 1, QTableWidgetItem("New Sound"))
            self.resultsTable.item(0, 1).setForeground(QColor(255, 255, 255))
            self.resultsTable.item(0, 1).setBackground(QColor(255,192,203))
            self.resultsTable.item(0, 1).setTextAlignment(Qt.AlignCenter)
            self.resultsTable.setItem(0, 2, QTableWidgetItem("Previous Sound"))
            self.resultsTable.item(0, 2).setForeground(QColor(255, 255, 255))
            self.resultsTable.item(0, 2).setBackground(QColor(255,192,203))
            self.resultsTable.item(0, 2).setTextAlignment(Qt.AlignCenter)

            original_count = int(self.rangeStartCombo.currentText())
            count = original_count
            for selected_file in selected_files:

                if count > int(self.rangeEndCombo.currentText()):
                    break

                else:
                    valid_related_sound = self.validRelatedSounds[count - 1]
                    tf2_path = self.config['tf2_path']
                    export_path = f"{tf2_path}/tf/custom/TF2 Hitsound Manager/sound/{valid_related_sound}"
                    if not os.path.exists(export_path):
                        label = "[None]"
                        colour = QColor(128,128,128)
                    else:
                        if valid_related_sound in self.config:
                            label = self.config[valid_related_sound]
                            colour = QColor(255,192,203)
                        else:
                            label = "[Unknown]"
                            colour = QColor(255,255,255)

                    deactivate_sound(valid_related_sound, self.config, tf2_path)

                    row = count - original_count + 1
                    self.resultsTable.setItem(row, 2, QTableWidgetItem(label))
                    item = self.resultsTable.item(row, 2)
                    item.setForeground(colour)
                    item.setBackground(QColor(0, 139, 139))

                    os.makedirs(os.path.dirname(export_path), exist_ok=True)
                    export_sound(export_path, selected_file)

                    self.resultsTable.setItem(row, 0, QTableWidgetItem(valid_related_sound))
                    item = self.resultsTable.item(row, 0)
                    item.setForeground(QColor(255, 255, 255))
                    item.setBackground(QColor(0, 139, 139))

                    self.resultsTable.setItem(row, 1, QTableWidgetItem(os.path.basename(selected_file)))
                    item = self.resultsTable.item(row, 1)
                    item.setForeground(QColor(255,192,203))
                    item.setBackground(QColor(0,139,139))

                    count += 1

            os.makedirs(f"{wd}/data/sound/{os.path.dirname(self.validRelatedSounds[0])}", exist_ok=True)
            count = 0
            if os.path.abspath(os.path.dirname(selected_files[0])) != os.path.abspath(f"{wd}/data/sound/{os.path.dirname(self.validRelatedSounds[0])}"):
                for selected_file in selected_files:
                    if count >= self.rangeEndCombo.count():
                        break
                    export_path = import_sound(selected_file, self.validRelatedSounds[count])
                    self.config[self.validRelatedSounds[count]] = export_path
                    count += 1
            else:
                for selected_file in selected_files:
                    if count >= self.rangeEndCombo.count():
                        break
                    self.config[self.validRelatedSounds[count]] = os.path.basename(selected_file)
                    count += 1
            write_config(self.config)
            self.resultsTable.setVisible(True)

    def rangeEndChanged (self, index):
        if self.rangeStartCombo.count() > 0 and int(self.rangeEndCombo.currentText()) < int(self.rangeStartCombo.currentText()):
            self.rangeStartCombo.setCurrentIndex(0)

    def rangeStartChanged (self, index):
        if self.rangeEndCombo.count() > 0 and int(self.rangeEndCombo.currentText()) < int(self.rangeStartCombo.currentText()):
            self.rangeEndCombo.setCurrentIndex(self.rangeEndCombo.count() - 1)

    def relatedListPressed(self, item):
        self.rangeStartCombo.currentIndexChanged.disconnect(self.rangeStartChanged)
        self.rangeEndCombo.currentIndexChanged.disconnect(self.rangeEndChanged)
        self.rangeStartCombo.clear()
        self.rangeEndCombo.clear()
        self.rangeStartCombo.currentIndexChanged.connect(self.rangeStartChanged)
        self.rangeEndCombo.currentIndexChanged.connect(self.rangeEndChanged)
        self.validRelatedSounds = []
        user_relatedSound = item.text()
        if user_relatedSound is None:
            return
        user_relatedSound_split = user_relatedSound.split('.')
        user_relatedSound_basename = user_relatedSound_split[0]
        user_relatedSound_extension = user_relatedSound_split[1]
        related_sounds_count = 0
        while True:
            comparative_string =  f"{user_relatedSound_basename}{f"{'0' * (self.relatedSounds[user_relatedSound][1] - len(str(related_sounds_count)))}{1 + related_sounds_count}" if related_sounds_count + 1 > 1 or self.relatedSounds[user_relatedSound][0] else ''}.{user_relatedSound_extension}"
            if comparative_string not in self.customSounds:
                break
            self.validRelatedSounds.append(comparative_string)
            self.rangeStartCombo.addItem(str(related_sounds_count + 1))
            self.rangeEndCombo.addItem(str(related_sounds_count + 1))
            related_sounds_count += 1
        self.rangeEndCombo.setCurrentIndex(self.rangeEndCombo.count() - 1)

def write_config (config):
    with open(f"{wd}/data/config.json", 'w') as f:
        json.dump(config, f)

class Widget (QWidget):
    def __init__ (self):
        super().__init__()

        self.selectedSound = None
        self.config = None
        self.userSound = None
        self.tf2_path = None
        self.customSounds = []

        self.text = None

        with open(f'{wd}/data/custom_sounds.txt') as f:
            while True:
                try:
                    self.customSounds.append(next(f).replace('\n', ''))
                except StopIteration:
                    break


        self.setWindowTitle("TF2 Hitsound Manager")
        font1 = QFont("TF2 Build", 20)
        font2 = QFont("TF2 Build", 15)
        
        self.enterTF2Path = QLineEdit(self)
        self.enterTF2Path.setPlaceholderText("Enter TF2 file path....")
        self.enterTF2Path.returnPressed.connect(self.getTF2Path)
        self.enterTF2Path.setFont(font1)

        self.invalidLabel = QLabel("Invalid directory", self)
        self.invalidLabel.setFont(font1)
        self.invalidLabel.setAlignment(Qt.AlignCenter)

        self.changeAllButton = QPushButton("Change all", self)
        self.changeAllButton.clicked.connect(self.changeAllPressed)
        self.changeAllButton.setFont(font2)
        self.changeAllButton.setStyleSheet("background-color: darkcyan;")

        self.searchCustomSounds = QLineEdit(self)
        self.searchCustomSounds.setPlaceholderText("Search custom sounds....")
        self.searchCustomSounds.textChanged.connect(self.textChanged)
        self.searchCustomSounds.setFont(font1)

        self.results = QListWidget(self)
        self.results.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.results.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results.itemPressed.connect(self.resultPressed)
        self.results.setFont(font2)

        self.backButton = BackButton('<-', self, self.backButtonPressed)

        self.activeSoundLabel = QLabel(self)
        self.activeSoundLabel.setFont(font1)
        self.activeSoundLabel.setAlignment(Qt.AlignCenter)

        self.availableSoundsList = QListWidget(self)
        self.availableSoundsList.itemPressed.connect(self.soundPressed)
        self.availableSoundsList.setFont(font2)

        self.changeButton = QPushButton("Change", self)
        self.changeButton.clicked.connect(self.changePressed)
        self.changeButton.setFont(font2)
        self.changeButton.setStyleSheet("background-color: darkcyan;")
        self.importButton = QPushButton("Import", self)
        self.importButton.clicked.connect(self.importPressed)
        self.importButton.setFont(font2)
        self.importButton.setStyleSheet("background-color: darkcyan;")
        self.deactivateButton = QPushButton("Deactivate", self)
        self.deactivateButton.clicked.connect(self.deactivatePressed)
        self.deactivateButton.setFont(font2)
        self.deactivateButton.setStyleSheet("background-color: darkcyan;")

        set_all_visible(False, self.invalidLabel, self.backButton, self.deactivateButton, self.activeSoundLabel, self.availableSoundsList, self.changeButton, self.importButton)

        try:
            f = open(f"{wd}/data/config.json", 'r')
            j = json.load(f)
            tf2_path = j['tf2_path']
        except (IOError, JSONDecodeError, KeyError):

            def search_environ (variable):
                for path in variable:
                    if os.path.exists(path) and os.path.basename(path) == "Team Fortress 2" and "tf" in os.listdir(path):
                        self.enterTF2Path.setVisible(False)
                        self.writeTF2Path(path)
                return self.tf2_path

            if search_environ(os.environ.values()) is None:
                if search_environ(os.environ["PATH"].split(os.pathsep)) is None:
                    set_all_visible(False, self.changeAllButton, self.searchCustomSounds, self.results)
        else:
            self.enterTF2Path.setVisible(False)
            self.config = j
            self.tf2_path = tf2_path
        self.showMaximized()

    def availableSoundsListAdd (self, text):
        if not text is None:
            item = QListWidgetItem(text, self.availableSoundsList)

    def backButtonPressed (self, event):
        set_all_visible(False, self.invalidLabel, self.backButton, self.deactivateButton, self.activeSoundLabel, self.availableSoundsList, self.changeButton, self.importButton)
        self.availableSoundsList.clear()
        self.userSound = None
        self.searchCustomSounds.setText(self.lastText)
        set_all_visible(True, self.changeAllButton, self.searchCustomSounds, self.results)

    def changeAllPressed (self, event):
        dialog = ChangeAllDialog(self.config, self.customSounds)

    def changeEvent (self, event):
        super().changeEvent(event)
        self.resizeWidgets()

    def deactivatePressed (self, event):
        if not self.selectedSound is None:
            base_name = os.path.basename(self.selectedSound).split('.')
            self.availableSoundsListAdd(deactivate_sound(self.selectedSound, self.config, self.tf2_path))
            self.activeSoundLabel.setText(f"<p>Active sound at<br>\"{self.selectedSound}\":<br><br><span style = \"color: grey;\">[None]<p>")

    def resultPressed(self, item):
        selectedSound = item.text()
        self.selectedSound = selectedSound
        set_all_visible(False, self.changeAllButton, self.searchCustomSounds, self.results)
        self.lastText = self.searchCustomSounds.text()
        self.searchCustomSounds.setText('')
        selectedSoundAbsolutePath = f"{self.tf2_path}/tf/custom/TF2 Hitsound Manager/sound/{selectedSound}"
        selectedSoundStorePath = f"{wd}/data/sound/{os.path.dirname(selectedSound)}"
        if os.path.exists(selectedSoundAbsolutePath):
            try:
                sound = f"<span style = \"color: pink; font-size: 15pt;\">{self.config[selectedSound]}"
            except KeyError:
                sound = "<p>[Unknown]"
        else:
            sound = "<span style = \"color: grey;\">[None]"

        if os.path.exists(selectedSoundStorePath):
            for s in os.listdir(selectedSoundStorePath):
                self.availableSoundsListAdd(s)

        self.activeSoundLabel.setText(f"<p>Active sound at<br>\"{selectedSound}\":<br><br>{sound}<p>")
        set_all_visible(True, self.backButton, self.deactivateButton, self.activeSoundLabel, self.availableSoundsList, self.changeButton, self.importButton)

    def getResults(self):
        if self.isVisible():
            self.results.clear()
            self.text, working_text = self.getUserText()
            if not working_text == '':
                self.results.setVisible(True)
                for sound in self.customSounds:
                    if self.text != working_text:
                        return
                    indices = re.search(working_text, sound, re.IGNORECASE)
                    if not indices is None:
                        if (self.results.count() <  1 or self.results.sizeHintForRow(0) * (self.results.count() + 2)) + 25 <=  int((self.height() - self.searchCustomSounds.height()) / 2):
                            item = QListWidgetItem(sound, self.results)
                            self.results.resize(self.searchCustomSounds.width(), self.results.sizeHintForRow(0) * self.results.count() + 25  if self.results.count() > 0 else 0)
                        else:
                            return
                if self.results.count() < 1:
                    self.results.setVisible(False)
            else:
                self.results.setVisible(False)

    def getTF2Path(self):
        tf2_path = self.enterTF2Path.text()
        if not os.path.exists(tf2_path) or not os.path.isdir(tf2_path):
            self.invalidLabel.setVisible(True)
        else:
            set_all_visible(False, self.enterTF2Path, self.invalidLabel)
            self.writeTF2Path(tf2_path)
            set_all_visible(True, self.changeAllButton, self.searchCustomSounds, self.results)

    def getUserText(self):
        text = self.searchCustomSounds.text()
        return text, text

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizeWidgets()

    def resizeWidgets(self):
        if self.isVisible():
            self.enterTF2Path.move(int(self.width() * 0.3 - (self.searchCustomSounds.width() * 0.3)),
                int(self.height() * 0.3 - (self.searchCustomSounds.height() * 0.3)))
            self.enterTF2Path.resize(int(self.width() * 0.7), 50)

            self.invalidLabel.move(self.enterTF2Path.x(), int(self.height() * 0.7 - 50))
            self.invalidLabel.resize(self.enterTF2Path.width(), 50)

            self.changeAllButton.move(int(self.width() * 0.9 - 10), 10)
            self.changeAllButton.resize(int(self.width() * 0.1), 50)

            self.searchCustomSounds.move(int(self.width() * 0.5 - (self.searchCustomSounds.width() * 0.5)),
                            int(self.height() * 0.5 - (self.searchCustomSounds.height() * 0.5)))
            self.searchCustomSounds.resize(int(self.width() * 0.4), 50)
            self.results.move(self.searchCustomSounds.x(), self.searchCustomSounds.y() + self.searchCustomSounds.height())
            self.results.resize(self.searchCustomSounds.width(), self.results.sizeHintForRow(0) * self.results.count() + 25 if self.results.count() > 0 else 0)

            self.activeSoundLabel.move(int(self.width() * 0.05), int(self.height() / 2 - 400))
            self.activeSoundLabel.resize(int(self.width() * 0.4), 800)

            self.availableSoundsList.move(int(self.width() * 0.55), int(self.height() / 4))
            self.availableSoundsList.resize(int(self.width() * 0.4), int(self.height() / 2 - 70))

            self.changeButton.move(self.availableSoundsList.x(), self.availableSoundsList.y() + self.availableSoundsList.height() + 20)
            self.changeButton.resize(int(self.availableSoundsList.width() / 2 - 20), 50)

            self.importButton.move(int(self.availableSoundsList.x() + self.availableSoundsList.width() / 2 + 20), self.availableSoundsList.y() + self.availableSoundsList.height() + 20)
            self.importButton.resize(int(self.availableSoundsList.width() / 2 - 20), 50)

            self.deactivateButton.move(int(self.changeButton.x() + self.changeButton.width() / 2 + 10), self.changeButton.y() + 70)
            self.deactivateButton.resize(int(self.availableSoundsList.width() / 2 - 20), 50)

            self.getResults()

    def soundPressed (self, item):
        self.userSound = item.text()

    def changePressed(self):
        if not self.userSound is None:
            selectedSoundAbsolutePathDir = f"{self.tf2_path}/tf/custom/TF2 Hitsound Manager/sound/{os.path.dirname(self.selectedSound)}"
            selectedSoundAbsolutePath = f"{selectedSoundAbsolutePathDir}/{os.path.basename(self.selectedSound)}"

            selectedSoundStorePathDir = f"{wd}/data/sound/{os.path.dirname(self.selectedSound)}"
            selectedSoundStorePath = f"{selectedSoundStorePathDir}/{os.path.basename(self.userSound)}"

            os.makedirs(selectedSoundAbsolutePathDir, exist_ok=True)

            self.availableSoundsListAdd(deactivate_sound(self.selectedSound, self.config, self.tf2_path))

            export_sound(selectedSoundAbsolutePath, selectedSoundStorePath)

            self.config[self.selectedSound] = self.userSound
            write_config(self.config)

            self.activeSoundLabel.setText(f"<p>Active sound at<br>\"{self.selectedSound}\":<br><br><span style = \"color: pink; font-size: 15pt;\">{self.userSound}<p>")

    def importPressed(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Import custom sounds")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            os.makedirs(f"{wd}/data/sound/{os.path.dirname(self.selectedSound)}", exist_ok=True)
            for selected_file in selected_files:
                export_path = import_sound(selected_file, self.selectedSound)
                self.availableSoundsListAdd(export_path)

    def textChanged (self):
        self.getResults()

    def writeTF2Path (self, tf2_path):
        self.config = {'tf2_path': tf2_path}
        self.tf2_path = tf2_path
        write_config(self.config)

def main ():
   app = QApplication(sys.argv)
   QFontDatabase.addApplicationFont(f"{wd}/assets/fonts/tf2build.ttf")
   app.setStyleSheet(open(f'{wd}/assets/styles/style.qss').read())
   widget = Widget()
   sys.exit(app.exec_())


if __name__ == '__main__':
   main()