import openseespy.opensees as ops
from loguru import logger
import sys

# Logger配置用于并行执行,其他情况默认
if ops.getNP() > 1:
    logger = logger.bind(PID=ops.getPID(), NP=ops.getNP())
    logger.configure(handlers=[
        {
            "sink": sys.stderr,
            "format": "{time:YY-MM-DD HH:mm:ss} |<lvl>{level:8}</>| PID:<cyan>{extra[PID]}</> NP:<green>{extra[NP]}</> | <cyan>{module} : {function}:{line:4}</> - <lvl>{message}</>",
            "colorize": True
        },
    ])

class ParallelStructure:
    def __init__(self, WaterLevel=0.0):
        self.__init_parallel_parameters()
        
        # 建立模型
        ops.model('basic', '-ndm', 2, '-ndf', 2)
        # 1.正常定义材料
        self.define_materials()
        
        if self.Parallel:
            # 2.定义节点和单元（建议手动分别建立不同的单元）
            self.add_nodes_and_elements_for_pid()
            # 3.边界条件
            self.add_boundary_conditions_for_pid()
            # 4. 定义荷载
            self.set_load_for_pid()
        else:
            # 2.定义节点和单元
            self.add_nodes_and_elements_at_once()
            # 3.边界条件
            self.add_boundary_conditions_at_once()
            # 4. 定义荷载
            self.set_load_at_once() 
        
        # 5.进行分析（本例外部调用）
        # self.run_analysis()
        
        logger.success('完成ParallelStructure模型构建！')

    def __init_parallel_parameters(self):
        """初始化并行计算参数"""
        self.PID = ops.getPID()
        self.NP = ops.getNP()
        self.Parallel = self.NP > 1

    def define_materials(self):
        """定义材料"""
        ops.uniaxialMaterial('Elastic', 1, 3000.0)

    def add_nodes_and_elements_at_once(self):
        """一次性添加所有节点和单元"""
        ops.node(1, 0.0, 0.0)
        ops.node(2, 144.0, 0.0)
        ops.node(3, 168.0, 0.0)
        ops.node(4, 72.0, 96.0)

        ops.element('Truss', 1, 1, 4, 10.0, 1)
        ops.element('Truss', 2, 2, 4, 5.0, 1)
        ops.element('Truss', 3, 3, 4, 5.0, 1)
        
    def add_nodes_and_elements_for_pid(self):
        """为并行计算分别节点和单元"""
        if self.PID == 0:
            ops.node(1, 0.0, 0.0)
            ops.node(4, 72.0, 96.0)
            
            ops.element('Truss', 1, 1, 4, 10.0, 1)
        elif self.PID == 1:
            ops.node(2, 144.0, 0.0)
            ops.node(3, 168.0, 0.0)
            ops.node(4, 72.0, 96.0)
            
            ops.element('Truss', 2, 2, 4, 5.0, 1)
            ops.element('Truss', 3, 3, 4, 5.0, 1)
        else:
            raise ValueError(f'PID {self.PID} 超出范围！本例仅为2线程计算演示，请修改代码以适应更多线程！')
    
    def add_boundary_conditions_at_once(self):
        """一次性添加所有边界条件"""
        ops.fix(1, 1, 1)
        ops.fix(2, 1, 1)
        ops.fix(3, 1, 1)
    
    def add_boundary_conditions_for_pid(self):
        """为并行计算分别添加边界条件"""
        if self.PID == 0:
            ops.fix(1, 1, 1)
        elif self.PID == 1:
            ops.fix(2, 1, 1)
            ops.fix(3, 1, 1)
        else:
            raise ValueError(f'PID {self.PID} 超出范围！本例仅为2线程计算演示，请修改代码以适应更多线程！')
    
    def set_load_for_pid(self):
        """为并行计算分别添加荷载"""
        if self.PID == 0:
            ops.timeSeries('Linear', 1)
            ops.pattern('Plain', 1, 1)
            ops.load(4, 100.0, -50.0)
        
    def set_load_at_once(self):
        """一次性添加所有荷载"""
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        ops.load(4, 100.0, -50.0)
    
    def run_analysis(self):
        """运行结构分析"""
        # 设置分析参数
        # 注：以下运行参数仅为Truss静力计算的示例，不具有一般性，请根据需要修改
        ops.constraints('Transformation')
        ops.test('NormDispIncr', 1e-6, 6)
        ops.algorithm('Newton')
    
        if self.Parallel:
            # 并行计算编号方式可选'ParallelPlain'或'ParallelRCM'
            ops.numberer('ParallelPlain')
            # 并行计算只能选'Mumps'，单核计算不可选
            ops.system('Mumps')
        else:
            ops.numberer('Plain')
            ops.system('ProfileSPD')
        
        ops.integrator('LoadControl', 0.1)
        ops.analysis('Static')

        ops.analyze(10)

        if self.PID == 0:
            logger.info(f'Node 4(Step 1): [{ops.nodeCoord(4)}, {ops.nodeDisp(4)}]')

        ops.loadConst('-time', 0.0)

        if self.PID == 0:
            ops.pattern('Plain', 2, 1)
            ops.load(4, 1.0, 0.0)

        ops.domainChange()
        ops.integrator('ParallelDisplacementControl', 4, 1, 0.1)
        ops.analyze(10)

        if self.PID == 0:
            logger.info(f'Node 4(Step 2): [{ops.nodeCoord(4)}, {ops.nodeDisp(4)}]')

        logger.success('分析成功完成！')

if __name__ == "__main__":
    parallel_demo = ParallelStructure()
    parallel_demo.run_analysis()