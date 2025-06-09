"""特效管理模块"""
import random
import math
from utils.constants import FIREWORK_COLORS, VICTORY_PARTICLE_DURATION, BOARD_SIZE
from utils.helpers import square_pos

class EffectsManager:
    """特效管理器"""
    
    def __init__(self, render, task_mgr):
        self.render = render
        self.task_mgr = task_mgr
        self.victory_particles = []
    
    def create_victory_particles(self, winner_positions):
        """创建胜利粒子特效"""
        for pos in winner_positions:
            for i in range(20):  # 每个位置20个粒子
                particle = self.render.attachNewNode("particle")
                square_position = square_pos(pos[0] * BOARD_SIZE + pos[1])
                particle.setPos(
                    square_position.x + random.uniform(-0.5, 0.5),
                    square_position.y + random.uniform(-0.5, 0.5),
                    random.uniform(0, 2)
                )
                
                # 随机颜色
                color = random.choice(FIREWORK_COLORS)
                particle.setColorScale(*color)
                
                # 添加动画
                self._animate_particle(particle, i * 0.05)
                self.victory_particles.append(particle)
    
    def _animate_particle(self, particle, delay):
        """粒子动画"""
        def particle_task(task):
            if not particle or particle.isEmpty():
                return task.done
            
            try:
                if task.time < VICTORY_PARTICLE_DURATION:
                    current_pos = particle.getPos()
                    new_z = current_pos.z + 0.5 * task.dt
                    particle.setZ(new_z)
                    
                    # 透明度变化
                    alpha = 1.0 - (task.time / VICTORY_PARTICLE_DURATION)
                    current_color = particle.getColorScale()
                    particle.setColorScale(current_color[0], current_color[1], current_color[2], alpha)
                    
                    return task.cont
                else:
                    if not particle.isEmpty():
                        particle.removeNode()
                    if particle in self.victory_particles:
                        self.victory_particles.remove(particle)
                    return task.done
            except Exception as e:
                print(f"粒子动画出错: {e}")
                try:
                    if not particle.isEmpty():
                        particle.removeNode()
                    if particle in self.victory_particles:
                        self.victory_particles.remove(particle)
                except:
                    pass
                return task.done
        
        self.task_mgr.doMethodLater(delay, particle_task, f"particle_anim_{id(particle)}")
    
    def cleanup_particles(self):
        """清理所有粒子"""
        for particle in self.victory_particles:
            if particle:
                particle.removeNode()
        self.victory_particles = []