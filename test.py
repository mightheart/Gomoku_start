from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

         # 加载模型
        self.model = self.loader.loadModel("models/qihe.bam")
        self.model.reparentTo(self.render)
        self.model.setPos(0, 0, 0)
        self.model.setScale(0.01)


       


app = MyApp()
app.run()