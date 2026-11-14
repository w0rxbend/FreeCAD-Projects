"""HD camera mount: the engine's camera mount sized for a 20 mm digital camera (the common width of the
HD cameras of the digital systems). It replaces the 19 mm mount, which stays as a variant."""

from zhalo import equipment as E
from zhalo.accessories import camera_mount

HD = E.Camera("HD 20 mm", 20.0, 6.0, 9.0, 16.0, 10.0, 2.0)


def build():
    acc = camera_mount._accessory(HD, "hd20", True)
    acc.title = "HD camera mount, 20 mm"
    acc.color = "accent"
    return [acc, camera_mount._accessory(E.CAM_MICRO, "19", False), camera_mount._accessory(E.CAM_MINI, "22", False)]
