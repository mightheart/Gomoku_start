"""测试模型加载"""
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *
import traceback

class ModelTester(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.test_models()
    
    def test_models(self):
        """测试各个模型的加载"""
        models_to_test = [
            ("square", "square模型"),
            ("qi_pan.obj", "棋盘厚度模型"),
            ("qihe.obj", "棋盒装饰模型"),
            ("Raiden shogun.glb", "对手模型"),
            ("background2.jpg", "背景图片"),
            ("kk.bam", "地面模型"),
            ("lulu.glb", "水豚噜噜模型"),
        ]
        
        for model_path, model_name in models_to_test:
            try:
                print(f"\n测试 {model_name} ({model_path})...")
                
                if model_path.endswith('.jpg'):
                    # 测试纹理
                    texture = self.loader.loadTexture(model_path)
                    if texture:
                        print(f"  ✓ {model_name} 纹理加载成功")
                    else:
                        print(f"  ✗ {model_name} 纹理加载失败")
                else:
                    # 测试模型
                    model = self.loader.loadModel(model_path)
                    if model and not model.isEmpty():
                        print(f"  ✓ {model_name} 模型加载成功")
                        
                        # 检查边界盒
                        bounds = model.getBounds()
                        if bounds and not bounds.isEmpty():
                            print(f"    边界盒: {bounds}")
                        else:
                            print(f"    警告: 边界盒无效")
                        
                        # 检查变换矩阵
                        model.setScale(1, 1, 1)
                        transform = model.getTransform()
                        if transform:
                            mat = transform.getMat()
                            if mat.isNan():
                                print(f"    警告: 变换矩阵包含NaN")
                            else:
                                print(f"    变换矩阵正常")
                        
                        model.removeNode()
                    else:
                        print(f"  ✗ {model_name} 模型加载失败")
                        
            except Exception as e:
                print(f"  ✗ {model_name} 测试失败: {e}")
                traceback.print_exc()
        
        # 测试Actor模型
        try:
            print(f"\n测试战士Actor模型...")
            actor = Actor("zhanshi.glb")
            if actor and not actor.isEmpty():
                print(f"  ✓ 战士Actor加载成功")
                
                # 检查动画
                anims = actor.getAnimNames()
                print(f"    动画数量: {len(anims)}")
                
                # 检查边界盒
                bounds = actor.getBounds()
                if bounds and not bounds.isEmpty():
                    print(f"    边界盒: {bounds}")
                else:
                    print(f"    警告: 边界盒无效")
                
                actor.removeNode()
            else:
                print(f"  ✗ 战士Actor加载失败")
        except Exception as e:
            print(f"  ✗ 战士Actor测试失败: {e}")
            traceback.print_exc()
        
        print("\n模型测试完成，3秒后退出...")
        self.taskMgr.doMethodLater(3, self.exit_test, 'exit-test')
    
    def exit_test(self, task):
        self.userExit()
        return task.done

if __name__ == "__main__":
    tester = ModelTester()
    tester.run()