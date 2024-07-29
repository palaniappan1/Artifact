from enum import Enum


class CallgraphAlgorithm(Enum):
    CHA = "CHA"
    VTA = "VTA"
    RTA = "RTA"
    SPARK = "SPARK"
    QILIN = "QILIN"


class NonConfigurablePTA(Enum):
    insens = "insens"
    B_2o = "B-2o"
    D_2o = "D-2o"
    D_2c = "D-2c"


class ConfigurablePTA(Enum):
    kc = "kc"
    ko = "ko"
    kt = "kt"
    kh = "kh"
    kht = "kht"
    M_ko = "M-ko"
    M_kc = "M-kc"
    E_ko = "E-ko"
    T_ko = "T-ko"
    Z_ko = "Z-ko"
    Z_kc = "Z-kc"
    s_kc = "s-kc"
