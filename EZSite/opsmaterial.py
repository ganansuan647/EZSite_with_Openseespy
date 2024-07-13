from collections import namedtuple
import openseespy.opensees as ops
from loguru import logger

class ShouldNotInstantiateError(Exception):
    pass

class EZOpsMaterial:
    def __init__(self):
        logger.error('EZOpsMaterial is a abstract class!Should not be instantiated!')
        raise ShouldNotInstantiateError('Abstract class EZOpsMaterial accidentally instantiated!')
    
    @property
    @staticmethod
    def PIMY(self)-> namedtuple:
        """
        PressureIndependMultiYield namedtuple Parameters:
            name: str, material name
            matTag: int, material tag
            nd: int(2 or 3), number of dimensions
            rho: float(ton/m^3), Saturated soil mass density,default=1.9
            ShearModul(Gr): float(kPa),default=7.5e4
            BulkModul(Br): float(kPa),default=2.0e5
            cohesion: float(kPa),default=37.0
            peakShearStrain: float, default=0.1
            frictionAng: float(deg),default=0.0
            refPress: float(kPa), default=100.0
            pressDependCoef: float, default=0.0
            noYieldSurf:Number of yield surfaces,must be less than 40, default is 20
            note:str
        """
        PIMY = namedtuple(
            'PIMY',
            ['SoilType', 'matTag',
            'nd', 'rho', 'ShearModul', 'BulkModul', 'cohesion',
            'peakShearStrain', 'frictionAng', 'refPress', 
            'pressDependCoef', 'noYieldSurf','note'],
            defaults=['PressureIndependMultiYield', 0,
            2, 1.9, 75000.0, 200000.0, 37.0,
            0.1, 0.0, 100.0,
            0.0, 20, None]
        )
        return PIMY

    @property
    @staticmethod
    def PDMY(self)-> namedtuple:
        """"
        namedtuple Parameters:
            name: str, material name
            matTag: int, material tag
            nd: int(2 or 3), number of dimensions
            rho: float(ton/m^3), Saturated soil mass density,default=1.9
            ShearModul(Gr): float(kPa),default=7.5e4
            BulkModul(Br): float(kPa),default=2.0e5
            frictionAng: float(deg),default=33
            peakShearStrain: float, default=0.1
            refPress: float(kPa), default=80.0
            pressDependCoef: float, default=0.5
            PTAng(φPT): float(deg), Phase transformation angle, default=27.0
            contrac: float,剪缩系数,default=0.07
            dilat1,dilat2: float,剪胀系数
            Liq1(kPa),Liq2,Liq3:液化系数default=10,0.01,1,Liq1代表有效围压的阈值,小于该值起作用,Liq2、Liq3 代表循环流动过程中塑性剪应变的累积
            noYieldSurf:Number of yield surfaces,must be less than 40, default is 20
            e: float, initial void ratio,default=0.6
            cs1,cs2,cs3: float, default=0.9,0.02,0.7
            pa: float, atmospheric pressure, default=101
            note:str
        """
        PDMY = namedtuple(
            'PDMY',
            ['SoilType', 'matTag',
            'nd', 'rho', 'ShearModul', 'BulkModul', 'frictionAng',
            'peakShearStrain', 'refPress', 'pressDependCoef', 'PTAng',
            'contrac', 'dilat1', 'dilat2',
            'Liq1', 'Liq2', 'Liq3', 'noYieldSurf', 'e',
            'cs1', 'cs2', 'cs3', 'pa', 'note'],
            defaults=['PressureDependMultiYield', 0,
            2, 1.9, 75000.0, 200000.0, 33,
            0.1, 80.0, 0.0, 27.0,
            0.07, 0.4, 2.0,
            10.0, 0.01, 1.0, 20, 0.6,
            0.9, 0.02, 0.7, 101.0, None]
            )
        return PDMY

    @property
    @staticmethod
    def PDMY02(self)-> namedtuple:
        """"
        namedtuple Parameters:
            name: str, material name
            matTag: int, material tag
            nd: int(2 or 3), number of dimensions
            rho: float(ton/m^3), Saturated soil mass density,default=1.9
            ShearModul(Gr): float(kPa),default=7.5e4
            BulkModul(Br): float(kPa),default=2.0e5
            frictionAng: float(deg),default=33
            peakShearStrain: float, default=0.1
            refPress: float(kPa), default=80.0
            pressDependCoef: float, default=0.5
            PTAng(φPT): float(deg), Phase transformation angle, default=27.0
            contrac1,contrac3(NEW! for Kσ effect): float,剪缩系数,default=0.045,0.15
            dilat1,dilat3(NEW! for Kσ effect): float,剪胀系数,default=0.06,0.15
            noYieldSurf:Number of yield surfaces,must be less than 40, default is 20
            contrac2,dilat2(NEW! for dilation history): float，default=5.0,3.0
            Liq1(kPa),Liq2:default=1.0,0.0,Redefined and different from PressureDependMultiYield material
            e: float, initial void ratio,default=0.6
            cs1,cs2,cs3: float, default=0.9,0.02,0.7
            pa: float, atmospheric pressure, default=101
            note:str
        """
        PDMY02 = namedtuple(
            'PDMY02',
            ['SoilType', 'matTag',
            'nd', 'rho', 'ShearModul', 'BulkModul', 'frictionAng',
            'peakShearStrain', 'refPress', 'pressDependCoef', 'PTAng',
            'contrac1','contrac3', 'dilat1','dilat3',
            'noYieldSurf','contrac2','dilat2',
            'Liq1', 'Liq2', 'e',
            'cs1', 'cs2', 'cs3', 'pa', 'note'],
            defaults=['PressureDependMultiYield02 ', 0,
            2, 1.9, 75000.0, 200000.0, 33,
            0.1, 80.0, 0.5, 27.0,
            0.045, 0.15, 0.06, 0.15,
            20, 5.0, 3.0,
            1.0, 0.0, 0.6,
            0.9, 0.02, 0.7, 101.0, None]
            )
        return PDMY02

    @property
    @staticmethod
    def NODE2(self)-> namedtuple:
        """
        2D Node namedtuple Parameters:
            tag: int, node tag
            x: float, x coordinate
            y: float, y coordinate
        """
        Node = namedtuple('Node', ['tag', 'x', 'y'], defaults=[0, 0.0, 0.0])
        return Node
    
    @property
    @staticmethod
    def NODE3(self)-> namedtuple:
        """
        3D Node namedtuple Parameters:
            tag: int, node tag
            x: float, x coordinate
            y: float, y coordinate
            z: float, z coordinate
        """
        Node = namedtuple('Node', ['tag', 'x', 'y', 'z'], defaults=[0, 0.0, 0.0, 0.0])
        return Node

    @property
    @staticmethod
    def uniaxialMaterial(self)-> namedtuple:
        """
        uniaxialMaterial namedtuple Parameters:
            Type: str, material type
            matTag: int, material tag
            matArgs: list, material arguments
            note: str
        """
        uniaxialMaterial = namedtuple('uniaxialMaterial', ['Type', 'matTag', 'matArgs', 'note'])
        return uniaxialMaterial

    @staticmethod
    def define_PressureDependMultiYield(SoilProp:namedtuple)->None:
        """
        define PressureDependMultiYield Material in openseespy
        """
        ops.nDMaterial('PressureDependMultiYield', SoilProp.matTag, SoilProp.nd, SoilProp.rho, SoilProp.ShearModul, SoilProp.BulkModul, SoilProp.frictionAng, SoilProp.peakShearStrain, SoilProp.refPress, SoilProp.pressDependCoef, SoilProp.PTAng, SoilProp.contrac, SoilProp.dilat1, SoilProp.dilat2, SoilProp.Liq1, SoilProp.Liq2, SoilProp.Liq3, SoilProp.noYieldSurf, SoilProp.e, SoilProp.cs1, SoilProp.cs2, SoilProp.cs3, SoilProp.pa)

    @staticmethod
    def define_PressureDependMultiYield02(SoilProp:namedtuple)->None:
        """
        define PressureDependMultiYield02 Material in openseespy
        """
        ops.nDMaterial('PressureDependMultiYield02', SoilProp.matTag, SoilProp.nd, SoilProp.rho, SoilProp.ShearModul, SoilProp.BulkModul, SoilProp.frictionAng, SoilProp.peakShearStrain, SoilProp.refPress, SoilProp.pressDependCoef, SoilProp.PTAng, SoilProp.contrac1, SoilProp.contrac3, SoilProp.dilat1, SoilProp.dilat3, SoilProp.noYieldSurf, SoilProp.contrac2, SoilProp.dilat2, SoilProp.Liq1, SoilProp.Liq2, SoilProp.e, SoilProp.cs1, SoilProp.cs2, SoilProp.cs3, SoilProp.pa)

    @staticmethod
    def define_PressureDependMultiYield03(SoilProp:namedtuple)->None:
        """
        define PressureDependMultiYield03 Material in openseespy
        """
        raise NotImplementedError
    
    @staticmethod
    def define_PressureIndependMultiYield(SoilProp:namedtuple)->None:
        """
        define PressureIndependMultiYield Material in openseespy
        """
        ops.nDMaterial('PressureIndependMultiYield', SoilProp.matTag, SoilProp.nd, SoilProp.rho, SoilProp.ShearModul, SoilProp.BulkModul, SoilProp.cohesion, SoilProp.peakShearStrain, SoilProp.frictionAng, SoilProp.refPress, SoilProp.pressDependCoef, SoilProp.noYieldSurf)

    @property
    def opsNodes(self)-> list[int]:
        return ops.getNodeTags()
    
    @property
    def opsElements(self)-> list[int]:
        return ops.getEleTags()