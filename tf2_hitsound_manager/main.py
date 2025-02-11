import json
import os.path
import re
import shutil
import sys
from json import JSONDecodeError

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QListWidget, QLineEdit, QListWidgetItem, QPushButton, \
    QFileDialog

wd = os.path.dirname(__file__)

class FilePathListItem (QLabel):
    def __init__ (self, label, working_text, start, end):
        super(QLabel, self).__init__(f"<p style=\"border: none; color: white; font-family: TF2 Build, TF2 Build; font-size: 33px;\">{label[:start]}<span style = \"background-color: gold\">{working_text}</span>{label[end:]}</p>")
        self.file_path = label

    def getFilePath (self):
        return self.file_path


class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.selectedSound = None
        self.userSoundLast = None
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

        self.searchCustomSounds = QLineEdit(self)
        self.searchCustomSounds.setPlaceholderText("Search custom sounds....")
        self.searchCustomSounds.textChanged.connect(self.textChanged)
        self.searchCustomSounds.setFont(font1)

        self.results = QListWidget(self)
        self.results.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results.itemPressed.connect(self.resultPressed)
        self.results.setFont(font2)

        self.backButton = QPushButton("<-", self)
        self.backButton.setStyleSheet("background-color : crimson")
        self.backButton.move(5, 5)
        self.backButton.resize(60, 40)
        self.backButton.clicked.connect(self.backButtonPressed)
        self.backButton.setFont(font2)

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

        self.setAllVisible(False, self.invalidLabel, self.backButton, self.activeSoundLabel, self.availableSoundsList, self.changeButton, self.importButton)

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
                    self.setAllVisible(False, self.searchCustomSounds, self.results)
        else:
            self.enterTF2Path.setVisible(False)
            self.config = j
            self.tf2_path = tf2_path
        self.showMaximized()

    def availableSoundsListAdd(self, text):
        label = FilePathListItem(text, '', 0, 0)
        item = QListWidgetItem(self.availableSoundsList)
        self.availableSoundsList.setItemWidget(item, label)

    def backButtonPressed(self, event):
        self.setAllVisible(False, self.invalidLabel, self.backButton, self.activeSoundLabel, self.availableSoundsList, self.changeButton, self.importButton)
        self.availableSoundsList.clear()
        self.userSound = None
        self.userSoundLast = None
        self.searchCustomSounds.setText(self.lastText)
        self.setAllVisible(True, self.searchCustomSounds, self.results)

    def changeEvent(self, event):
        super().changeEvent(event)
        self.resizeWidgets()
        self.getResults()

    def resultPressed(self, item):
        selectedSound = self.results.itemWidget(item).getFilePath()
        self.selectedSound = selectedSound
        self.setAllVisible(False, self.searchCustomSounds, self.results)
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
        self.setAllVisible(True, self.backButton, self.activeSoundLabel, self.availableSoundsList, self.changeButton, self.importButton)

    def getResults(self):
        if self.isVisible():
            self.resultsLast = []
            self.results.clear()
            self.text, working_text = self.getUserText()
            if not working_text == '':
                self.results.setVisible(True)
                for sound in self.customSounds:
                    if self.text != working_text:
                        return
                    indices = re.search(working_text, sound, re.IGNORECASE)
                    if not indices is None:
                        label = FilePathListItem(sound, working_text, indices.start(), indices.end())
                        label.resize(label.width(), 30)
                        if (35 * (self.results.count() + 1)) <=  int((self.height() - self.searchCustomSounds.height()) / 2):
                            item = QListWidgetItem()
                            self.resultsLast.append(item)
                            self.results.addItem(item)
                            self.results.setItemWidget(item, label)
                            self.results.resize(self.searchCustomSounds.width(), 35 * self.results.count())
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
            self.setAllVisible(False, self.enterTF2Path, self.invalidLabel)
            self.writeTF2Path(tf2_path)
            self.setAllVisible(True, self.searchCustomSounds, self.results)

    def getUserText(self):
        text = self.searchCustomSounds.text()
        return text, text

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizeWidgets()
        self.getResults()

    def resizeWidgets(self):
        if self.isVisible():
            self.enterTF2Path.move(int(self.width() * 0.3 - (self.searchCustomSounds.width() * 0.3)),
                int(self.height() * 0.3 - (self.searchCustomSounds.height() * 0.3)))
            self.enterTF2Path.resize(int(self.width() * 0.7), 50)

            self.invalidLabel.move(self.enterTF2Path.x(), int(self.height() * 0.7 - 50))
            self.invalidLabel.resize(self.enterTF2Path.width(), 50)

            self.searchCustomSounds.move(int(self.width() * 0.5 - (self.searchCustomSounds.width() * 0.5)),
                            int(self.height() * 0.5 - (self.searchCustomSounds.height() * 0.5)))
            self.searchCustomSounds.resize(int(self.width() * 0.4), 50)
            self.results.move(self.searchCustomSounds.x(), self.searchCustomSounds.y() + self.searchCustomSounds.height())
            self.results.resize(self.searchCustomSounds.width(), 35 * self.results.count())

            self.activeSoundLabel.move(int(self.width() * 0.05), int(self.height() / 2 - 400))
            self.activeSoundLabel.resize(int(self.width() * 0.4), 800)

            self.availableSoundsList.move(int(self.width() * 0.55), int(self.height() / 4))
            self.availableSoundsList.resize(int(self.width() * 0.4), int(self.height() / 2 - 70))

            self.changeButton.move(self.availableSoundsList.x(), self.availableSoundsList.y() + self.availableSoundsList.height() + 20)
            self.changeButton.resize(int(self.availableSoundsList.width() / 2 - 20), 50)

            self.importButton.move(int(self.availableSoundsList.x() + self.availableSoundsList.width() / 2 + 20), self.availableSoundsList.y() + self.availableSoundsList.height() + 20)
            self.importButton.resize(int(self.availableSoundsList.width() / 2 - 20), 50)

    def setAllVisible(self, visible, *widgets):
        for widget in widgets:
            widget.setVisible(visible)

    def soundPressed (self, item):
        self.userSound = self.availableSoundsList.itemWidget(item).getFilePath()
        self.availableSoundsList.itemWidget(item).setStyleSheet("background-color: darkcyan;")
        if not self.userSoundLast is None and self.userSoundLast != item:
            self.availableSoundsList.itemWidget(self.userSoundLast).setStyleSheet("background-color: cadetblue;")
        self.userSoundLast = item

    def changePressed(self):
        if not self.userSound is None:
            self.selectedSoundAbsolutePathDir = f"{self.tf2_path}/tf/custom/TF2 Hitsound Manager/sound/{os.path.dirname(self.selectedSound)}"
            self.selectedSoundAbsolutePath = f"{self.selectedSoundAbsolutePathDir}/{os.path.basename(self.selectedSound)}"

            self.selectedSoundStorePathDir = f"{wd}/data/sound/{os.path.dirname(self.selectedSound)}"
            self.selectedSoundStorePath = f"{self.selectedSoundStorePathDir}/{os.path.basename(self.userSound)}"

            os.makedirs(self.selectedSoundAbsolutePathDir, exist_ok=True)

            base_name = os.path.basename(self.selectedSound).split('.')
            if os.path.exists(self.selectedSoundAbsolutePath):
                selectedSound_name = base_name[0]

                if self.selectedSound not in self.config:
                    copy_num = 2
                    export_path = f"{selectedSound_name}.{base_name[1]}"
                    while os.path.exists(f"{self.selectedSoundStorePathDir}/{export_path}"):
                        export_path = f"{selectedSound_name} ({copy_num}).{base_name[1]}"
                        copy_num += 1
                    shutil.copy(self.selectedSoundAbsolutePath, f"{self.selectedSoundStorePathDir}/{export_path}")
                    self.availableSoundsListAdd(export_path)

                os.remove(self.selectedSoundAbsolutePath)

            audio = AudioSegment.from_file(self.selectedSoundStorePath)
            audio = audio.set_frame_rate(44100)
            audio = audio.set_sample_width(2)
            audio.export(f"{self.selectedSoundAbsolutePathDir}/{os.path.basename(self.selectedSound)}", format=base_name[1])

            self.config[self.selectedSound] = self.userSound
            with open(f'{wd}/data/config.json', 'w') as f:
                json.dump(self.config, f)

            self.activeSoundLabel.setText(f"<p>Active sound at<br>\"{self.selectedSound}\":<br><br><span style = \"color: pink; font-size: 15pt;\">{self.userSound}<p>")

    def importPressed(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Import custom sounds")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            os.makedirs(f"{wd}/data/sound/{os.path.dirname(self.selectedSound)}", exist_ok=True)
            for selected_file in selected_files:
                try:
                    AudioSegment.from_file(selected_file)
                except CouldntDecodeError:
                    continue
                else:
                    copy_num = 2
                    base_name = os.path.basename(selected_file)
                    name = base_name.split('.')[0]
                    extension = base_name.split('.')[1]
                    export_path = base_name
                    while export_path in os.listdir(f"{wd}/data/sound/{os.path.dirname(self.selectedSound)}"):
                        export_path = f"{name} ({copy_num}).{extension}"
                        copy_num += 1
                    shutil.copy(selected_file, f"{wd}/data/sound/{os.path.dirname(self.selectedSound)}/{export_path}")
                    self.availableSoundsListAdd(export_path)


    def textChanged (self):
        self.getResults()

    def writeTF2Path (self, tf2_path):
        self.config = {'tf2_path': tf2_path}
        self.tf2_path = tf2_path
        with open(f"{wd}/data/config.json", 'w') as f:
            json.dump(self.config, f)

def main ():
   app = QApplication(sys.argv)
   QFontDatabase.addApplicationFont(f"{wd}/assets/fonts/tf2build.ttf")
   app.setStyleSheet(open(f'{wd}/assets/styles/style.qss').read())
   widget = Widget()
   sys.exit(app.exec_())


if __name__ == '__main__':
   main()