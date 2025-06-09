import random
import math
from panda3d.core import (
    GeomNode, GeomVertexFormat, GeomVertexData, Geom, GeomVertexWriter,
    GeomPoints, RenderModeAttrib, Shader, GeomVertexReader, CardMaker
)
from utils.constants import (
    SKYDOME_MODEL_PATH, SKYDOME_SCALE, SKYDOME_COLOR, SKYDOME_BIN, SKYDOME_DEPTHWRITE, SKYDOME_LIGHTOFF, SKYDOME_RADIUS,
    STAR_CONTAINER_NAME, STAR_BIN, STAR_DEPTHWRITE, STAR_LIGHTOFF,
    STAR_POINTS_NODE_NAME, STAR_NUM, STAR_POINT_SIZE,
    FALLBACK_SKY_FRAME, FALLBACK_SKY_P, FALLBACK_SKY_Z, FALLBACK_SKY_BIN, FALLBACK_SKY_DEPTHWRITE, FALLBACK_SKY_LIGHTOFF
)

def load_space(game):
    """加载星空，优先点精灵，失败则回退平面"""
    try:
        return create_star_sprites(game)
    except Exception as e:
        print(f"星空创建失败: {e}")
        return create_fallback_sky_plane(game)

def create_star_sprites(game):
    """使用点精灵创建3D星星"""
    print("使用点精灵创建星空")
    skydome = game.loader.loadModel(SKYDOME_MODEL_PATH)
    skydome.setScale(SKYDOME_SCALE)
    skydome.setTwoSided(True)
    skydome.setColor(*SKYDOME_COLOR)
    skydome.setBin(SKYDOME_BIN, 0)
    skydome.setDepthWrite(SKYDOME_DEPTHWRITE)
    skydome.setLightOff(SKYDOME_LIGHTOFF)
    skydome.reparentTo(game.render)

    game.stars = game.render.attachNewNode(STAR_CONTAINER_NAME)
    game.stars.setBin(STAR_BIN, 1)
    game.stars.setDepthWrite(STAR_DEPTHWRITE)
    game.stars.setLightOff(STAR_LIGHTOFF)

    game.star_points = GeomNode(STAR_POINTS_NODE_NAME)
    star_points_np = game.stars.attachNewNode(game.star_points)

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
    game.star_points.addGeom(geom)
    star_points_np.setAttrib(RenderModeAttrib.make(1))
    star_points_np.setRenderModeThickness(STAR_POINT_SIZE)
    game.star_twinkle_task = game.taskMgr.add(lambda task: twinkle_stars(game, task), "twinkleStars")
    print("使用点精灵创建星空成功")
    return game.stars

def twinkle_stars(game, task):
    """星星闪烁动画效果"""
    if hasattr(game, 'star_points'):
        try:
            geom = game.star_points.modifyGeom(0)
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

def create_fallback_sky_plane(game):
    """创建简单的星空平面 - 回退方案"""
    print("使用平面回退方案创建星空")
    try:
        cm = CardMaker("fallback_sky")
        cm.setFrame(FALLBACK_SKY_FRAME)
        sky = game.render.attachNewNode(cm.generate())
        sky.setP(FALLBACK_SKY_P)
        sky.setZ(FALLBACK_SKY_Z)
        sky.setBin(FALLBACK_SKY_BIN, 1)
        sky.setDepthWrite(FALLBACK_SKY_DEPTHWRITE)
        sky.setLightOff(FALLBACK_SKY_LIGHTOFF)
        shader = Shader.make("""
            #version 140
            uniform mat4 p3d_ModelViewProjectionMatrix;
            in vec4 p3d_Vertex;
            in vec2 p3d_MultiTexCoord0;
            out vec2 texcoord;
            void main() {
                gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                texcoord = p3d_MultiTexCoord0;
            }
        """, """
            #version 140
            uniform sampler2D p3d_Texture0;
            in vec2 texcoord;
            out vec4 fragColor;
            void main() {
                vec3 bgColor = vec3(0.0, 0.0, 0.05);
                float stars = 0.0;
                vec2 uv = texcoord * 100.0;
                vec2 ipos = floor(uv);
                vec2 fpos = fract(uv);
                float r = fract(sin(dot(ipos, vec2(127.1, 311.7))) * 43758.545);
                if (r > 0.99) {
                    float size = 0.05;
                    float dist = length(fpos - 0.5);
                    stars = smoothstep(size, 0.0, dist);
                }
                vec3 color = mix(bgColor, vec3(1.0), stars);
                fragColor = vec4(color, 1.0);
            }
        """)
        sky.setShader(shader)
        return sky
    except Exception as e:
        print(f"平面回退方案失败: {e}")
        game.setBackgroundColor(0, 0, 0.05, 1)
        print("使用纯深蓝色背景")
        return None