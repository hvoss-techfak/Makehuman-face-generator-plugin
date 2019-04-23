#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Marc Flerackers, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

TODO
"""

import random
from threading import Thread

import PIL
import gui3d
import gui
import mh
import os
from core import G
import log
import numpy as np
import face_recognition
import cv2

import scandir
from PIL import Image


class MyAction(gui3d.Action):
    def __init__(self, human, before, after):
        super(MyAction, self).__init__("Face Reconstruct")
        self.human = human
        self.before = before
        self.after = after

    def do(self):
        self._assignModifierValues(self.after)
        return True

    def undo(self):
        self._assignModifierValues(self.before)
        return True

    def _assignModifierValues(self, valuesDict):
        _tmp = self.human.symmetryModeEnabled
        self.human.symmetryModeEnabled = False
        for mName, val in valuesDict.items():
            try:
                log.notice(mName)
                log.notice(val)
                self.human.getModifier(mName).setValue(val)
            except:
                pass
        self.human.applyAllTargets()
        self.human.symmetryModeEnabled = _tmp


class FaceTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Face Reconstruction')
        toolbox = self.addLeftWidget(gui.SliderBox('Face Reconstruction'))

        self.Dir = toolbox.addWidget(gui.BrowseButton(mode='dir'), 0, 0)
        self.Dir.setLabel('Face Reference Directory')
        self.Dir.directory = '.' #mh.getPath('scripts')

        self.fast = toolbox.addWidget(gui.CheckBox("Fast Method", False))
        self.semifast = toolbox.addWidget(gui.CheckBox("Normal Method", False))
        self.slow = toolbox.addWidget(gui.CheckBox("Slow Method", False))
        self.rslow = toolbox.addWidget(gui.CheckBox("Really Slow Method", False))
        self.brute = toolbox.addWidget(gui.CheckBox("Bruteforce Method", False))
        self.random = toolbox.addWidget(gui.CheckBox("Random Method (best)", True))
        self.epoch = toolbox.addWidget(gui.Slider(5, 4, 20,
                                                 ["Epoch rounds (only for random method)", ": %d"]))
        self.iter = toolbox.addWidget(gui.Slider(3, 1, 50,
                                                    ["Iterations Per Modifier (only for random method)", ": %d"]))
        self.faceBtn = toolbox.addWidget(gui.Button("Do Face Reconstruction"))
        self.cam = G.app.modelCamera
        self.human = gui3d.app.selectedHuman
        self.fcount = 0
        cv2.namedWindow("Face Preview")


        @self.faceBtn.mhEvent
        def onClicked(event):
            if self.Dir.directory == '.':
                log.error("Not a valid reference folder. Aborting...")
                return
            avg = self.createavg()
            if avg is None:
                log.error("Not a valid reference folder. Aborting...")
                return
            log.notice(self.createavg())
            modifierGroups = ['eyebrows', 'eyes', 'chin',
                              'forehead', 'head', 'mouth', 'nose', 'neck', 'ears',
                              'cheek']
            modifiers = []

            for mGroup in modifierGroups:
                modifiers = modifiers + self.human.getModifiersByGroup(mGroup)

            # Make sure not all modifiers are always set in the same order
            # (makes it easy to vary dependent modifiers like ethnics)
            random.shuffle(modifiers)
            with open("Output.txt", "w", buffering=1) as text_file:
                if self.fast.selected:
                    self.checkFace([0.2,  0.2], text_file, avg, modifiers)
                    self.checkFace([-0.4, 0.4], text_file, avg, modifiers)

                if self.semifast.selected:
                    self.checkFace([-0.4, -0.2, 0.2, 0.4], text_file, avg, modifiers)
                    self.checkFace([-0.8, -0.6, 0.6, 0.8], text_file, avg, modifiers)

                if self.slow.selected:
                    self.checkFace([-0.2, -0.1, 0.1, 0.2], text_file, avg, modifiers)
                    self.checkFace([-0.4, -0.3, 0.3, 0.4], text_file, avg, modifiers)
                    self.checkFace([-0.6, -0.5, 0.5, 0.6], text_file, avg, modifiers)
                    self.checkFace([-0.8, -0.7, 0.7, 0.8], text_file, avg, modifiers)

                if self.rslow.selected:
                    self.checkFace([-0.2, -0.1, 0.1, 0.2], text_file, avg, modifiers)
                    self.checkFace([-0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4], text_file, avg, modifiers)
                    self.checkFace([-0.6, -0.5,-0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], text_file, avg, modifiers)
                    self.checkFace([-0.8, -0.7,-0.6, -0.5,-0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], text_file, avg, modifiers)
                if self.brute.selected:
                    self.checkFace([-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],text_file, avg, modifiers)

                if self.random.selected:
                    ip = 0.2
                    for j in range(int(self.epoch.getValue())):
                        self.checkFace(None,text_file, avg, modifiers,imin=-ip,imax=ip,c=int(self.iter.getValue()),irandom=True)
                        ip = min(ip + 0.2, 1.0)



            mh.redraw()

        # self.human.setPosition((0,0,0))

    def checkFace(self,mm,text_file,avg,modifiers,irandom=False,imin=-1.0,imax=1.0,c=3):
        blacklist = []
        random.shuffle(modifiers)
        bestdist = self.checkDist(avg,text_file)
        ie = 0
        for m in modifiers:
            text_file.write(str(ie) + " of " + str(len(modifiers)) + "\n")
            text_file.write(str(m.fullName) + "\n")
            log.notice(m)
            ie += 1
            if m.fullName not in blacklist:
                bestval = m.getValue()
                if irandom or mm is None:
                    mm = []
                    for i in range(c):
                        mm.append(random.uniform(imin, imax))
                st = m.getValue()
                symm = m.getSymmetricOpposite()
                blacklist.append(m.fullName)
                for i in mm:
                    val = i
                    oldValues = {}
                    newValues = {}

                    oldValues[m.fullName] = m.getValue()
                    newValues[m.fullName] = val

                    if symm:
                        oldValues[symm] = m.getValue()
                        newValues[symm] = val
                        if symm in modifiers:
                            modifiers.remove(symm)
                    gui3d.app.do(MyAction(self.human, oldValues, newValues))
                    mh.redraw()
                    dist = self.checkDist(avg, text_file)
                    if dist < bestdist:
                        bestdist = dist
                        bestval = val
                log.notice("best distance is:" + str(bestdist))
                text_file.write("best distance is:" + str(bestdist) + "\n")
                text_file.write("old  value    is:" + str(st) + "\n")
                text_file.write("best value    is:" + str(bestval) + "\n")
                oldValues = {}
                newValues = {}
                oldValues[m.fullName] = st
                newValues[m.fullName] = bestval
                if symm:
                    oldValues[symm] = st
                    newValues[symm] = bestval
                    blacklist.append(symm)
                    if symm in modifiers:
                        modifiers.remove(symm)
                gui3d.app.do(MyAction(self.human, oldValues, newValues))
                visim = self.makeImage([0, 0, 0])
                if visim is not None:
                    try:
                        visim = PIL.Image.fromarray(visim)
                        log.notice("show!")
                        cv2.imshow("Face Preview", cv2.cvtColor(np.asarray(visim), cv2.COLOR_BGR2RGB))
                        cv2.waitKey()
                        #visim.save("mh_vis.jpg")
                        #visim.save('{0:05d}'.format(self.fcount) + ".jpg")
                        self.fcount += 1
                    except Exception as e:
                        log.error(e)


    def createavg(self):
        ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'JPG', 'PNG', 'JPEG']
        avg = np.zeros(128)
        acc = 0
        knownImageFol = self.Dir.getPath()
        for dirName, subdirList, fileList in scandir.walk(knownImageFol):
            print("going to dir: " + dirName)
            for image_file in fileList:
                try:
                    full_file_path = dirName + "/" + image_file
                    if image_file.endswith(tuple(ALLOWED_EXTENSIONS)):
                        known_brandon_image = face_recognition.load_image_file(full_file_path)
                        face_locations = face_recognition.face_locations(known_brandon_image,
                                                                         number_of_times_to_upsample=0,
                                                                         model="cnn")
                        loadedface = np.asarray(face_recognition.face_encodings(known_brandon_image, num_jitters=10,
                                                                                known_face_locations=face_locations)[0])
                        acc += 1
                        avg += loadedface
                except Exception as e:
                    print(e)
        avg /= max(1, acc)
        return avg if acc > 0 else None


    def checkDist(self, avg,text_file):
        images = self.makeImages(text_file)
        ret = np.zeros(128)
        acc = 0

        for f in images:
            if f is not None:
                try:
                    pp = PIL.Image.fromarray(f)
                    pp = pp.convert('RGB')
                    pp = np.array(pp)
                    face_locations = face_recognition.face_locations(pp, number_of_times_to_upsample=0,
                                                                     model="cnn")
                    val = face_recognition.face_encodings(pp, num_jitters=1,
                                                          known_face_locations=face_locations)
                    if len(val) > 0:
                        loadedface = np.asarray(val[0])
                        ret += loadedface
                        acc += 1
                except Exception as e:
                    print(e)
                    text_file.write(str(e))
        ret /= max(1, acc)
        return np.linalg.norm(ret - avg)


    def makeImages(self,text_file):
        mh.redraw()
        ret = []
        try:
            log.notice(self.cam.zoomFactor)
            self.cam.zoomFactor = 3.5
            pos = self.human.getPosition()
            pos[1] = -7
            self.human.setPosition(pos)
            mh.redraw()

            ret.append(self.makeImage([0,0,0]))
            ret.append(self.makeImage([-10, 0, 0]))
            ret.append(self.makeImage([-20, 0, 0]))
            ret.append(self.makeImage([-30, 0, 0]))
            ret.append(self.makeImage([10, 0, 0]))
            ret.append(self.makeImage([20, 0, 0]))
            ret.append(self.makeImage([0, -10, 0]))
            ret.append(self.makeImage([0, -20, 0]))
            ret.append(self.makeImage([0, -30, 0]))
            ret.append(self.makeImage([0, 10, 0]))
            ret.append(self.makeImage([0, 20, 0]))
            ret.append(self.makeImage([0, 30, 0]))

            self.human.setRotation([0, 0, 0])
            mh.redraw()
        except Exception as e:
            print(e)
            text_file.write(str(e))
        return ret

    def makeImage(self,rot):
        try:
            self.human.setRotation(rot)
            mh.redraw()
            ret = mh.grabScreen(0, 0, G.windowWidth, G.windowHeight).data
            self.human.setRotation([0, 0, 0])
            mh.redraw()
            return ret
        except Exception as e:
            return None

def getFaceDist():
    print("no")


def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(FaceTaskView(category))


def unload(app):
    pass
