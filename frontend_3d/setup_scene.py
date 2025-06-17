from panda3d.core import AmbientLight, DirectionalLight, LVector3, CardMaker, GeomNode, GeomVertexFormat, GeomVertexData, Geom, GeomVertexWriter, GeomPoints, RenderModeAttrib,GeomVertexReader
from direct.actor.Actor import Actor
import random
import math
from utils.constants import *

class SceneSetup:
    def __init__(self, loader, render, taskMgr):
        self.loader = loader
        self.render = render
        self.taskMgr = taskMgr
        # 记录加载的模型节点
        self.background_card = None
        self.ground_model = None
        self.leidian_model = None
        self.yaoyao_model = None
        self.skydome = None
        self.stars = None
        
        # 新增：光照节点引用
        self.ambient_light_np = None
        self.directional_light_np = None

    def setup_lighting(self):
        """设置光照"""
        ambient_light = AmbientLight("ambientLight")
        ambient_light.setColor((.8, .8, .8, 1))
        self.ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(self.ambient_light_np)

        directional_light = DirectionalLight("directionalLight")
        directional_light.setDirection(LVector3(0, 45, -45))
        directional_light.setColor((0.2, 0.2, 0.2, 1))
        self.directional_light_np = self.render.attachNewNode(directional_light)
        self.render.setLight(self.directional_light_np)

    def load_scene(self):
        """加载场景模型（背景、地面、角色、星空）"""
        # 背景
        try:
            background_texture = self.loader.loadTexture("models/background2.jpg")
            card_maker = CardMaker("background")
            card_maker.setFrame(-1, 1, -1, 1)
            self.background_card = self.render.attachNewNode(card_maker.generate())
            self.background_card.setTexture(background_texture)
            self.background_card.setPos(*BACKGROUND_POSITION)
            self.background_card.setScale(20)
        except Exception as e:
            print(f"背景加载失败: {e}")

        # 地面
        try:
            self.ground_model = self.loader.loadModel("models/kk.bam")
            self.ground_model.reparentTo(self.render)
            self.ground_model.setPos(0, 0, -5)
            self.ground_model.setScale(20)
            self.ground_model.setHpr(180, 0, 0)
            
        except Exception as e:
            print(f"地面模型加载失败: {e}")

        # 角色模型
        self._load_character_models()

        # 星空
        self.load_space()

    def _load_character_models(self):
        """加载角色模型"""
        try:
            self.leidian_model = Actor("models/pikaqiu.glb")
            self.leidian_model.reparentTo(self.render)
            self.leidian_model.setPos(-35, 30, -3)  
            self.leidian_model.setScale(15)
            self.leidian_anims = self.leidian_model.getAnimNames()
            self.current_anim_index = 0
            if self.leidian_anims:
                self.leidian_model.play(self.leidian_anims[self.current_anim_index])
                self.taskMgr.add(self._check_anim_completion, "checkAnimCompletion")
    
            # 移动和转向动画，所有z都为-4
            from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpHprInterval, Wait

            seq = Sequence(
                LerpPosInterval(self.leidian_model, 8.0, (-35, -240, -3)),
                LerpHprInterval(self.leidian_model, 1.0, (90, 0, 0)),
                LerpPosInterval(self.leidian_model, 8.0, (35, -240, -3)),
                LerpHprInterval(self.leidian_model, 1.0, (180, 0, 0)),
                LerpPosInterval(self.leidian_model, 8.0, (35, 30, -3)),
                LerpHprInterval(self.leidian_model, 1.0, (270, 0, 0)),
                LerpPosInterval(self.leidian_model, 8.0, (-35, 30, -3)),
                LerpHprInterval(self.leidian_model, 1.0, (0, 0, 0)),
                Wait(1.0)
            )
            seq.loop()
        except Exception as e:
            print(f"皮卡丘模型加载失败: {e}")


    def _check_anim_completion(self, task):
        """检查动画完成"""
        if not hasattr(self, 'leidian_model') or self.leidian_model.isEmpty():
            return task.done
        if not self.leidian_anims:
            return task.done
        current_anim = self.leidian_anims[self.current_anim_index]
        anim_control = self.leidian_model.getAnimControl(current_anim)
        if anim_control is None or not anim_control.isPlaying():
            self.current_anim_index = (self.current_anim_index + 1) % len(self.leidian_anims)
            next_anim = self.leidian_anims[self.current_anim_index]
            self.leidian_model.play(next_anim)
        return task.cont
    
    def load_space(self):
        try:
            # 方法1：使用点精灵创建星空（最可靠）
            return self.create_star_sprites()

        except Exception as e:
            print(f"星空创建失败: {e}")
            # 方法2：使用简单平面纹理回退
            return self._load_starfield()

    def create_star_sprites(self):
        """使用点精灵创建3D星星 - 最可靠的方法"""
        skydome = self.loader.loadModel(SKYDOME_MODEL_PATH)
        skydome.setScale(SKYDOME_SCALE)
        skydome.setTwoSided(True)
        skydome.setColor(*SKYDOME_COLOR)
        skydome.setBin(SKYDOME_BIN, 0)
        skydome.setDepthWrite(SKYDOME_DEPTHWRITE)
        skydome.setLightOff(SKYDOME_LIGHTOFF)
        skydome.reparentTo(self.render)

        self.stars = self.render.attachNewNode(STAR_CONTAINER_NAME)
        self.stars.setBin(STAR_BIN, 1)
        self.stars.setDepthWrite(STAR_DEPTHWRITE)
        self.stars.setLightOff(STAR_LIGHTOFF)

        self.star_points = GeomNode(STAR_POINTS_NODE_NAME)
        star_points_np = self.stars.attachNewNode(self.star_points)

        vformat = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("stars", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        color = GeomVertexWriter(vdata, "color")

        for _ in range(STAR_NUM):
            theta = random.uniform(0, math.pi)
            phi = random.uniform(0, 2 * math.pi)
            r = SKYDOME_RADIUS
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            vertex.addData3f(x, y, z)
            brightness = random.uniform(0.7, 1.0)
            if random.random() < 0.8:
                rr = gg = bb = brightness
            else:
                rr = brightness * random.uniform(0.8, 1.0)
                gg = brightness * random.uniform(0.7, 0.9)
                bb = brightness * random.uniform(0.9, 1.0)
            color.addData4f(rr, gg, bb, 1.0)

        points = GeomPoints(Geom.UHStatic)
        points.addConsecutiveVertices(0, STAR_NUM)
        points.closePrimitive()
        geom = Geom(vdata)
        geom.addPrimitive(points)
        self.star_points.addGeom(geom)
        star_points_np.setAttrib(RenderModeAttrib.make(1))
        star_points_np.setRenderModeThickness(STAR_POINT_SIZE)
        self.star_twinkle_task = self.taskMgr.add(self.twinkle_stars, "twinkleStars")
        return self.stars

    def twinkle_stars(self, task):
        """星星闪烁动画效果"""
        if hasattr(self, 'star_points'):
            try:
                geom = self.star_points.modifyGeom(0)
                vdata = geom.modifyVertexData()
                color_reader = GeomVertexReader(vdata, "color")
                color_writer = GeomVertexWriter(vdata, "color")
                num_vertices = vdata.getNumRows()
                for i in range(num_vertices):
                    color_reader.setRow(i)
                    color_writer.setRow(i)
                    r, g, b, a = color_reader.getData4f()
                    if random.random() < 0.1:
                        brightness_change = random.uniform(0.8, 1.2)
                        r = min(1.0, max(0.2, r * brightness_change))
                        g = min(1.0, max(0.2, g * brightness_change))
                        b = min(1.0, max(0.2, b * brightness_change))
                        color_writer.setData4f(r, g, b, a)
                geom.setVertexData(vdata)
            except Exception as e:
                print(f"星星闪烁动画出错: {e}")
        return task.cont

    def _load_starfield(self):
        """加载星空"""
        try:
            skydome = self.loader.loadModel(SKYDOME_MODEL_PATH)
            skydome.setScale(SKYDOME_SCALE)
            skydome.setTwoSided(True)
            skydome.setColor(*SKYDOME_COLOR)
            skydome.setBin(SKYDOME_BIN, 0)
            skydome.setDepthWrite(SKYDOME_DEPTHWRITE)
            skydome.setLightOff(SKYDOME_LIGHTOFF)
            skydome.reparentTo(self.render)
            self._create_stars()
        except Exception as e:
            print(f"星空加载失败: {e}")

    def _create_stars(self):
        """创建星星"""
        self.stars = self.render.attachNewNode(STAR_CONTAINER_NAME)
        self.stars.setBin(STAR_BIN, 1)
        self.stars.setDepthWrite(STAR_DEPTHWRITE)
        self.stars.setLightOff(STAR_LIGHTOFF)
        star_points = GeomNode(STAR_POINTS_NODE_NAME)
        star_points_np = self.stars.attachNewNode(star_points)
        vformat = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("stars", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        color = GeomVertexWriter(vdata, "color")
        for _ in range(STAR_NUM):
            theta = random.uniform(0, math.pi)
            phi = random.uniform(0, 2 * math.pi)
            r = SKYDOME_RADIUS
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            vertex.addData3f(x, y, z)
            brightness = random.uniform(0.7, 1.0)
            if random.random() < 0.8:
                rr, gg, bb = brightness, brightness, brightness
            else:
                rr, gg, bb = brightness, brightness * 0.8, brightness * 0.6
            color.addData4f(rr, gg, bb, 1.0)
        points = GeomPoints(Geom.UHStatic)
        points.addConsecutiveVertices(0, STAR_NUM)
        points.closePrimitive()
        geom = Geom(vdata)
        geom.addPrimitive(points)
        star_points.addGeom(geom)
        star_points_np.setAttrib(RenderModeAttrib.make(1))
        star_points_np.setRenderModeThickness(STAR_POINT_SIZE)

    def cleanup(self):
        """清理所有加载的模型节点和光照"""
        if self.background_card:
            self.background_card.removeNode()
            self.background_card = None
        if self.ground_model:
            self.ground_model.removeNode()
            self.ground_model = None
        if self.leidian_model:
            self.leidian_model.removeNode()
            self.leidian_model = None
        if self.yaoyao_model:
            self.yaoyao_model.removeNode()
            self.yaoyao_model = None
        if self.skydome:
            self.skydome.removeNode()
            self.skydome = None
        if self.stars:
            self.stars.removeNode()
            self.stars = None
        # 移除星星闪烁任务
        if hasattr(self, "star_twinkle_task"):
            self.taskMgr.remove(self.star_twinkle_task)
            del self.star_twinkle_task
        # 新增：清理光照节点
        if self.ambient_light_np:
            self.render.clearLight(self.ambient_light_np)
            self.ambient_light_np.removeNode()
            self.ambient_light_np = None
        if self.directional_light_np:
            self.render.clearLight(self.directional_light_np)
            self.directional_light_np.removeNode()
            self.directional_light_np = None