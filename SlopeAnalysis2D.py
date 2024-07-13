import openseespy.opensees as ops
from collections import namedtuple, Counter
from alive_progress import alive_bar, alive_it
from loguru import logger
import opstool as opst
import time,sys
from EZSite.opsmaterial import EZOpsMaterial
from pathlib import Path

# logger configuration
if ops.getNP()>1:
    logger = logger.bind(PID=ops.getPID(), NP=ops.getNP())
    logger.configure(handlers=[
        {
            "sink": sys.stderr,
            "format": "{time:YY-MM-DD HH:mm:ss} |<lvl>{level:8}</>| PID:<cyan>{extra[PID]}</> NP:<green>{extra[NP]}</> | <cyan>{module} : {function}:{line:4}</> - <lvl>{message}</>",
            "colorize": True
        },
    ])

def define_file_path(DATA_PATH:Path, pathname:str)->Path:
        if not DATA_PATH.exists():
            logger.error(f'File at Path {DATA_PATH} does not exist!')
        return DATA_PATH / pathname

class SlopeAnalysis2D(EZOpsMaterial):
    if ops.getPID() == 0:
        logger.info('Start building the model for SlopeAnalysis2D...')
        logger.info('Created by Lingyun Gou, Ph.D. Candidate at Tongji University, July 2024. Email:gulangyu@tongji.edu.cn')
        
    # Data Path
    ABS_PATH = Path(__file__).parent
    data_path = 'SlopeAnalysis2Dexample'
    data_file_path = ABS_PATH.joinpath(data_path)
    if data_file_path.is_dir():
        DATA_PATH = data_file_path
        logger.info(f'Using Data in path {DATA_PATH}')
        
        NODEINFO_PATH = define_file_path(DATA_PATH, 'nodeInfo.dat')  
        ELEMENTINFO_PATH = define_file_path(DATA_PATH, 'elementInfo.dat')
        FIXNODESINFO_PATH = define_file_path(DATA_PATH, 'fixedNodeInfo.dat')
        EQDOF_01_INFO_PATH = define_file_path(DATA_PATH, 'EqualDOFnodes_01_Info.dat')
        EQDOF_02_INFO_PATH = define_file_path(DATA_PATH, 'EqualDOFnodes_02_Info.dat')
        EQDOF_BASE_INFO_PATH = define_file_path(DATA_PATH, 'EqualDOFnodes_Base_Info.dat')
        MASS_INFO_PATH = define_file_path(DATA_PATH, 'massInfo.dat')
    else:
        logger.error(f'There is no directory named "{data_path}" in current path: {ABS_PATH}!')
    
    @property
    def NodesDict_ALL(self)->dict[namedtuple]:
        keys = [node.tag for node in self.Nodes_ALL]
        return dict(zip(keys, self.Nodes_ALL))
    
    @property
    def NodesDict(self)->dict[namedtuple]:
        keys = [node.tag for node in self.Nodes]
        return dict(zip(keys, self.Nodes))
    
    def __init_properties(self, WaterLevel)->None:
        self.WaterLevel = WaterLevel
        self._SOIL_MAT_PROP()
        self.MAT_TAG_NAME_MAP = self.MAT_TAG_NAME_MAP()
        self.MAT_NAME_TAG_MAP = self.MAT_NAME_TAG_MAP()
        self._SOIL_ELE_PROP()

    def MAT_NAME_TAG_MAP(self)->dict[str,int]:
        """
        Soil Material Name and Tag Map
        """
        return {name:prop.matTag for name, prop in self.SOIL_MAT_PROP.items()}
    
    def MAT_TAG_NAME_MAP(self)->dict[int,str]:
        """
        Soil Material Tag and Name Map
        """
        return {prop.matTag:name for name, prop in self.SOIL_MAT_PROP.items()}
    
    def _SOIL_MAT_PROP(self)->None:
        """
        Soil material parameters (https://opensees.berkeley.edu/wiki/index.php?title=File:2DsoilProfileMap.png)
        return: None
        Soil Layers:
            silt1:tag=1
            loose sand:tag=2
            silt2:tag=3
            silt3:tag=4
            dense sand1:tag=5
            dense sand2:tag=6
            sandy gravel:tag=7
        """
        if not hasattr(self, 'SOIL_MAT_PROP'):
            # 创建材料对象
            soil_material_property = dict()
            # silt
            soil_material_property["silt1"] = self.PIMY(SoilType='PressureIndependMultiYield',
                                                       matTag=1,
                                                       rho=1.68,
                                                       ShearModul=14046.9,
                                                       BulkModul=42140.7,
                                                       cohesion=35.9,
                                                       peakShearStrain=0.1,
                                                       frictionAng=0.0,
                                                       refPress=100.0,
                                                       pressDependCoef=0.0,
                                                       noYieldSurf=30,
                                                       note='silt1'
                                                       )
            # loose sand
            soil_material_property["loose sand"] = self.PIMY(SoilType='PressureIndependMultiYield',
                                                       matTag=2,
                                                       rho=1.68,
                                                       ShearModul=39020.0,
                                                       BulkModul=117060.0,
                                                       cohesion=183.8,
                                                       peakShearStrain=0.1,
                                                       frictionAng=0.0,
                                                       refPress=100.0,
                                                       pressDependCoef=0.0,
                                                       noYieldSurf=30,
                                                       note='sand'
                                                       )
            # silt2
            soil_material_property["silt2"] = self.PIMY(SoilType='PressureIndependMultiYield',
                                                        matTag=3,
                                                        rho=1.68,
                                                        ShearModul=87793.4,
                                                        BulkModul=263380.0,
                                                        cohesion=183.8,
                                                        peakShearStrain=0.1,
                                                        frictionAng=0.0,
                                                        refPress=100.0,
                                                        pressDependCoef=0.0,
                                                        noYieldSurf=30,
                                                        note='silt2'
                                                        )
            # silt3                                               
            soil_material_property["silt3"] = self.PDMY02(SoilType='PressureDependMultiYield02',
                                                          matTag=4,
                                                          rho=1.84,
                                                          ShearModul=42735.4,
                                                          BulkModul=128206.2,
                                                          frictionAng=33,
                                                          peakShearStrain=0.1,
                                                          refPress=100,
                                                          pressDependCoef=0.5,
                                                          PTAng=26,
                                                          contrac1=0.067,
                                                          contrac3=0.23,
                                                          dilat1=0.06,
                                                          dilat3=0.27,
                                                          noYieldSurf=30,
                                                          contrac2=5.0,
                                                          dilat2=3.0,
                                                          Liq1=1.0,
                                                          Liq2=0.0,
                                                          e=0.73,
                                                          cs1=0.9,
                                                          cs2=0.02,
                                                          cs3=0.7,
                                                          pa=101,
                                                          note='silt3'
                                                          )
            # dense sand                                              
            soil_material_property["dense sand1"] = self.PDMY02(SoilType='PressureDependMultiYield02',
                                                                matTag=5,
                                                                rho=2.24,
                                                                ShearModul=42735.4,
                                                                BulkModul=128206.2,
                                                                frictionAng=40,
                                                                peakShearStrain=0.1,
                                                                refPress=100,
                                                                pressDependCoef=0.5,
                                                                PTAng=26,
                                                                contrac1=0.013,
                                                                contrac3=0.0,
                                                                dilat1=0.3,
                                                                dilat3=0.0,
                                                                noYieldSurf=30,
                                                                contrac2=5.0,
                                                                dilat2=3.0,
                                                                Liq1=1.0,
                                                                Liq2=0.0,
                                                                e=0.532,
                                                                cs1=0.9,
                                                                cs2=0.02,
                                                                cs3=0.7,
                                                                pa=101,
                                                                note='dense sand1'
                                                                )
            # dense sand2
            soil_material_property["dense sand2"] = self.PDMY02(SoilType='PressureDependMultiYield02',
                                                                matTag=6,
                                                                rho=2.24,
                                                                ShearModul=42735.4,
                                                                BulkModul=128206.2,
                                                                frictionAng=40,
                                                                peakShearStrain=0.1,
                                                                refPress=100,
                                                                pressDependCoef=0.5,
                                                                PTAng=26,
                                                                contrac1=0.013,
                                                                contrac3=0.0,
                                                                dilat1=0.3,
                                                                dilat3=0.0,
                                                                noYieldSurf=30,
                                                                contrac2=5.0,
                                                                dilat2=3.0,
                                                                Liq1=1.0,
                                                                Liq2=0.0,
                                                                e=0.49,
                                                                cs1=0.9,
                                                                cs2=0.02,
                                                                cs3=0.7,
                                                                pa=101,
                                                                note='dense sand2'
                                                                )
            # sandy gravel
            soil_material_property["sandy gravel"] = self.PDMY02(SoilType='PressureDependMultiYield02',
                                                                matTag=7,
                                                                rho=2.24,
                                                                ShearModul=42735.4,
                                                                BulkModul=128206.2,
                                                                frictionAng=40,
                                                                peakShearStrain=0.1,
                                                                refPress=100,
                                                                pressDependCoef=0.5,
                                                                PTAng=26,
                                                                contrac1=0.013,
                                                                contrac3=0.0,
                                                                dilat1=0.3,
                                                                dilat3=0.0,
                                                                noYieldSurf=30,
                                                                contrac2=5.0,
                                                                dilat2=3.0,
                                                                Liq1=1.0,
                                                                Liq2=0.0,
                                                                e=0.49,
                                                                cs1=0.9,
                                                                cs2=0.02,
                                                                cs3=0.7,
                                                                pa=101,
                                                                note='sandy gravel'
                                                                )
                         
            self.SOIL_MAT_PROP = soil_material_property
        else:
            logger.warning('Soil Material Properties already defined!')

    def _SOIL_ELE_PROP(self)->None:
        """
        Soil element parameters
        return: Soil Element Dict[namedtuple]
        """
        if not hasattr(self, 'SOIL_ELE_PROP'):
            ele_info = namedtuple('ele_info', ['thick', 'matTag', 'bulk', 'fmass', 'hperm', 'vperm', 'unitWeightX', 'unitWeightY'], defaults=[1.0, 9901, 2.2e6/0.6, 1.0, 1e-7, 1e-7, 0.0, -9.81])
            soil_ele_prop = dict()
            # define element properties(Only specificed properties are defined, like bulk modulus, shear modulus, and permeability etc.)
            # silt1:tag=1
            soil_ele_prop["silt1"] = ele_info(matTag=self.SOIL_MAT_PROP["silt1"].matTag, bulk=2.2e5, vperm=1.0e-5, hperm=1.0e-5)
            # loose sand:tag=2
            soil_ele_prop["loose sand"] = ele_info(matTag=self.SOIL_MAT_PROP["loose sand"].matTag, bulk=6.0e6, vperm=1.0e-5, hperm=1.0e-5)
            # silt2:tag=3
            soil_ele_prop["silt2"] = ele_info(matTag=self.SOIL_MAT_PROP["silt2"].matTag, bulk=6.0e6, vperm=1.0e-5, hperm=1.0e-5)
            # silt3:tag=4
            soil_ele_prop["silt3"] = ele_info(matTag=self.SOIL_MAT_PROP["silt3"].matTag, bulk=5.2e6, vperm=1.0e-4, hperm=1.0e-4)
            # dense sand1:tag=5
            soil_ele_prop["dense sand1"] = ele_info(matTag=self.SOIL_MAT_PROP["dense sand1"].matTag, bulk=6.3e6, vperm=1.0e-3, hperm=1.0e-3)
            # dense sand2:tag=6
            soil_ele_prop["dense sand2"] = ele_info(matTag=self.SOIL_MAT_PROP["dense sand2"].matTag, bulk=6.7e6, vperm=1.0e-3, hperm=1.0e-3)
            # sandy gravel:tag=7
            soil_ele_prop["sandy gravel"] = ele_info(matTag=self.SOIL_MAT_PROP["sandy gravel"].matTag, bulk=6.7e6, vperm=1.0e-3, hperm=1.0e-3)
            
            self.SOIL_ELE_PROP = soil_ele_prop
        else:
            logger.warning('Soil Element Properties already defined!')
    
    def define_soil_materials(self)->None:
        """
        define soil materials from SOIL_MATERIAL dict
        """
        for name, prop in self.SOIL_MAT_PROP.items():
            if prop.SoilType=='PressureDependMultiYield':
                self.define_PressureDependMultiYield(prop)
            elif prop.SoilType=='PressureDependMultiYield02':
                self.define_PressureDependMultiYield02(prop)
            elif prop.SoilType=='PressureDependMultiYield03':
                self.define_PressureDependMultiYield03(prop)
            elif prop.SoilType=='PressureIndependMultiYield':
                self.define_PressureIndependMultiYield(prop)
            else:
                raise ValueError('SoilType not defined!')
        logger.success('Finished creating all soil materials...')
    
    def _get_site_nodes(self)->None:
        """
        read node information from nodeInfo.dat
        """
        nodelist = []
        try:
            with open(SlopeAnalysis2D.NODEINFO_PATH, 'r') as f:
                for line in f:
                    line = line.split()
                    nodeTag = int(line[0])
                    x = float(line[1])
                    y = float(line[2])
                    nodelist.append(self.NODE2(nodeTag,x, y))
            self.Nodes_ALL = tuple(nodelist)
        except FileNotFoundError as e:
            logger.error(f'FileNotFoundError: {e}\nPlease check the file path!')
             
    def define_site_nodes(self)->None:
        """read node information from nodeInfo.dat and define soil nodes"""
        if not hasattr(self, 'Nodes'):
            self.split_nodes_and_elements()
        exist_nodes = self.opsNodes
        for node in self.Nodes:
            if node.tag not in exist_nodes:
                ops.node(node.tag, node.x, node.y)
            else:
                logger.warning(f'{node} already exists! Not created!')
        logger.success('Finished creating Site nodes...')
    
    def _get_site_elements(self)->None:
        """
        read element information from elementInfo.dat
        NOTE: elementInfo.dat SHOULD only contains Four Node Quad u-p Elements
        """
        elelist = []
        QuadUPele = namedtuple('QuadUPele', ('tag','nodes', 'matTag', 'vpermParamtag', 'hpermParamtag'))
        try:
            with open(SlopeAnalysis2D.ELEMENTINFO_PATH, 'r') as f:
                for line in f:
                    line = line.split()
                    eleTag,n1,n2,n3,n4,matTag = [int(point) for point in line]
                    elelist.append(QuadUPele(eleTag,(n1,n2,n3,n4),matTag, None, None))
            self.Elements_ALL = tuple(elelist)
        except FileNotFoundError as e:
            logger.error(f'FileNotFoundError: {e}\nPlease check the file path!')
    
    def define_site_elements(self,
                             thicker_boundary = True,
                             high_perm = True,
                             basic_thick_coef = 100,
                             thicker_coef = 100
                             )->None:
        """
        read element information from elementInfo.dat and define soil elements
        thicker_boundary: bool, default=True, if True, the boundary elements with nodes in
                        (self.eqDOF_nodes_01_list & eqDOF_nodes_02_list)
                        will be thicker
        high_perm: bool, default=True, if True, all elements permibility will be set to 1.0
                    NEED TO update material properties later!
        """
        if not hasattr(self, 'Elements'):
            self.split_nodes_and_elements()
        exist_elements = self.opsElements
        maxtag = max(ele.tag for ele in self.Elements_ALL)
        New_Param_tag = 10 ** len(str(maxtag))  # set a large number for parameter tag
        
        if thicker_boundary:
            self.basic_thick_coef = basic_thick_coef
            self.thicker_coef = thicker_coef
            # only consider the first nodepair in eqDOF_nodes_01_list, consider as soil colomns
            left_boundary = max(self.NodesDict_ALL[node].x for node in self.eqDOF_nodes_01_list_ALL[0].NodeTags)
            right_boundary = min(self.NodesDict_ALL[node].x for node in self.eqDOF_nodes_02_list_ALL[0].NodeTags)
            self._site_boundary = (left_boundary, right_boundary)
        
        elements = list(self.Elements)
        for num, ele in enumerate(self.Elements):
            if ele.tag not in exist_elements:
                # get material properties
                mat_name = self.MAT_TAG_NAME_MAP[ele.matTag]
                ele_thick = self.SOIL_ELE_PROP[mat_name].thick*basic_thick_coef
                bulk = self.SOIL_ELE_PROP[mat_name].bulk
                fmass = self.SOIL_ELE_PROP[mat_name].fmass
                unitWX=self.SOIL_ELE_PROP[mat_name].unitWeightX
                unitWY=self.SOIL_ELE_PROP[mat_name].unitWeightY
                
                if thicker_boundary:
                    ele_nodes_x = [self.NodesDict[node].x for node in ele.nodes]
                    if min(ele_nodes_x) < left_boundary:
                        ele_thick = ele_thick*thicker_coef
                        # logger.trace(f'ele {ele.tag} is thicker!, because min_x={min(ele.nodes)} < {left_boundary}=left_boundary')
                    if max(ele_nodes_x) > right_boundary:
                        ele_thick = ele_thick*thicker_coef
                        # logger.trace(f'ele {ele.tag} is thicker!,max_x={max(ele.nodes)} > {right_boundary}=right_boundary')
                
                if high_perm:
                    vperm = 1.0
                    hperm = 1.0
                else:
                    vperm = self.SOIL_ELE_PROP[mat_name].vperm
                    hperm = self.SOIL_ELE_PROP[mat_name].hperm
                
                # create element
                ops.element('quadUP', ele.tag, *ele.nodes, ele_thick, ele.matTag, bulk, fmass, vperm, hperm, unitWX, unitWY)
                
                # add parameters for vperm and hperm
                vPermtag = New_Param_tag+2*ele.tag
                hPermtag = New_Param_tag+2*ele.tag+1
                ops.parameter(vPermtag, 'element', ele.tag, 'vPerm')
                ops.parameter(hPermtag, 'element', ele.tag, 'hPerm')
                elements[num] = ele._replace(vpermParamtag = vPermtag, hpermParamtag = hPermtag)
            else:
                logger.warning(f'{ele} already exists! Not created!')
        self.Elements = tuple(elements)
        logger.success('Finished creating Site elements...')
        
    def _get_fix_nodes(self)->None:
        """
        read fixed node information from fixedNodeInfo.dat
        """
        fix_Bottom_node_list = []
        fix_Surface_node_list = []
        FixedNode = namedtuple('FixedNode', ('tag', 'FixedDOF'))
        # get undrained surface nodes
        undrained_node_list = [FixedNode(node.tag, [0,0,1]) for node in self.Nodes if node.y >= self.WaterLevel]
        self.UndrainedNodes = tuple(undrained_node_list)
        try:
            with open(SlopeAnalysis2D.FIXNODESINFO_PATH, 'r') as f:
                for line in f:
                    line = line.split()
                    nodetag = int(line[0])
                    fixedDOF = [int(dof) for dof in line[1:]]
                    if fixedDOF == [0,1,0]:
                        fix_Bottom_node_list.append(FixedNode(nodetag, fixedDOF))
                    elif fixedDOF == [0,0,1]:
                        # Only Contain the surface nodes below water level here
                        if self.NodesDict_ALL[nodetag].y < self.WaterLevel:
                            fix_Surface_node_list.append(FixedNode(nodetag, fixedDOF))
                    else:
                        raise ValueError(f'FixedDOF {fixedDOF} not supported!')
            self.FixedNodes_ALL = tuple(fix_Bottom_node_list + fix_Surface_node_list)
            self.FixedBottomNodes_ALL = tuple(fix_Bottom_node_list)
            self.FixedSurfaceNodes_ALL = tuple(fix_Surface_node_list)
        except FileNotFoundError as e:
            logger.error(f'FileNotFoundError: {e}\nPlease check the file path!')
        self.FixedBottomNodes = tuple([fixnode for fixnode in self.FixedBottomNodes_ALL if fixnode.tag in self.NodesDict.keys()])
        self.FixedSurfaceNodes = tuple([fixnode for fixnode in self.FixedSurfaceNodes_ALL if fixnode.tag in self.NodesDict.keys()])
        self.FixedNodes = tuple(list(self.FixedBottomNodes) + list(self.FixedSurfaceNodes))
                
    def fix_bottom_nodes(self)->None:
        """fix bottom nodes with DOF=[0,1,0]"""
        if not hasattr(self, 'FixedBottomNodes'):
            self._get_fix_nodes()
        for node in self.FixedBottomNodes:
            ops.fix(node.tag, *node.FixedDOF)
        logger.success('Site Bottom nodes DOF:2 fixed...')
        
    def fix_surface_nodes(self)->None:
        """fix surface nodes with DOF=[0,0,1]"""
        if not hasattr(self, 'FixedSurfaceNodes'):
            self._get_fix_nodes()
        for node in self.FixedSurfaceNodes:
            ops.fix(node.tag, *node.FixedDOF)
        logger.success('Site Surface nodes fixed--> DOF:3 fixed...')
    
    def undrain_nodes_above_water(self)->None:
        """undrain nodes above water level"""
        if not hasattr(self, 'UndrainedNodes'):
            self._get_fix_nodes()
        for node in self.UndrainedNodes:
            ops.fix(node.tag, *node.FixedDOF)
        logger.success('Site nodes above water level undrained --> DOF:3 fixed...')
    
    def add_nodes(self, nodes:list)->None:
        """
        add nodes to the model
        """
        Nodes = self.Nodes
        exist_nodes = self.opsNodes
        All_nodes = self.Nodes_ALL
        for node in nodes:
            if node not in All_nodes:
                logger.warning(f'{node} not defined in {self.NODEINFO_PATH}! MAKE SURE you Know what you are doing! Adding it...')
                ops.node(node.tag, node.x, node.y)
                self.Nodes_ALL += (node,)
                self.Nodes += (node,)
                logger.info(f'User defined {node} is created!')
                continue
                
            if node.tag not in Nodes and node.tag not in exist_nodes:
                ops.node(node.tag, node.x, node.y)
                self.Nodes += (node,)
                logger.info(f'{node} is created!')
            elif node.tag in Nodes and node.tag not in exist_nodes:
                ops.node(node.tag, node.x, node.y)
                logger.info(f'{node} already built but not found in opensees, created!')
            elif node.tag not in Nodes and node.tag in exist_nodes:
                logger.warning(f'{node} not built but found in opensees, Please Check!')
                raise ValueError(f'{node} not built but found in opensees, Please Check!')
            else:
                logger.warning(f'{node} already exists! Not created!')
    
    def _get_eqDOF_nodes(self)->None:
        """
        read equalDOF node information from EqualDOFnodes_Info.dat
        """
        EqDOFNode = namedtuple('EqDOFNode', ['NodeTags', 'eqDOF'])
        
        def _read_eqDOF_nodes(file_path):
            eqDOF_nodes_list = []
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.split()
                        NodeTags = [int(line[0]), int(line[1])]
                        eqDOF = [int(dof) for dof in line[2:]]
                        eqDOF_nodes_list.append(EqDOFNode(NodeTags, eqDOF))
            except FileNotFoundError as e:
                logger.error(f'FileNotFoundError: {e}\nPlease check the file path!')
            return eqDOF_nodes_list

        def recheck_and_define_missing_nodes(eqDOF_nodes_list):
            qualified_nodes_list = [node for node in eqDOF_nodes_list if any(tag in self.NodesDict.keys() for tag in node.NodeTags)]
            undefined_nodes_list = list(set([nodetag for nodepair in qualified_nodes_list for nodetag in nodepair.NodeTags if nodetag not in self.NodesDict.keys()]))
            nodes_undefined = [self.NodesDict_ALL[nodetag] for nodetag in undefined_nodes_list]
            if len(nodes_undefined)==0:
                # no need to add nodes and check constraints
                return qualified_nodes_list
            
            # add undefined nodes
            logger.warning(f'{nodes_undefined} not defined in this part of the model but Used in EqDOF! Adding it...')
            self.add_nodes(nodes_undefined)
            
            # check constraints
            nodes_to_fix = [fixed_node for fixed_node in self.FixedNodes_ALL if fixed_node.tag in undefined_nodes_list]
            for node in nodes_to_fix:
                ops.fix(node.tag, *node.FixedDOF)
                logger.info(f'{self.NodesDict[node.tag]} missing constraints at DOF:{node.FixedDOF}! Adding it ...')
                
            return qualified_nodes_list
        
        self.eqDOF_nodes_01_list_ALL   = _read_eqDOF_nodes(SlopeAnalysis2D.EQDOF_01_INFO_PATH)
        self.eqDOF_nodes_02_list_ALL   = _read_eqDOF_nodes(SlopeAnalysis2D.EQDOF_02_INFO_PATH)
        self.eqDOF_nodes_Base_list_ALL = _read_eqDOF_nodes(SlopeAnalysis2D.EQDOF_BASE_INFO_PATH)
        
        self.eqDOF_nodes_01_list   = recheck_and_define_missing_nodes(self.eqDOF_nodes_01_list_ALL)
        self.eqDOF_nodes_02_list   = recheck_and_define_missing_nodes(self.eqDOF_nodes_02_list_ALL)
        self.eqDOF_nodes_Base_list = recheck_and_define_missing_nodes(self.eqDOF_nodes_Base_list_ALL)
             
    def equalDOF_for_Site(self)->None:
        """read equalDOF node information from:
            EqualDOFnodes_01_Info.dat
            EqualDOFnodes_02_Info.dat
            EqualDOFnodes_Base_Info.dat
        and then define equalDOF constraints"""
        self._get_eqDOF_nodes()
        for node in self.eqDOF_nodes_01_list:
            ops.equalDOF(*node.NodeTags, *node.eqDOF)
            
        for node in self.eqDOF_nodes_02_list:
            ops.equalDOF(*node.NodeTags, *node.eqDOF)
            
        for node in self.eqDOF_nodes_Base_list:
            ops.equalDOF(*node.NodeTags, *node.eqDOF)
        logger.success('Finished creating equalDOF constraints for site...')
        
    def _get_nodal_mass(self)->None:
        """
        read nodal mass information
        """
        nodal_mass_list = []
        NodalMass = namedtuple('NodalMass', ('NodeTag', 'mass'))
        try:
            with open(SlopeAnalysis2D.MASS_INFO_PATH, 'r') as f:
                for line in f:
                    line = line.split()
                    NodeTag = int(line[0])
                    mass = [float(l) for l in line[1:]]
                    if any(mass)<0:
                        logger.trace(f'Negative mass found in {NodeTag}! ignored!')
                    nodal_mass_list.append(NodalMass(NodeTag, mass))
                self.NodalMass_ALL = tuple(nodal_mass_list)
        except FileNotFoundError as e:
            logger.warning(f'FileNotFoundError: {e}\nPlease check the file path!')
        # only consider the nodes in the model
        self.NodalMass = tuple([node for node in self.NodalMass_ALL if node in self.Nodes])
            
    def define_nodal_mass(self)->None:
        """define nodal mass"""
        if not hasattr(self, 'NodalMass'):
            self._get_nodal_mass()
        for node in self.NodalMass:
            ops.mass(node.NodeTag, *node.mass)
        logger.success('Finished creating nodal mass...')
    
    def add_nodal_mass_gravity(self)->None:
        """add nodal mass for gravity
        """
        if not hasattr(self, 'NodalMass'):
            raise AttributeError('NodalMass not defined!')
        
        if len(ops.getPatterns())<1:
                ops.pattern('Plain', 1, 1)
                logger.warning(f'No Pattern Found! Created a Plain Pattern with tag 1!')
                
        for node in self.NodalMass:
            logger.warning('记得检查，这里多乘了个厚度')
            ops.load(node.NodeTag, *[m*-9.81 for m in node.mass])
        logger.success('Finished adding nodal mass for gravity')
    
    def _get_LK_boundary_property(self)->None:
        """
        calc Lysmer-Kulhemyer boundary property from existing information
        """
        LKDashPot = namedtuple('LKDashPot',['FixedNode','EqDOFNode','LeftCornerNode','Material', 'Element', 'BaseArea','DashpotCoef'])
        
        # get LK dashpot position(x,y) by eqDOF_nodes_01_list ∩ eqDOF_nodes_Base_list, there should be 2 nodes but the one with smaller x is needed
        nodetags01 = [tag for node in self.eqDOF_nodes_01_list_ALL for tag in node.NodeTags]
        nodetagsbase = [tag for node in self.eqDOF_nodes_Base_list_ALL for tag in node.NodeTags]
        common_node_tags  = set(filter(lambda x: x in nodetags01, nodetagsbase))
        common_nodes = [self.NodesDict_ALL[node] for node in common_node_tags]
        left_corner_node = sorted(common_nodes, key=lambda node: node.x)[0]
        x,y = left_corner_node.x, left_corner_node.y
        
        # create LK dashpot nodes
        newtag = max(node.tag for node in self.Nodes_ALL) + 1

        # define fixities for dashpot nodes
        DashPotNode = namedtuple('DashPotNode', ['tag', 'x', 'y', 'FixedDOF', 'EqDOF'])
        fixed_node = DashPotNode(newtag, x, y, FixedDOF = [1,1,1], EqDOF = None)
        eqdof_node = DashPotNode(newtag+1, x, y, FixedDOF = [0,1,1], EqDOF = [1])

        # define dashpot material parameters
        # dashpotcoef = rou*vs, rou is the density(ton/m^3) of the soil below the site, vs is the shear wave velocity(m/s)
        rou = 2.00
        vs = 875.0
        dashpotcoef = rou*vs
        
        # baseArea = sum of the area of the soil length*soil thickness
        max_x = max(self.NodesDict[node].x for node in self.eqDOF_nodes_Base_list[0].NodeTags)
        min_x = min(self.NodesDict[node].x for node in self.eqDOF_nodes_Base_list[0].NodeTags)
        base_thick = self.SOIL_ELE_PROP['sandy gravel'].thick*self.basic_thick_coef
        if not hasattr(self, '_site_boundary'):
            baseArea = (max_x-min_x)*base_thick
        else:
            baseArea = (self._site_boundary[1]-self._site_boundary[0])*base_thick\
                        +(max_x-self._site_boundary[1])*base_thick*self.thicker_coef\
                        +(self._site_boundary[0]-min_x)*base_thick*self.thicker_coef
                        
        # define dashpot material
        new_material_tag = max(self.SOIL_MAT_PROP.values(), key=lambda x:x.matTag).matTag + 1
        LK_material = self.uniaxialMaterial('Viscous', new_material_tag, [dashpotcoef*baseArea, 1], 'LK_Dashpot Vicious Material')

        # create LK dashpot element
        Viciousele = namedtuple('Viciousele', ['tag', 'nodes', 'matTag'])
        new_ele_tag = max(self.opsElements) + 1
        LKele = Viciousele(new_ele_tag, [fixed_node.tag, eqdof_node.tag], LK_material.matTag)
        self.LKDashPot = LKDashPot(fixed_node, eqdof_node, left_corner_node, LK_material, LKele, baseArea, dashpotcoef)
        
    def define_LK_boundary(self)->None:
        """define Lysmer-Kulhemyer boundary"""
        if not hasattr(self, 'LKDashPot'):
            self._get_LK_boundary_property()
            
        fixed_node = self.LKDashPot.FixedNode
        eqdof_node = self.LKDashPot.EqDOFNode
        left_corner_node = self.LKDashPot.LeftCornerNode
        
        # define dashpot nodes
        self.add_nodes([fixed_node, eqdof_node])

        # define boundary conditions for dashpot nodes
        ops.fix(fixed_node.tag, *fixed_node.FixedDOF)
        ops.fix(eqdof_node.tag, *eqdof_node.FixedDOF)
        ops.equalDOF(left_corner_node.tag, eqdof_node.tag, *eqdof_node.EqDOF)
        logger.info(f'left_corner_node:{left_corner_node.tag} to eqdof_node:{eqdof_node.tag} with DOF:{eqdof_node.EqDOF}')
        logger.info(f'LK dashpot nodes(tag={fixed_node.tag, eqdof_node.tag}) & boundary defined!')
        
        # define dashpot material
        material = self.LKDashPot.Material
        ops.uniaxialMaterial(material.Type, material.matTag, *material.matArgs)
        # define dashpot element
        element = self.LKDashPot.Element
        ops.element('zeroLength', element.tag, *element.nodes, '-mat', element.matTag, '-dir', 1)
        logger.info(f'LK dashpot material(tag={element.matTag}) & element(tag={element.tag}) defined!')
        logger.success('Finished creating Lysmer-Kulhemyer dashpot boundary...')
    
    def check_matrix_dof(self, dof_to_check:int)->namedtuple:
        """
        check matrix DOF
        """
        for nodeTag in self.opsNodes:
            if dof_to_check in ops.nodeDOFs(nodeTag):
                return self.NODE2(nodeTag, *ops.nodeCoord(nodeTag))
        return None
    
    def update_material(self, stage = 'elastic')->None:
        """
        update material properties for all elements
        """
        if stage == 'elastic':
            for material in self.SOIL_MAT_PROP.values():
                ops.updateMaterialStage('-material', material.matTag, '-stage', 0)
        elif stage == 'plastic':
            for material in self.SOIL_MAT_PROP.values():
                ops.updateMaterialStage('-material', material.matTag, '-stage', 1)

    def update_permibility(self)->None:
        """
        update permibility for all elements
        """
        for ele in self.Elements:
            mat_name = self.MAT_TAG_NAME_MAP[ele.matTag]
            vperm = self.SOIL_ELE_PROP[mat_name].vperm
            hperm = self.SOIL_ELE_PROP[mat_name].hperm
            ops.updateParameter(ele.vpermParamtag, vperm)
            ops.updateParameter(ele.hpermParamtag, hperm)
        logger.success('Updated permibility for all elements...')

    def fix_side_nodes(self, side, pos_tol = 1e-1)->tuple[int]:
        """
        fix side nodes with DOF=[1,0,0]
        side: str, default: 'both', or 'left' or 'right'
        pos_tol: float, default=1e-2, x position tolerance for fixing nodes
        """
        fixed_nodes = []
        nodes = []
        if side == 'both':
            self.fix_side_nodes('left', pos_tol)
            self.fix_side_nodes('right', pos_tol)
        elif side == 'left':
            nodes = self.eqDOF_nodes_01_list
            x_target = min(self.NodesDict[node].x for node in nodes[0].NodeTags)
        elif side == 'right':
            nodes = self.eqDOF_nodes_02_list
            x_target = max(self.NodesDict[node].x for node in nodes[0].NodeTags)
        else:
            raise ValueError('Must Specify Side!')
        
        for node in nodes:
            try:
                node_tag = [n for n in node.NodeTags if (self.NodesDict[n].x-x_target) < pos_tol][0]
            except IndexError:
                n1x = self.NodesDict[node.NodeTags[0]].x  
                n2x = self.NodesDict[node.NodeTags[1]].x
                logger.error(f'No Node\'s x position:[{n1x},{n2x}] falls in boundary:[{x_target-pos_tol},{x_target+pos_tol}]! Please Check pos_tol!')
            fixeddofs = ops.getFixedDOFs(node_tag)  # get fixed DOFs, if exists, return [1,2,3], none return []
            if 1 not in fixeddofs:
                ops.fix(node_tag, *[1,0,0])
                fixed_nodes.append(node_tag)

        # return fixed_nodes
        if side == 'left':
            self.FixedLeftNodes = tuple(fixed_nodes)
        elif side == 'right':
            self.FixedRightNodes = tuple(fixed_nodes)

    # def unfix_side_nodes(self, side)->None:
    #     """
    #     unfix side nodes with DOF=[1,0,0]
    #     side: str, default: 'both', or 'left' or 'right'
    #     """
    #     nodes = []
    #     if side == 'both':
    #         self.unfix_side_nodes('left')
    #         self.unfix_side_nodes('right')
    #         return None
    #     elif side == 'left':
    #         nodes = self.FixedLeftNodes
    #     elif side == 'right':
    #         nodes = self.FixedRightNodes
    #     else:
    #         raise ValueError('Must Specify Side!')
        
    #     self._unfix_nodes(nodes, dof = 1)
    #     logger.success(f'Finished unfixing {side} side nodes...')
        
    # def _unfix_nodes(self, nodes:tuple[int], dof = None)->None:
    #     """
    #     unfix nodes with specified DOF
    #     """
    #     for node in nodes:
    #         fixeddofs = ops.getFixedDOFs(node)  # get fixed DOFs, if exists, return [1,2,3], none return []
    #         if dof in fixeddofs:
    #             ops.remove('sp', node, dof)
    #             logger.trace(f'Node {node} DOF:{dof} unfixed!')

    # def replace_support_reaction(self)->None:
    #     """
    #     replace support reaction for side nodes in Side_Support_Reaction

    #     """
    #     for node, reaction in self.Side_Support_Reaction.items():
    #         ops.load(node, reaction['Reaction'],0,0)
    #         logger.trace(f'Node {node} reaction replaced with {reaction["Reaction"]}!')

    # def record_side_nodes_force(self, side = 'both', dof = 1)->dict:
    #     """
    #     record nodes force of one side
    #     side: str, default: 'both', or 'left' or 'right'
    #     dof: int, default: 1, or 2,3
    #     """
    #     side_node_force = dict()
    #     if side == 'both':
    #         self.Side_Support_Reaction = {
    #             **self.record_side_nodes_force('left'),
    #             **self.record_side_nodes_force('right')
    #             }
    #         return self.Side_Support_Reaction
    #     elif side == 'left':
    #         nodes = self.FixedLeftNodes
    #     elif side == 'right':
    #         nodes = self.FixedRightNodes
    #     else:
    #         raise ValueError('Must Specify Side!')
        
    #     for node in nodes:
    #         side_node_force[node] = {'Side':side,'Reaction':ops.nodeReaction(node, dof)}
    #     return side_node_force

    def site_gravity_analysis(self, plot_disp = False, save = False)->None:
        """
        site gravity analysis
        """
        # gravity analysis settings
        ops.constraints('Penalty', 1.e18, 1.e18)
        ops.test('RelativeNormDispIncr', 1e-4, 35, 1)
        ops.algorithm('Newton')
        ops.integrator('Newmark', 0.5, 0.25)
        
        if self.Parallel:
            ops.numberer('ParallelRCM')
            ops.system('Mumps')
        else:
            ops.numberer('RCM')
            ops.system('ProfileSPD')
            
        ops.analysis('Transient')
        ops.reactions('-dynamic')
    
        # elastic gravity analysis
        self.update_material(stage='elastic')
        startT = time.time()
        if plot_disp:
            logger.info('Recording displacement data for Visualization...')
            ModelData = opst.GetFEMdata(results_dir="opstool_output")
            ModelData.get_model_data(save_file="ModelData.hdf5")
            ops.analyze(10, 5.0e2)
            ModelData.get_resp_step()
            ops.analyze(10, 5.0e3)
            ModelData.get_resp_step()
        else:     
            ops.analyze(10, 5.0e2)
            ops.analyze(10, 5.0e3)
        logger.info(f'Finished with elastic gravity analysis. Time used:{time.time()-startT:.2f}s')
        
        # nodalFy = [ops.nodeUnbalance(node.tag,2) for node in self.FixedSurfaceNodes_ALL].sort()
        if not self.Parallel:
            for node in self.FixedSurfaceNodes_ALL:
                logger.info(f'Node {node.tag} nodereaction Fy:{ops.nodeReaction(node.tag)}')
        # print(nodalFy[:10])
        
        # plastic gravity analysis
        self.update_material(stage='plastic')
        ops.test('RelativeNormDispIncr', 1e-4, 50, 1)
        
        startT1 = time.time()
        if plot_disp:
            ops.analyze(10, 5.0e-3)
            ModelData.get_resp_step()
        else:      
            ops.analyze(10, 5.0e-3)
        logger.info(f'Finished with plastic gravity analysis. Time used:{time.time()-startT1:.2f}s')
        
        if plot_disp:
            ModelData.save_resp_all(save_file="RespStepData-Gravity.hdf5")
            opsvis = opst.OpsVisPlotly(point_size=2, line_width=3, colors_dict=None, theme="plotly",
                           color_map="jet", results_dir="opstool_output")
            fig = opsvis.deform_vis(input_file="RespStepData-Gravity.hdf5",
                  slider=True,
                  response="disp", alpha=1.0,
                  show_outline=False, show_origin=True,
                  show_face_line=False, opacity=1,
                  model_update=False)
            fig.show()
            if save:
                fig.write_html('Gravity_Deformation_Animation.html', auto_open = False)
                logger.success('Animation file saved at Gravity_Deformation_Animation.html')
        logger.success(f'Finished site gravity analysis')
        
    def set_velocity_record(self, tsTag: int, path:str = 'velocityHistory.txt', dt: float = 0.01)->int:
        """

        Args:
            path (str): velocity time history file path
        """
        # define velocity time history file
        # NOTICE: the file path should be relative to the working directory
        full_path = SlopeAnalysis2D.DATA_PATH.relative_to(SlopeAnalysis2D.ABS_PATH) / path
        if not full_path.exists():
            raise FileNotFoundError(f'FileNotFoundError: {full_path} not found!')
        # timeseries object for force history
        cfactor = self.LKDashPot.BaseArea*self.LKDashPot.DashpotCoef
        ops.timeSeries('Path', tsTag,'-dt', dt,'-filePath',str(full_path),'-factor',cfactor)
        return tsTag
    
    def create_recorders(self):
        # record nodal displacment, acceleration, and porepressure
        ops.recorder('Node', '-file', 'displacement.out', '-time', '-dT', 0.01, '-node', *self.opsNodes, '-dof', 1, 2, 'disp')
        ops.recorder('Node', '-file', 'acceleration.out', '-time', '-dT', 0.01, '-node', *self.opsNodes, '-dof', 1, 2, 'accel')
        ops.recorder('Node', '-file', 'porePressure.out', '-time', '-dT', 0.01, '-node', *self.opsNodes, '-dof', 3, 'vel')
        # record elemental stress and strain
        maxelenum = max([ele.tag for ele in self.Elements_ALL])
        ops.recorder('Element', '-file', 'stress1.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 1, 'stress')
        ops.recorder('Element', '-file', 'stress2.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 2, 'stress')
        ops.recorder('Element', '-file', 'stress3.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 3, 'stress')
        ops.recorder('Element', '-file', 'stress4.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 4, 'stress')
        ops.recorder('Element', '-file', 'strain1.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 1, 'strain')
        ops.recorder('Element', '-file', 'strain2.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 2, 'strain')
        ops.recorder('Element', '-file', 'strain3.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 3, 'strain')
        ops.recorder('Element', '-file', 'strain4.out', '-time', '-dT', 0.01, '-eleRange', 1, maxelenum, 'material', 4, 'strain')
        logger.success('Finished creating all recorders...')
    
    def _get_NP_split_boundary(self)->tuple[float,float]:
        """
        get min and max x coordinates for spliting nodes into ops.NP parts
        return: left and right boundary for the ops.PID part
        """
        def x_at_percentage(x_coord_count:dict, percentage:float)->float:
            if percentage == 0.0:
                return min(x_coord_count.keys())
            if percentage == 1.0:
                return max(x_coord_count.keys())

            total = sum(x_coord_count.values())
            cumsum = 0.
            x0 = min(x_coord_count.keys())
            for x, count in x_coord_count.items():
                cumsumnew = cumsum + count/total
                if cumsumnew >= percentage:
                    if abs(cumsumnew - percentage) <= abs(cumsum - percentage):
                        return x
                    else:
                        return x0
                cumsum = cumsumnew
                x0 = x
        
        left_percentage = float(self.PID)/float(self.NP)
        right_percentage = float(self.PID+1)/float(self.NP)
        x_coord_count = Counter([node.x for node in self.Nodes_ALL]).items()
        x_coord_count = dict(sorted(x_coord_count))
        left_boundary = x_at_percentage(x_coord_count, left_percentage)
        right_boundary = x_at_percentage(x_coord_count, right_percentage)
        return left_boundary, right_boundary
        
    def split_nodes_and_elements(self)->list[float,float]:
        """
        split nodes into ops.NP parts with only a line of common nodes(in x direction)
        return: boundary x coordinates:list[float,float]
                self.Nodes defines all nodes satisfying the boundary condition
        """
        if not hasattr(self, 'Nodes_ALL'):
            self._get_site_nodes()
        if not hasattr(self,'Elements_ALL'):
            self._get_site_elements()
        # split x coordinates into ops.NP parts and get boundary for this split
        xmin,xmax = self._get_NP_split_boundary()
        # return if not parallel
        if not self.Parallel:
            self.Nodes = self.Nodes_ALL
            self.Elements = self.Elements_ALL
            return xmin, xmax
        
        # get nodes in the boundary
        nodes = [node for node in self.Nodes_ALL if xmin<=node.x<=xmax]
        nodetags = [node.tag for node in nodes]
        # add nodes not in the boundary but in the common elements
        elements = []
        for ele in self.Elements_ALL:
            is_quadup = type(ele).__name__ == 'QuadUPele'
            node_in_boundary:list[int] = [node for node in ele.nodes if node in nodetags]
            if len(node_in_boundary)<=1:
                # element not in the boundary, do nothing
                continue
            elif len(node_in_boundary) == 4 and is_quadup:
                # element in the boundary, no node to add
                elements.append(ele)
            elif len(node_in_boundary) in [2,3] and is_quadup:
                # element in the boundary, add one node
                missing_nodes = [self.NodesDict_ALL[nodetag] for nodetag in ele.nodes if nodetag not in node_in_boundary]
                for node in missing_nodes:
                    nodes.append(node)
                elements.append(ele)
            else:
                logger.warning(f'Element:{ele} has {len(node_in_boundary)} nodes in the boundary, not supported!')
                raise ValueError('Element type not supported!')
        # add qualified nodes/elements to self and remove suplicate nodes/elements
        self.Nodes = tuple(set(nodes))
        self.Elements = tuple(set(elements))
        return xmin, xmax
          
    def __init_parallel_parameters(self):
        """
        init parallel parameters
        """
        self.PID = ops.getPID()
        self.NP = ops.getNP()
        if self.NP>1:
            self.Parallel = True
        else:
            self.Parallel = False
        
        if self.NP>1:
            self.split_nodes_and_elements()
    
    def __init__(self, WaterLevel=0.0):
        """
        Build the model for SlopeAnalysis2D Example at https://opensees.berkeley.edu/wiki/index.php?title=Dynamic_2D_Effective_Stress_Analysis_of_Slope
        I've Changed the model element from nine_four_node_quadUP to four_node_quadUP
        Tested in Openseespy(version:3.6.0.3) for Windows and Linux(Parallel part only works in Linux, I used WSL2)
        Test Computer: Windows 11, 32GB RAM, Intel(R) Core(TM) i5-13600K CPU @ 3.40GHz
        Speed:1 Core: 509.120s, 2 Cores: 207.437s, 3 Cores: 170.449s, 4 Cores: 157.543s, 5 Cores or more: Unconverged
        """
        self.__init_properties(WaterLevel)
        self.__init_parallel_parameters()
        
        ops.wipe()
        ops.model('BasicBuilder', '-ndm', 2, '-ndf', 3)
        
        self.define_site_nodes()

        self.fix_bottom_nodes()
        self.fix_surface_nodes()
        self.undrain_nodes_above_water()

        self.equalDOF_for_Site()
        
        self.define_soil_materials()
        
        self.define_site_elements(
            thicker_boundary = True,
            high_perm = True,
            basic_thick_coef = 1,
            thicker_coef = 10000
            )
        
        self.define_nodal_mass()
        
        ops.timeSeries('Constant', 1)
        ops.pattern('Plain', 1, 1)
        self.add_nodal_mass_gravity()
        
        self.define_LK_boundary()
        
        # Auto Partition, not recommended
        # if self.Parallel:
        #     ops.partition('-info')
        
        # gravity analysis
        logger.info('Start Gravity Analysis...')

        self.site_gravity_analysis(plot_disp=False, save=False)
        
        self.update_permibility()
        
        ops.setTime(0.0)
        ops.loadConst('-time',0)
        ops.remove('recorders')
        logger.success('Finished building the model for SlopeAnalysis2D!')
        
        
        
    
if __name__ == "__main__":
    Slope2D = SlopeAnalysis2D(WaterLevel = -6.0)
    
    # print some information if you like
    # print(Slope2D.Nodes[:5])
    # print(Slope2D.Elements[:5])
    # print(Slope2D.PDMY._fields)
    # print(Slope2D.SOIL_MAT_PROP["silt1"])
    # print(Slope2D.FixedNodes[:5])
    
    
    # Plot Model if you like
    # if not Slope2D.Parallel:  
    #     ModelData = opst.GetFEMdata(results_dir="opstool_output")
    #     ModelData.get_model_data(save_file="ModelData.hdf5")
    #     opsvis = opst.OpsVisPlotly(point_size=2, line_width=3, colors_dict=None, theme="plotly",
    #                         color_map="jet", results_dir="opstool_output")
    #     fig = opsvis.model_vis(input_file="ModelData.hdf5",
    #                 show_node_label=True,
    #                 show_ele_label=False,
    #                 show_local_crd=False,
    #                 show_fix_node=True,
    #                 show_constrain_dof=False,
    #                 label_size=8,
    #                 show_outline=True,
    #                 opacity=1.0,
    #                 save_html="ModelVis.html")
    #     fig.show()
    
    logger.info('Start Dynamic Analysis...')
    velSeriesTag = Slope2D.set_velocity_record(tsTag = 100, path='velocityHistory.txt', dt = 0.005)
    logger.success(f'Velocity Time History (tag:{velSeriesTag}) Loaded!')
    
    dir=1
    patternTag = 400
    ops.pattern('UniformExcitation', patternTag, dir, '-vel', velSeriesTag)
    logger.success(f'UniformExcitation Pattern (tag:{patternTag}) Loaded!')
    
    # set damping
    damp = 0.2
    w1 = 2*3.1415926535*0.2
    w2 = 2*3.1415926535*20
    a0 = 2*damp*w1*w2/(w1+w2)
    a1 = 2*damp/(w1+w2)
    ops.rayleigh(a0,a1,0,0)
    
    nstep = 5000
    dt = 0.005
    tFinal = nstep*dt

    if Slope2D.Parallel:
        Slope2D.create_recorders()
    else:
        # opstool can't run in parallel
        ModelData = opst.GetFEMdata(results_dir="opstool_output")
        ModelData.get_model_data(save_file="ModelData.hdf5")
    
    # algorithm settings 10:Newton 20:NewtonLineSearch 30:ModifiedNewton 40:KrylovNewton 70:Broyden
    analysis = opst.SmartAnalyze(analysis_type="Transient",
                                 testType = 'RelativeNormDispIncr',
                                 algoTypes=[10,20,30,40,70],
                                 printPer = 100 if Slope2D.PID==0 else nstep,
                                 tryLooseTestTol = True,
                                 looseTestTolTo = 1e-4,
                                 tryAlterAlgoTypes = True,
                                 )
    segs = analysis.transient_split(nstep)
    ops.constraints('Penalty', 1.e20, 1.e20)
    ops.test('RelativeNormDispIncr', 1e-4, 35, 0)
    ops.algorithm('Newton')
    
    if Slope2D.Parallel:
        ops.numberer('ParallelRCM')
        ops.system('Mumps')
    else:
        ops.numberer('RCM')
        ops.system('ProfileSPD')
    
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')
    
    # Dynamic Analysis
    if Slope2D.PID==0:
        with alive_bar(nstep,title="NLTHA:",length=30,bar='notes') as bar:
            for seg in segs:
                ok = analysis.TransientAnalyze(dt)
                # save response data per 100 steps
                if seg%100==0 and not Slope2D.Parallel:
                    ModelData.get_resp_step()
                bar()
    else:
        for seg in segs:
            ok = analysis.TransientAnalyze(dt)
            if seg%100==0:
                    ModelData.get_resp_step()
    
    # save response data and plot if you like
    if not Slope2D.Parallel:     
        ModelData.save_resp_all(save_file="RespStepData-Dynamic.hdf5")
    
        opsvis = opst.OpsVisPlotly(point_size=2, line_width=3, colors_dict=None, theme="plotly",
                        color_map="jet", results_dir="opstool_output")
        fig = opsvis.deform_vis(input_file="RespStepData-Dynamic.hdf5",
                                slider=True,
                                response="disp", alpha=1.0,
                                show_outline=False, show_origin=True,
                                show_face_line=False, opacity=1,
                                model_update=False,
                                save_html="DeformVis.html")
        fig.show()
        # fig = opsvis.react_vis(input_file="RespStepData-Dynamic.hdf5",
        #                         slider=True,
        #                         direction="Fy",
        #                         show_values = True,
        #                         show_outline = False,
        #                         save_html = "ReactVis.html")
        # fig.show()

    
    